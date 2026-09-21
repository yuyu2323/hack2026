"""모든 영업 API가 공유하는 현재 DB 담당 범위."""
from sqlalchemy import select
from server.accounts.models import Account
from server.stores.models import Store,Region,StoreOwnerMapping,OFCStoreMapping
from server.core.errors import ApiError

BUSINESS_ROLES=('store_owner','ofc','regional','hq')


def require_business(account):
    if account.role not in BUSINESS_ROLES:
        raise ApiError(403,'FORBIDDEN','영업 데이터에 접근할 권한이 없습니다.')


def accessible_store_ids(db, account):
    if account.role=='hq': return list(db.scalars(select(Store.id)))
    if account.role=='regional': return list(db.scalars(select(Store.id).where(Store.region_id==account.region_id)))
    mapping=StoreOwnerMapping if account.role=='store_owner' else OFCStoreMapping if account.role=='ofc' else None
    if mapping is None: return []
    query=select(mapping.store_id).where(mapping.account_id==account.id,mapping.ended_at.is_(None))
    if account.role=='ofc': query=query.join(Store,Store.id==mapping.store_id).where(Store.region_id==account.region_id)
    return list(db.scalars(query))


def require_store_access(db, account, store_id, write=False):
    require_business(account)
    store=db.get(Store,store_id)
    if store is None or store.id not in accessible_store_ids(db,account):
        raise ApiError(404,'NOT_FOUND','대상을 찾을 수 없습니다.')
    if write:
        region=db.get(Region,store.region_id)
        if not store.is_active or not region or not region.is_active:
            raise ApiError(422,'INACTIVE_TARGET','비활성 매장 또는 지역에는 새 업무를 등록할 수 없습니다.')
    return store
