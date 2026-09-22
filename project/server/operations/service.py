"""영업 본문을 노출하지 않는 운영 관리와 변경 감사."""
import uuid
from datetime import timedelta
import httpx
from sqlalchemy import select,func,or_
from server.core.config import get_settings
from server.core.db import utcnow,as_utc
from server.core.errors import ApiError
from server.core.security import hash_password
from server.core.serialization import fields,scalar
from server.accounts.models import Account,AuthSession
from server.stores.models import Region,Store,Category,StoreOwnerMapping,OFCStoreMapping
from server.stores.service import store_dto,region_dto,category_dto
from server.operations.models import AuditEvent,ServiceStatus,Announcement
from server.analysis_jobs.models import AnalysisJob,AnalysisAttempt


def lock_row(db,model,target_id):
    row=db.scalar(select(model).where(model.id==target_id).with_for_update().execution_options(populate_existing=True))
    if not row:raise ApiError(404,'NOT_FOUND','대상을 찾을 수 없습니다.')
    return row


def active_mappings(db,account):
    model=StoreOwnerMapping if account.role=='store_owner' else OFCStoreMapping if account.role=='ofc' else None
    return list(db.scalars(select(model).where(model.account_id==account.id,model.ended_at.is_(None)))) if model else []


def operator_account(db,account):
    dto=fields(account,['id','login_id','display_name','role','region_id','is_active','version','created_at','updated_at'])
    maps=active_mappings(db,account);dto['store_ids']=[str(row.store_id) for row in maps]
    missing=account.role in ('store_owner','ofc') and not maps
    invalid=account.role in ('ofc','regional') and account.region_id is None
    if account.role=='ofc':invalid=invalid or any(db.get(Store,row.store_id).region_id!=account.region_id for row in maps)
    dto['mapping_status']='invalid' if invalid else 'missing' if missing else 'ready'
    return dto


def audit(db,actor,action,target_type,row,reason,before,after,request_id):
    allowed={'id','login_id','display_name','role','region_id','is_active','version','store_ids','code','name','store_type','title','severity','starts_at','ends_at','ended_mapping_ids','status','current_attempt_id'}
    clean=lambda value:{key:scalar(item) for key,item in value.items() if key in allowed}
    db.add(AuditEvent(actor_id=actor.id,action=action,target_type=target_type,target_id=row.id,reason=reason,before_data=clean(before),after_data=clean(after),outcome='succeeded',request_id=uuid.UUID(str(request_id))))


def impact(db,account=None,ended=None,stores=None,blocked=False):
    count=db.scalar(select(func.count()).select_from(AuthSession).where(AuthSession.account_id==account.id,AuthSession.revoked_at.is_(None),AuthSession.expires_at>utcnow())) if account else 0
    return {'ended_mapping_ids':[str(v) for v in (ended or [])],'affected_store_ids':[str(v) for v in (stores or [])],'active_session_count':count,'new_business_blocked':blocked}


def check_role_region(db,role,region_id):
    if role in ('ofc','regional') and region_id is None:raise ApiError(422,'VALIDATION_ERROR','OFC와 지역 계정에는 지역이 필요합니다.')
    if role in ('hq','platform_operator') and region_id is not None:raise ApiError(422,'VALIDATION_ERROR','이 역할에는 지역을 지정할 수 없습니다.')
    if region_id:
        region=db.get(Region,region_id)
        if not region or not region.is_active:raise ApiError(422,'INACTIVE_TARGET','활성 지역을 선택해 주세요.')


def create_account(db,actor,data,request_id):
    check_role_region(db,data.role,data.region_id)
    row=Account(login_id=data.login_id,display_name=data.display_name.strip(),role=data.role,region_id=data.region_id,password_hash=hash_password(data.password),is_active=True)
    if not row.display_name:raise ApiError(422,'VALIDATION_ERROR','이름을 입력해 주세요.')
    db.add(row);db.flush()
    audit(db,actor,'accounts.create','account',row,data.reason,{},operator_account(db,row),request_id)
    db.commit();return operator_account(db,row)


def patch_values(data,model):
    values=data.model_dump(exclude_unset=True,exclude={'version','reason'})
    if not values:raise ApiError(422,'VALIDATION_ERROR','변경할 필드를 입력해 주세요.')
    for key,value in list(values.items()):
        if key=='password':
            if value is None:raise ApiError(422,'VALIDATION_ERROR','비밀번호를 비울 수 없습니다.')
            continue
        if value is None and not model.__table__.columns[key].nullable:raise ApiError(422,'VALIDATION_ERROR','필수값을 비울 수 없습니다.')
        if isinstance(value,str):
            values[key]=value.strip()
            if key not in ('description','address') and not values[key]:raise ApiError(422,'VALIDATION_ERROR','필수값을 입력해 주세요.')
    return values


def check_version(row,version):
    if row.version!=version:raise ApiError(409,'VERSION_CONFLICT','다른 변경이 반영되었습니다. 다시 조회해 주세요.')


def patch_account(db,actor,target_id,data,request_id):
    row=lock_row(db,Account,target_id)
    if row.role=='platform_operator':raise ApiError(403,'FORBIDDEN','운영자 계정은 초기 설정에서 관리합니다.')
    check_version(row,data.version);values=patch_values(data,Account)
    role=values.get('role',row.role);region_id=values.get('region_id',row.region_id)
    if role!=row.role or region_id!=row.region_id:
        check_role_region(db,role,region_id)
    before=operator_account(db,row);ended=[];affected=[]
    changed=any(key=='password' or getattr(row,key)!=value for key,value in values.items())
    if not changed:return {'account':before,'impact':impact(db,row,blocked=not row.is_active)}
    for model in (StoreOwnerMapping,OFCStoreMapping):
        mappings=list(db.scalars(select(model).where(model.account_id==row.id,model.ended_at.is_(None))))
        for mapping in mappings:
            appropriate=(model is StoreOwnerMapping and role=='store_owner') or (model is OFCStoreMapping and role=='ofc' and db.get(Store,mapping.store_id).region_id==region_id)
            if not appropriate:
                mapping.ended_at=utcnow();ended.append(mapping.id);affected.append(mapping.store_id)
    for key,value in values.items():
        if key=='password':row.password_hash=hash_password(value)
        else:setattr(row,key,value)
    row.version+=1;db.flush()
    after=operator_account(db,row);after['ended_mapping_ids']=[str(v) for v in ended]
    audit(db,actor,'accounts.update','account',row,data.reason,before,after,request_id)
    db.commit();return {'account':operator_account(db,row),'impact':impact(db,row,ended,affected,not row.is_active)}


def set_mappings(db,actor,target_id,data,request_id):
    row=lock_row(db,Account,target_id);check_version(row,data.version)
    if row.role not in ('store_owner','ofc'):raise ApiError(422,'VALIDATION_ERROR','점주 또는 OFC 계정만 매장을 연결할 수 있습니다.')
    target=set(data.store_ids)
    stores=list(db.scalars(select(Store).where(Store.id.in_(target)).order_by(Store.id).with_for_update()))
    if len(stores)!=len(target):raise ApiError(422,'VALIDATION_ERROR','존재하는 매장을 선택해 주세요.')
    for store in stores:
        region=db.get(Region,store.region_id)
        if not store.is_active or not region.is_active:raise ApiError(422,'INACTIVE_TARGET','활성 매장을 연결해 주세요.')
        if row.role=='ofc' and store.region_id!=row.region_id:raise ApiError(422,'VALIDATION_ERROR','OFC 소속 지역의 매장만 연결할 수 있습니다.')
    model=StoreOwnerMapping if row.role=='store_owner' else OFCStoreMapping
    current=active_mappings(db,row);current_ids={v.store_id for v in current};before=operator_account(db,row)
    if target==current_ids:return {'account':before,'impact':impact(db,row)}
    ended=[]
    if row.role=='ofc':
        conflicts=list(db.scalars(select(OFCStoreMapping).where(OFCStoreMapping.store_id.in_(target-current_ids),OFCStoreMapping.ended_at.is_(None))))
        for mapping in conflicts:
            mapping.ended_at=utcnow();ended.append(mapping.id)
    for mapping in current:
        if mapping.store_id not in target:mapping.ended_at=utcnow();ended.append(mapping.id)
    db.flush()
    for store_id in target-current_ids:db.add(model(account_id=row.id,store_id=store_id,changed_by_id=actor.id,reason=data.reason))
    row.version+=1;db.flush()
    after=operator_account(db,row);after['ended_mapping_ids']=[str(v) for v in ended]
    audit(db,actor,'accounts.mappings','account',row,data.reason,before,after,request_id)
    db.commit();return {'account':operator_account(db,row),'impact':impact(db,row,ended,target|current_ids)}

MASTER_MODELS={'regions':Region,'stores':Store,'categories':Category}

def master_dto(db,row):
    if isinstance(row,Store):return store_dto(db,row)
    if isinstance(row,Category):return category_dto(row)
    return region_dto(row)


def create_master(db,actor,kind,data,request_id):
    values=data.model_dump(exclude={'reason'})
    if kind=='stores':
        region=db.get(Region,values['region_id'])
        if not region or not region.is_active:raise ApiError(422,'INACTIVE_TARGET','활성 지역을 선택해 주세요.')
    for key,value in list(values.items()):
        if isinstance(value,str):values[key]=value.strip()
    if not values['name']:raise ApiError(422,'VALIDATION_ERROR','이름을 입력해 주세요.')
    row=MASTER_MODELS[kind](**values);db.add(row);db.flush()
    audit(db,actor,kind+'.create','category' if kind=='categories' else kind[:-1],row,data.reason,{},master_dto(db,row),request_id)
    db.commit();return master_dto(db,row)


def patch_master(db,actor,kind,target_id,data,request_id):
    model=MASTER_MODELS[kind];row=lock_row(db,model,target_id);check_version(row,data.version)
    values=patch_values(data,model);before=master_dto(db,row);ended=[];affected=[]
    if kind=='stores' and 'region_id' in values:
        region=db.get(Region,values['region_id'])
        if not region or not region.is_active:raise ApiError(422,'INACTIVE_TARGET','활성 지역을 선택해 주세요.')
        for mapping in db.scalars(select(OFCStoreMapping).where(OFCStoreMapping.store_id==row.id,OFCStoreMapping.ended_at.is_(None))):
            ofc=db.get(Account,mapping.account_id)
            if ofc.region_id!=region.id:mapping.ended_at=utcnow();ended.append(mapping.id)
    changed=any(getattr(row,key)!=value for key,value in values.items())
    if changed:
        for key,value in values.items():setattr(row,key,value)
        row.version+=1;db.flush()
        after=master_dto(db,row);after['ended_mapping_ids']=[str(v) for v in ended]
        audit(db,actor,kind+'.update','category' if kind=='categories' else kind[:-1],row,data.reason,before,after,request_id);db.commit()
    if kind=='stores':affected=[row.id]
    elif kind=='regions':affected=list(db.scalars(select(Store.id).where(Store.region_id==row.id)))
    return {kind[:-1] if kind!='categories' else 'category':master_dto(db,row),'impact':impact(db,ended=ended,stores=affected,blocked=not row.is_active)}


def announcement_dto(row):return fields(row,['id','title','body','severity','starts_at','ends_at','is_active','version','created_at','updated_at'])


def save_announcement(db,actor,data,request_id,target_id=None):
    row=lock_row(db,Announcement,target_id) if target_id else Announcement(created_by_id=actor.id,is_active=True)
    before=announcement_dto(row) if target_id else {}
    if target_id:check_version(row,data.version);values=patch_values(data,Announcement)
    else:values=data.model_dump(exclude={'reason'})
    start=values.get('starts_at',row.starts_at);end=values.get('ends_at',row.ends_at)
    if end and as_utc(end)<=as_utc(start):raise ApiError(422,'VALIDATION_ERROR','종료시각은 시작시각 이후여야 합니다.')
    if target_id and all(getattr(row,key)==value for key,value in values.items()):return before
    for key,value in values.items():setattr(row,key,value)
    if target_id:row.version+=1
    db.add(row);db.flush()
    audit(db,actor,'announcements.update' if target_id else 'announcements.create','announcement',row,data.reason,before,announcement_dto(row),request_id)
    db.commit();return announcement_dto(row)


def operation_job(db,row):
    result=fields(row,['id','status','created_at','queued_at','started_at','finished_at','error_code','error_message','current_attempt_id','is_fixture'])
    result['attempt_count']=db.scalar(select(func.count()).select_from(AnalysisAttempt).where(AnalysisAttempt.job_id==row.id))
    active=db.scalar(select(func.count()).select_from(AnalysisAttempt).where(AnalysisAttempt.job_id==row.id,AnalysisAttempt.status.in_(['queued','running'])))
    result['can_retry']=row.status=='failed' and not active
    return result


def operation_attempt(row):return fields(row,['id','attempt_number','status','queued_at','started_at','finished_at','deadline_at','lease_expires_at','error_code','error_message','result_applied'])


def audit_dto(db,row):
    result=fields(row,['id','actor_id','action','target_type','target_id','reason','before_data','after_data','outcome','request_id','created_at'])
    account=db.get(Account,row.actor_id);result['actor_name']=account.display_name if account else ''
    return result


def service_dashboard(db):
    from server.vercel_runtime import enabled, ai_settings
    request_mode=enabled()
    now=utcnow();db.execute(select(1))
    services=[{'name':'api','status':'up','checked_at':scalar(now),'heartbeat_at':None,'last_success_at':None,'error_code':None,'is_fixture':False},
              {'name':'db','status':'up','checked_at':scalar(now),'heartbeat_at':None,'last_success_at':None,'error_code':None,'is_fixture':False}]
    try:
        if request_mode:
            config=ai_settings()
            ai_up=config.ai_requests_enabled and bool(config.openai_api_key.get_secret_value().strip())
        else:
            response=httpx.get(get_settings().ai_service_url+'/health',timeout=1.0,trust_env=False,headers={'Authorization':'Bearer '+get_settings().ai_service_token})
            ai_up=response.is_success
    except httpx.HTTPError:ai_up=False
    services.append({'name':'ai','status':'up' if ai_up else 'down','checked_at':scalar(now),'heartbeat_at':None,'last_success_at':None,'error_code':None if ai_up else 'AI_UNAVAILABLE','is_fixture':False})
    status_rows=list(db.scalars(select(ServiceStatus)));heartbeat=None
    last_success=None;last_failure=None;last_error=None
    for row in status_rows:
        if row.service_name not in ('api','db','ai') and not (request_mode and row.service_name=='worker'):
            data=fields(row,['status','checked_at','heartbeat_at','last_success_at','error_code','is_fixture']);data['name']=row.service_name
            if row.service_name=='worker' and row.heartbeat_at and not row.is_fixture:
                heartbeat=max(0,(now-as_utc(row.heartbeat_at)).total_seconds())
                if heartbeat>30:data['status']='unknown'
            services.append(data)
        if not row.is_fixture and row.service_name=='model':
            if row.last_success_at and (not last_success or as_utc(row.last_success_at)>as_utc(last_success)):last_success=row.last_success_at
            if row.last_failure_at and (not last_failure or as_utc(row.last_failure_at)>as_utc(last_failure)):last_failure=row.last_failure_at;last_error=row.error_code
    if not any(row['name']=='worker' for row in services):
        services.append({'name':'worker','status':'up' if request_mode else 'unknown','checked_at':scalar(now),'heartbeat_at':None,'last_success_at':None,'error_code':None,'is_fixture':False})
    def counts(fixture):
        result=dict.fromkeys(('queued','running','succeeded','failed'),0)
        result.update(dict(db.execute(select(AnalysisJob.status,func.count()).where(AnalysisJob.is_fixture==fixture).group_by(AnalysisJob.status)).all()))
        return result
    missing_owner=db.scalar(select(func.count()).select_from(Account).where(Account.role=='store_owner',Account.is_active.is_(True),~Account.id.in_(select(StoreOwnerMapping.account_id).where(StoreOwnerMapping.ended_at.is_(None)))))
    missing_ofc=db.scalar(select(func.count()).select_from(Account).where(Account.role=='ofc',Account.is_active.is_(True),~Account.id.in_(select(OFCStoreMapping.account_id).where(OFCStoreMapping.ended_at.is_(None)))))
    unassigned=db.scalar(select(func.count()).select_from(Store).where(Store.is_active.is_(True),~Store.id.in_(select(OFCStoreMapping.store_id).where(OFCStoreMapping.ended_at.is_(None)))))
    readiness='unknown' if not last_success and not last_failure else 'available' if last_success and (not last_failure or as_utc(last_success)>as_utc(last_failure)) else 'unavailable'
    return {'services':services,'jobs':counts(False),'fixture_jobs':counts(True),'worker_heartbeat_age_seconds':heartbeat,'model':{'readiness':readiness,'last_success_at':scalar(last_success),'last_failure_at':scalar(last_failure),'last_error_code':last_error},'data_quality':{'unmapped_owner_accounts':missing_owner,'unmapped_ofc_accounts':missing_ofc,'unassigned_stores':unassigned}}
