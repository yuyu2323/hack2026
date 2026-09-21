from sqlalchemy import select
from server.operations.models import AuditEvent


def test_deactivation_changes_existing_session_and_audit_is_safe(client,make_client,db,account_factory,login_as):
    owner=account_factory();operator=account_factory('platform_operator')
    owner_client=make_client();login_as(owner,owner_client)
    headers=login_as(operator)
    response=client.patch(f'/api/operations/accounts/{owner.id}',json={'version':1,'is_active':False,'reason':'계정 이용 종료'},headers=headers)
    assert response.status_code==200
    assert owner_client.get('/api/auth/me').status_code==401
    audit=db.scalar(select(AuditEvent).where(AuditEvent.target_id==owner.id))
    assert audit and audit.reason=='계정 이용 종료'
    assert 'password' not in str(audit.before_data) and 'password' not in str(audit.after_data)


def test_operator_cannot_create_operator_or_business_can_operate(client,account_factory,login_as):
    operator=account_factory('platform_operator');headers=login_as(operator)
    response=client.post('/api/operations/accounts',json={'login_id':'new.operator','display_name':'권한상승','role':'platform_operator','region_id':None,'password':'only-test-invalid-password','reason':'권한상승'},headers=headers)
    assert response.status_code==422
    business=account_factory('hq');login_as(business)
    assert client.get('/api/operations/accounts').status_code==403


def test_mapping_replacement_and_role_change_preserve_history(client,make_client,db,account_factory,store_factory,login_as):
    from server.stores.models import StoreOwnerMapping
    from server.accounts.models import Account
    owner=account_factory();operator=account_factory('platform_operator');first=store_factory();second=store_factory()
    headers=login_as(operator)
    response=client.put(f'/api/operations/accounts/{owner.id}/mappings',json={'version':1,'store_ids':[str(first.id)],'reason':'최초 배정'},headers=headers)
    assert response.status_code==200
    owner_client=make_client();login_as(owner,owner_client)
    assert owner_client.get('/api/stores').json()['total']==1
    response=client.put(f'/api/operations/accounts/{owner.id}/mappings',json={'version':2,'store_ids':[str(second.id)],'reason':'범위 변경'},headers=headers)
    assert response.status_code==200
    assert owner_client.get('/api/stores/'+str(first.id)).status_code==404
    assert len(list(db.scalars(select(StoreOwnerMapping).where(StoreOwnerMapping.account_id==owner.id))))==2
    stale=client.patch(f'/api/operations/accounts/{owner.id}',json={'version':1,'display_name':'늦은 변경','reason':'이전 화면'},headers=headers)
    assert stale.status_code==409
    assert client.patch(f'/api/operations/accounts/{owner.id}',json={'version':3,'role':'hq','region_id':None,'reason':'담당 역할 변경'},headers=headers).status_code==200
    assert owner_client.get('/api/auth/me').json()['role']=='hq'
    assert all(row.ended_at for row in db.scalars(select(StoreOwnerMapping).where(StoreOwnerMapping.account_id==owner.id)))


def test_master_deactivation_preserves_rows_and_announcement_period(client,db,account_factory,store_factory,login_as):
    from datetime import timedelta
    from server.core.db import utcnow
    from server.stores.models import Store
    operator=account_factory('platform_operator');store=store_factory();headers=login_as(operator)
    response=client.patch(f'/api/operations/stores/{store.id}',json={'version':1,'is_active':False,'reason':'영업 종료'},headers=headers)
    assert response.status_code==200 and response.json()['impact']['new_business_blocked']
    assert db.get(Store,store.id) is not None
    now=utcnow()
    for title,start,end in [('현재 안내',now-timedelta(hours=1),now+timedelta(hours=1)),('만료 안내',now-timedelta(days=2),now-timedelta(days=1))]:
        response=client.post('/api/operations/announcements',json={'title':title,'body':'시연 운영 안내','severity':'info','starts_at':start.isoformat(),'ends_at':end.isoformat(),'reason':'공지 등록'},headers=headers)
        assert response.status_code==201
    assert [row['title'] for row in client.get('/api/announcements').json()['items']]==['현재 안내']


def test_safe_jobs_dto_has_no_business_payload(client,db,account_factory,store_factory,login_as):
    from datetime import timedelta
    from server.core.db import utcnow
    from server.core.models import Category,Submission,AnalysisJob
    owner=account_factory();operator=account_factory('platform_operator');store=store_factory()
    category=Category(code='job-demo',name='시연');db.add(category);db.flush()
    submission=Submission(store_id=store.id,category_id=category.id,submitted_by_id=owner.id,question='본문은 운영자에게 노출 금지',source_kind='seed_demo');db.add(submission);db.flush()
    job=AnalysisJob(submission_id=submission.id,status='failed',queue_deadline_at=utcnow()+timedelta(seconds=180),error_code='MODEL_TIMEOUT',error_message='분석 시간이 초과되었습니다.');db.add(job);db.commit();login_as(operator)
    response=client.get('/api/operations/jobs/'+str(job.id));assert response.status_code==200
    payload=response.json()
    assert not {'submission_id','question','photos','context','review','store_id'} & payload.keys()
    assert payload['can_retry'] is True


def test_patch_rejects_empty_and_null_required_values(client,account_factory,login_as):
    operator=account_factory('platform_operator');owner=account_factory();headers=login_as(operator)
    endpoint=f'/api/operations/accounts/{owner.id}'
    assert client.patch(endpoint,json={'version':1,'reason':'빈 변경'},headers=headers).status_code==422
    assert client.patch(endpoint,json={'version':1,'display_name':None,'reason':'이름 삭제'},headers=headers).status_code==422
    response=client.patch(endpoint,json={'version':1,'display_name':owner.display_name,'reason':'변경 없음'},headers=headers)
    assert response.status_code==200 and response.json()['account']['version']==1


import pytest
@pytest.mark.postgres
def test_postgres_version_conflict_keeps_one_audited_change(postgres_db):
    import uuid
    from threading import Barrier
    from concurrent.futures import ThreadPoolExecutor
    from sqlalchemy.orm import Session
    from sqlalchemy import func
    from server.core.models import Account
    from server.core.security import hash_password
    from server.core.errors import ApiError
    from server.operations.schemas import AccountUpdate
    from server.operations.service import patch_account
    password_hash=hash_password('only-test-invalid-password')
    operator=Account(login_id='race.operator',display_name='운영자',role='platform_operator',password_hash=password_hash)
    owner=Account(login_id='race.owner',display_name='기존 이름',role='store_owner',password_hash=password_hash)
    postgres_db.add_all([operator,owner]);postgres_db.commit();barrier=Barrier(2)
    def run(index):
        with Session(postgres_db.bind,expire_on_commit=False) as db:
            actor=db.get(Account,operator.id);barrier.wait()
            try:
                patch_account(db,actor,owner.id,AccountUpdate(version=1,display_name='변경'+str(index),reason='동시 변경'),uuid.uuid4())
                return 'accepted'
            except ApiError as error:db.rollback();return error.code
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,[1,2]))
    assert sorted(results)==['VERSION_CONFLICT','accepted']
    postgres_db.expire_all()
    assert postgres_db.get(Account,owner.id).version==2
    assert postgres_db.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.target_id==owner.id))==1


def test_store_region_change_ends_incompatible_ofc_assignment(client,db,account_factory,store_factory,region_factory,login_as):
    from server.stores.models import OFCStoreMapping
    operator=account_factory('platform_operator');store=store_factory();new_region=region_factory();ofc=account_factory('ofc',region_id=store.region_id)
    mapping=OFCStoreMapping(account_id=ofc.id,store_id=store.id,changed_by_id=operator.id,reason='초기 배정');db.add(mapping);db.commit()
    headers=login_as(operator)
    response=client.patch('/api/operations/stores/'+str(store.id),json={'version':1,'region_id':str(new_region.id),'reason':'지역 정정'},headers=headers)
    assert response.status_code==200
    assert response.json()['impact']['ended_mapping_ids']==[str(mapping.id)]
    assert db.get(OFCStoreMapping,mapping.id).ended_at is not None


def test_operator_reassignment_corrects_ofc_mapping_without_deleting_history(client,db,account_factory,store_factory,login_as):
    from server.stores.models import OFCStoreMapping
    operator=account_factory('platform_operator');store=store_factory();first=account_factory('ofc',region_id=store.region_id);second=account_factory('ofc',region_id=store.region_id)
    mapping=OFCStoreMapping(account_id=first.id,store_id=store.id,changed_by_id=operator.id,reason='초기 배정');db.add(mapping);db.commit();headers=login_as(operator)
    response=client.put('/api/operations/accounts/'+str(second.id)+'/mappings',json={'version':1,'store_ids':[str(store.id)],'reason':'OFC 변경'},headers=headers)
    assert response.status_code==200
    rows=list(db.scalars(select(OFCStoreMapping).where(OFCStoreMapping.store_id==store.id)))
    assert len(rows)==2 and sum(row.ended_at is None for row in rows)==1
    assert next(row for row in rows if row.ended_at is None).account_id==second.id


def test_service_health_never_calls_model_and_separates_fixture(client,db,account_factory,login_as,monkeypatch):
    from server.operations import service
    from server.operations.models import ServiceStatus
    from server.core.db import utcnow
    calls=[]
    class Healthy:
        is_success=True
    def health(url,**kwargs):
        calls.append(url)
        assert url.endswith('/health') and '/analyze' not in url
        return Healthy()
    monkeypatch.setattr(service.httpx,'get',health)
    now=utcnow()
    db.add(ServiceStatus(service_name='worker',status='up',checked_at=now,heartbeat_at=now,details={}))
    db.add(ServiceStatus(service_name='fixture-model',status='down',checked_at=now,is_fixture=True,last_failure_at=now,error_code='MODEL_TIMEOUT',details={}))
    db.commit();login_as(account_factory('platform_operator'))
    response=client.get('/api/operations/status');assert response.status_code==200
    data=response.json();assert len(calls)==1 and data['model']['readiness']=='unknown'
    assert data['worker_heartbeat_age_seconds'] is not None
    assert any(row['is_fixture'] for row in data['services'])


def test_operator_retry_api_replays_same_attempt_and_omits_business_body(client,db,account_factory,store_factory,login_as):
    from datetime import timedelta
    from server.core.db import utcnow
    from server.core.models import Category,Submission,AnalysisJob,AnalysisAttempt
    owner=account_factory();operator=account_factory('platform_operator');store=store_factory()
    category=Category(code='retry-api',name='재처리');db.add(category);db.flush()
    submission=Submission(store_id=store.id,category_id=category.id,submitted_by_id=owner.id,question='영업 본문',source_kind='seed_demo');db.add(submission);db.flush()
    now=utcnow();job=AnalysisJob(submission_id=submission.id,status='failed',queue_deadline_at=now+timedelta(seconds=180),finished_at=now,error_code='MODEL_TIMEOUT',error_message='분석 시간이 초과되었습니다.');db.add(job);db.flush()
    old=AnalysisAttempt(job_id=job.id,attempt_number=1,status='expired',queued_at=now,finished_at=now,error_code='MODEL_TIMEOUT',result_applied=False);db.add(old);db.flush();job.current_attempt_id=old.id;db.commit()
    headers=login_as(operator);headers['Idempotency-Key']='retry-api-idempotent-2026'
    endpoint='/api/operations/jobs/'+str(job.id)+'/retry'
    response=client.post(endpoint,json={'reason':'환경 복구'},headers=headers)
    assert response.status_code==202,response.text
    assert response.json()['status']=='queued' and 'submission_id' not in response.json()
    first_attempt=response.json()['current_attempt_id']
    replay=client.post(endpoint,json={'reason':'환경 복구'},headers=headers)
    assert replay.status_code==202 and replay.headers['Idempotency-Replayed']=='true'
    assert replay.json()['current_attempt_id']==first_attempt
    assert db.get(AnalysisAttempt,old.id).status=='expired'
    assert len(list(db.scalars(select(AnalysisAttempt).where(AnalysisAttempt.job_id==job.id))))==2
