import uuid
from datetime import date,datetime,time,timedelta,timezone
from fastapi import APIRouter,Depends,Query,Request,Response,Header,BackgroundTasks
from sqlalchemy import select,or_
from sqlalchemy.orm import Session
from server.core.auth import require_roles,require_csrf,get_current_account
from server.core.db import get_db,utcnow
from server.core.serialization import paginate
from server.core.errors import ApiError
from server.accounts.models import Account
from server.operations.models import AuditEvent,Announcement
from server.analysis_jobs.models import AnalysisJob,AnalysisAttempt
from server.stores.schemas import ReasonInput
from server.operations.schemas import AccountCreate,AccountUpdate,MappingUpdate,RegionCreate,RegionUpdate,CategoryCreate,CategoryUpdate,StoreCreate,StoreUpdate,AnnouncementCreate,AnnouncementUpdate
from server.operations import service

router=APIRouter(prefix='/api',tags=['operations'])
operator=Depends(require_roles('platform_operator'))
write=[Depends(require_csrf)]

@router.get('/operations/accounts')
def accounts(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),q:str=Query('',max_length=120),role:str|None=None,is_active:bool|None=None,mapping_status:str|None=None,db:Session=Depends(get_db),account=operator):
    if role and role not in ('store_owner','ofc','regional','hq','platform_operator'):raise ApiError(422,'VALIDATION_ERROR','잘못된 역할입니다.')
    if mapping_status and mapping_status not in ('ready','missing','invalid'):raise ApiError(422,'VALIDATION_ERROR','잘못된 연결상태입니다.')
    query=select(Account)
    if q:query=query.where(or_(Account.display_name.ilike('%'+q+'%'),Account.login_id.ilike('%'+q+'%')))
    if role:query=query.where(Account.role==role)
    if is_active is not None:query=query.where(Account.is_active==is_active)
    if mapping_status:
        rows=[service.operator_account(db,row) for row in db.scalars(query.order_by(Account.created_at.desc(),Account.id))]
        rows=[row for row in rows if row['mapping_status']==mapping_status]
        return {'items':rows[(page-1)*page_size:page*page_size],'total':len(rows),'page':page,'page_size':page_size}
    return paginate(db,query.order_by(Account.created_at.desc(),Account.id),page,page_size,lambda row:service.operator_account(db,row))

@router.get('/operations/accounts/{account_id}')
def account_detail(account_id:uuid.UUID,db:Session=Depends(get_db),account=operator):
    row=db.get(Account,account_id)
    if not row:raise ApiError(404,'NOT_FOUND','대상을 찾을 수 없습니다.')
    return service.operator_account(db,row)

@router.post('/operations/accounts',status_code=201,dependencies=write)
def account_create(data:AccountCreate,request:Request,db:Session=Depends(get_db),account=operator):return service.create_account(db,account,data,request.state.request_id)

@router.patch('/operations/accounts/{account_id}',dependencies=write)
def account_update(account_id:uuid.UUID,data:AccountUpdate,request:Request,db:Session=Depends(get_db),account=operator):return service.patch_account(db,account,account_id,data,request.state.request_id)

@router.put('/operations/accounts/{account_id}/mappings',dependencies=write)
def account_mappings(account_id:uuid.UUID,data:MappingUpdate,request:Request,db:Session=Depends(get_db),account=operator):return service.set_mappings(db,account,account_id,data,request.state.request_id)


def master_list(kind,page,page_size,q,is_active,region_id,db):
    model=service.MASTER_MODELS[kind];query=select(model)
    if q:query=query.where(or_(model.name.ilike('%'+q+'%'),model.code.ilike('%'+q+'%')))
    if is_active is not None:query=query.where(model.is_active==is_active)
    if region_id and kind=='stores':query=query.where(model.region_id==region_id)
    return paginate(db,query.order_by(model.name,model.id),page,page_size,lambda row:service.master_dto(db,row))

@router.get('/operations/regions')
def regions(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),q:str=Query('',max_length=120),is_active:bool|None=None,db:Session=Depends(get_db),account=operator):return master_list('regions',page,page_size,q,is_active,None,db)
@router.post('/operations/regions',status_code=201,dependencies=write)
def create_region(data:RegionCreate,request:Request,db:Session=Depends(get_db),account=operator):return service.create_master(db,account,'regions',data,request.state.request_id)
@router.patch('/operations/regions/{target_id}',dependencies=write)
def patch_region(target_id:uuid.UUID,data:RegionUpdate,request:Request,db:Session=Depends(get_db),account=operator):return service.patch_master(db,account,'regions',target_id,data,request.state.request_id)

@router.get('/operations/categories')
def categories(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),q:str=Query('',max_length=120),is_active:bool|None=None,db:Session=Depends(get_db),account=operator):return master_list('categories',page,page_size,q,is_active,None,db)
@router.post('/operations/categories',status_code=201,dependencies=write)
def create_category(data:CategoryCreate,request:Request,db:Session=Depends(get_db),account=operator):return service.create_master(db,account,'categories',data,request.state.request_id)
@router.patch('/operations/categories/{target_id}',dependencies=write)
def patch_category(target_id:uuid.UUID,data:CategoryUpdate,request:Request,db:Session=Depends(get_db),account=operator):return service.patch_master(db,account,'categories',target_id,data,request.state.request_id)

@router.get('/operations/stores')
def stores(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),q:str=Query('',max_length=120),is_active:bool|None=None,region_id:uuid.UUID|None=None,db:Session=Depends(get_db),account=operator):return master_list('stores',page,page_size,q,is_active,region_id,db)
@router.post('/operations/stores',status_code=201,dependencies=write)
def create_store(data:StoreCreate,request:Request,db:Session=Depends(get_db),account=operator):return service.create_master(db,account,'stores',data,request.state.request_id)
@router.patch('/operations/stores/{target_id}',dependencies=write)
def patch_store(target_id:uuid.UUID,data:StoreUpdate,request:Request,db:Session=Depends(get_db),account=operator):return service.patch_master(db,account,'stores',target_id,data,request.state.request_id)

@router.get('/operations/status')
def status(db:Session=Depends(get_db),account=operator):return service.service_dashboard(db)

@router.get('/operations/jobs')
def jobs(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),status:str|None=None,error_code:str|None=None,is_fixture:bool|None=None,db:Session=Depends(get_db),account=operator):
    query=select(AnalysisJob)
    if status:
        if status not in ('queued','running','failed','succeeded'):raise ApiError(422,'VALIDATION_ERROR','잘못된 처리상태입니다.')
        query=query.where(AnalysisJob.status==status)
    if error_code:query=query.where(AnalysisJob.error_code==error_code)
    if is_fixture is not None:query=query.where(AnalysisJob.is_fixture==is_fixture)
    return paginate(db,query.order_by(AnalysisJob.created_at.desc(),AnalysisJob.id),page,page_size,lambda row:service.operation_job(db,row))

@router.get('/operations/jobs/{job_id}')
def job(job_id:uuid.UUID,background_tasks:BackgroundTasks,db:Session=Depends(get_db),account=operator):
    row=db.get(AnalysisJob,job_id)
    if not row:raise ApiError(404,'NOT_FOUND','대상을 찾을 수 없습니다.')
    from server.vercel_runtime import schedule_analysis
    schedule_analysis(background_tasks,row.id)
    result=service.operation_job(db,row)
    result['attempts']=[service.operation_attempt(v) for v in db.scalars(select(AnalysisAttempt).where(AnalysisAttempt.job_id==job_id).order_by(AnalysisAttempt.attempt_number))]
    return result

@router.post('/operations/jobs/{job_id}/retry',status_code=202,dependencies=write)
def retry(job_id:uuid.UUID,data:ReasonInput,request:Request,response:Response,background_tasks:BackgroundTasks,idempotency_key:str=Header(...,min_length=16,max_length=128,pattern=r'^[A-Za-z0-9_.:-]+$'),db:Session=Depends(get_db),account=operator):
    from server.analysis_jobs.service import retry_job
    row,replayed=retry_job(db,account,job_id,data.reason,idempotency_key,request.state.request_id)
    from server.vercel_runtime import schedule_analysis
    schedule_analysis(background_tasks,row.id)
    if replayed:response.headers['Idempotency-Replayed']='true'
    return service.operation_job(db,row)

@router.get('/operations/audit')
def audit(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),actor_id:uuid.UUID|None=None,target_type:str|None=None,target_id:uuid.UUID|None=None,date_from:date|None=None,date_to:date|None=None,db:Session=Depends(get_db),account=operator):
    if date_from and date_to and date_from>date_to:raise ApiError(422,'VALIDATION_ERROR','기간을 확인해 주세요.')
    query=select(AuditEvent)
    if actor_id:query=query.where(AuditEvent.actor_id==actor_id)
    if target_type:query=query.where(AuditEvent.target_type==target_type)
    if target_id:query=query.where(AuditEvent.target_id==target_id)
    if date_from:query=query.where(AuditEvent.created_at>=datetime.combine(date_from,time.min,tzinfo=timezone.utc))
    if date_to:query=query.where(AuditEvent.created_at<datetime.combine(date_to+timedelta(days=1),time.min,tzinfo=timezone.utc))
    return paginate(db,query.order_by(AuditEvent.created_at.desc(),AuditEvent.id),page,page_size,lambda row:service.audit_dto(db,row))

@router.get('/operations/announcements')
def announcements(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),is_active:bool|None=None,db:Session=Depends(get_db),account=operator):
    query=select(Announcement)
    if is_active is not None:query=query.where(Announcement.is_active==is_active)
    return paginate(db,query.order_by(Announcement.created_at.desc(),Announcement.id),page,page_size,service.announcement_dto)

@router.post('/operations/announcements',status_code=201,dependencies=write)
def create_announcement(data:AnnouncementCreate,request:Request,db:Session=Depends(get_db),account=operator):return service.save_announcement(db,account,data,request.state.request_id)

@router.patch('/operations/announcements/{target_id}',dependencies=write)
def patch_announcement(target_id:uuid.UUID,data:AnnouncementUpdate,request:Request,db:Session=Depends(get_db),account=operator):return service.save_announcement(db,account,data,request.state.request_id,target_id)

@router.get('/announcements')
def active_announcements(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),db:Session=Depends(get_db),account=Depends(get_current_account)):
    query=select(Announcement).where(Announcement.is_active.is_(True),Announcement.starts_at<=utcnow(),or_(Announcement.ends_at.is_(None),Announcement.ends_at>utcnow()))
    return paginate(db,query.order_by(Announcement.created_at.desc(),Announcement.id),page,page_size,service.announcement_dto)
