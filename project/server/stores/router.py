import uuid
from fastapi import APIRouter,Depends,Query,Request,Response,Header
from sqlalchemy import select,or_,exists
from sqlalchemy.orm import Session
from server.core.auth import get_current_account,require_csrf
from server.core.db import get_db
from server.core.permissions import require_business,accessible_store_ids,require_store_access
from server.core.serialization import paginate
from server.core.errors import ApiError
from server.stores.models import Store,Region,Category,OFCStoreMapping
from server.stores.schemas import ReasonInput
from server.stores.service import store_dto,region_dto,category_dto,claim_store

router=APIRouter(prefix='/api',tags=['stores'])

@router.get('/stores')
def stores(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),q:str=Query('',max_length=120),region_id:uuid.UUID|None=None,is_active:bool|None=None,db:Session=Depends(get_db),account=Depends(get_current_account)):
    require_business(account)
    if region_id and account.role in ('ofc','regional') and region_id!=account.region_id: raise ApiError(404,'NOT_FOUND','대상을 찾을 수 없습니다.')
    query=select(Store).where(Store.id.in_(accessible_store_ids(db,account)))
    if q: query=query.where(or_(Store.name.ilike('%'+q+'%'),Store.code.ilike('%'+q+'%')))
    if region_id: query=query.where(Store.region_id==region_id)
    if is_active is not None: query=query.where(Store.is_active==is_active)
    return paginate(db,query.order_by(Store.name,Store.id),page,page_size,lambda row:store_dto(db,row))

@router.get('/stores/candidates')
def candidates(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),q:str=Query('',max_length=120),db:Session=Depends(get_db),account=Depends(get_current_account)):
    if account.role!='ofc': raise ApiError(403,'FORBIDDEN','OFC만 후보를 조회할 수 있습니다.')
    query=select(Store).join(Region).where(Store.region_id==account.region_id,Store.is_active.is_(True),Region.is_active.is_(True),~exists(select(OFCStoreMapping.id).where(OFCStoreMapping.store_id==Store.id,OFCStoreMapping.ended_at.is_(None))))
    if q: query=query.where(or_(Store.name.ilike('%'+q+'%'),Store.code.ilike('%'+q+'%')))
    return paginate(db,query.order_by(Store.name,Store.id),page,page_size,lambda row:{key:value for key,value in store_dto(db,row).items() if key in ('id','code','name','region_id','region_name','store_type')})

@router.get('/stores/{store_id}')
def store(store_id:uuid.UUID,db:Session=Depends(get_db),account=Depends(get_current_account)):
    return store_dto(db,require_store_access(db,account,store_id))

@router.post('/stores/{store_id}/claim',status_code=201,dependencies=[Depends(require_csrf)])
def claim(store_id:uuid.UUID,data:ReasonInput,request:Request,response:Response,idempotency_key:str=Header(...,min_length=16,max_length=128,pattern=r'^[A-Za-z0-9_.:-]+$'),db:Session=Depends(get_db),account=Depends(get_current_account)):
    row,replayed=claim_store(db,account,store_id,data.reason,idempotency_key,request.state.request_id)
    if replayed: response.headers['Idempotency-Replayed']='true'
    return store_dto(db,row)

@router.get('/categories')
def categories(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),is_active:bool|None=None,db:Session=Depends(get_db),account=Depends(get_current_account)):
    require_business(account);query=select(Category)
    if is_active is not None:query=query.where(Category.is_active==is_active)
    return paginate(db,query.order_by(Category.name,Category.id),page,page_size,category_dto)

@router.get('/regions')
def regions(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),db:Session=Depends(get_db),account=Depends(get_current_account)):
    if account.role not in ('ofc','regional','hq'): raise ApiError(403,'FORBIDDEN','지역 목록을 조회할 권한이 없습니다.')
    query=select(Region)
    if account.role!='hq':query=query.where(Region.id==account.region_id)
    return paginate(db,query.order_by(Region.name,Region.id),page,page_size,region_dto)
