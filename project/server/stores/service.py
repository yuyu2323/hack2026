"""현재 담당 범위의 매장 조회와 원자적인 OFC 담당 등록."""
import hashlib,json,uuid
from sqlalchemy import select,func
from server.stores.models import Store,Region,Category,StoreOwnerMapping,OFCStoreMapping
from server.accounts.models import Account
from server.analysis_jobs.models import IdempotencyRecord
from server.operations.models import AuditEvent
from server.core.errors import ApiError
from server.core.permissions import require_store_access
from server.core.serialization import fields


def region_dto(row): return fields(row,['id','code','name','is_active','version','created_at','updated_at'])
def category_dto(row): return fields(row,['id','code','name','description','is_active','version','created_at','updated_at'])

def store_dto(db,row):
    result=fields(row,['id','code','name','region_id','store_type','address','is_active','version'])
    region=db.get(Region,row.region_id)
    result['region_name']=region.name if region else ''
    result['can_submit']=bool(row.is_active and region and region.is_active)
    ofc=db.scalar(select(Account).join(OFCStoreMapping,OFCStoreMapping.account_id==Account.id).where(OFCStoreMapping.store_id==row.id,OFCStoreMapping.ended_at.is_(None)))
    result['ofc']={'id':str(ofc.id),'display_name':ofc.display_name} if ofc else None
    result['owner_count']=db.scalar(select(func.count()).select_from(StoreOwnerMapping).where(StoreOwnerMapping.store_id==row.id,StoreOwnerMapping.ended_at.is_(None)))
    return result


def claim_store(db,account,store_id,reason,key,request_id):
    if account.role!='ofc': raise ApiError(403,'FORBIDDEN','OFC만 담당 매장을 등록할 수 있습니다.')
    store=db.scalar(select(Store).where(Store.id==store_id).with_for_update())
    if not store or store.region_id!=account.region_id: raise ApiError(404,'NOT_FOUND','대상을 찾을 수 없습니다.')
    region=db.get(Region,store.region_id)
    if not store.is_active or not region.is_active: raise ApiError(422,'INACTIVE_TARGET','비활성 대상을 담당 등록할 수 없습니다.')
    digest=hashlib.sha256(json.dumps({'method':'POST','target':str(store_id),'reason':reason},sort_keys=True).encode()).hexdigest()
    old=db.scalar(select(IdempotencyRecord).where(IdempotencyRecord.account_id==account.id,IdempotencyRecord.operation=='stores.claim',IdempotencyRecord.key==key))
    if old:
        if old.request_hash!=digest: raise ApiError(409,'IDEMPOTENCY_CONFLICT','다른 요청에 사용한 키입니다.')
        require_store_access(db,account,store_id)
        return store,True
    existing=db.scalar(select(OFCStoreMapping).where(OFCStoreMapping.store_id==store_id,OFCStoreMapping.ended_at.is_(None)))
    if existing: raise ApiError(409,'ALREADY_ASSIGNED','이미 담당자가 배정된 매장입니다.')
    db.add(OFCStoreMapping(account_id=account.id,store_id=store.id,changed_by_id=account.id,reason=reason))
    db.add(IdempotencyRecord(account_id=account.id,operation='stores.claim',key=key,request_hash=digest,resource_id=store.id,response_status=201))
    db.add(AuditEvent(actor_id=account.id,action='stores.claim',target_type='store',target_id=store.id,reason=reason,before_data={'ofc_id':None},after_data={'ofc_id':str(account.id)},outcome='succeeded',request_id=uuid.UUID(str(request_id))))
    db.commit()
    return store,False
