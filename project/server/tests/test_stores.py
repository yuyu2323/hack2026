from server.stores.models import StoreOwnerMapping


def test_store_scope_changes_without_relogin(client,db,account_factory,store_factory,login_as):
    owner=account_factory();first=store_factory();second=store_factory()
    mapping=StoreOwnerMapping(account_id=owner.id,store_id=first.id,changed_by_id=owner.id,reason='최초 연결')
    db.add(mapping);db.commit();login_as(owner)
    response=client.get('/api/stores')
    assert response.status_code==200
    assert [item['id'] for item in response.json()['items']]==[str(first.id)]
    assert client.get('/api/stores/'+str(second.id)).status_code==404
    from server.core.db import utcnow
    mapping.ended_at=utcnow();db.commit()
    assert client.get('/api/stores').json()['total']==0
    assert client.get('/api/stores/'+str(first.id)).status_code==404


def test_operator_has_no_business_store_scope(client,account_factory,login_as):
    login_as(account_factory('platform_operator'))
    assert client.get('/api/stores').status_code==403


def test_ofc_claim_is_scoped_idempotent_and_target_bound(client,db,account_factory,store_factory,login_as):
    ofc=account_factory('ofc')
    from server.stores.models import Region
    region=db.get(Region,ofc.region_id)
    first=store_factory(region);second=store_factory(region);outside=store_factory()
    headers=login_as(ofc);headers['Idempotency-Key']='same-key-target-bound-1234'
    rows=client.get('/api/stores/candidates').json()['items']
    assert {row['id'] for row in rows}=={str(first.id),str(second.id)}
    assert all(set(row)=={'id','code','name','region_id','region_name','store_type'} for row in rows)
    path='/api/stores/'+str(first.id)+'/claim'
    first_reply=client.post(path,json={'reason':'담당 등록'},headers=headers);assert first_reply.status_code==201
    replay=client.post(path,json={'reason':'담당 등록'},headers=headers);assert replay.status_code==201
    assert replay.headers['Idempotency-Replayed']=='true'
    assert client.post('/api/stores/'+str(second.id)+'/claim',json={'reason':'담당 등록'},headers=headers).status_code==409
    assert client.post('/api/stores/'+str(outside.id)+'/claim',json={'reason':'담당 등록'},headers=headers).status_code==404


import pytest
@pytest.mark.postgres
def test_postgres_simultaneous_ofc_claim_has_one_winner(postgres_db):
    import uuid
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from sqlalchemy import select,func
    from sqlalchemy.orm import Session
    from server.core.models import Region,Store,Account,OFCStoreMapping
    from server.core.security import hash_password
    from server.core.errors import ApiError
    from server.stores.service import claim_store
    region=Region(code='race-region',name='동시성 지역');postgres_db.add(region);postgres_db.flush()
    store=Store(code='race-store',name='동시성 매장',region_id=region.id,store_type='도심형');postgres_db.add(store)
    accounts=[Account(login_id='race.'+str(i),display_name='경쟁 OFC',role='ofc',region_id=region.id,password_hash=hash_password('only-test-invalid-password')) for i in range(2)]
    postgres_db.add_all(accounts);postgres_db.commit();barrier=Barrier(2)
    def run(account_id):
        with Session(postgres_db.bind,expire_on_commit=False) as db:
            account=db.get(Account,account_id);barrier.wait()
            try:
                row,replayed=claim_store(db,account,store.id,'담당 등록','claim-'+uuid.uuid4().hex,uuid.uuid4())
                return 'accepted'
            except ApiError as error:
                db.rollback();return error.code
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,[row.id for row in accounts]))
    assert sorted(results)==['ALREADY_ASSIGNED','accepted']
    assert postgres_db.scalar(select(func.count()).select_from(OFCStoreMapping).where(OFCStoreMapping.ended_at.is_(None)))==1
