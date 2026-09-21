"""실제 PostgreSQL에서 점유·재처리·만료·결과 저장의 경쟁을 검증한다."""
import copy
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from server.analysis_jobs import service
from server.analysis_jobs.models import AnalysisJob, AnalysisAttempt, IdempotencyRecord
from server.accounts.models import Account
from server.core.db import utcnow
from server.core.errors import ApiError
from server.guidelines.models import Guideline, GuidelineVersion
from server.issues.models import Issue
from server.notifications.models import Notification
from server.operations.models import AuditEvent, ServiceStatus
from server.reviews.models import ReviewResult, CriterionEvaluation
from server.stores.models import Region, Store, Category, OFCStoreMapping
from server.submissions.models import Submission, AnalysisContext

pytestmark = pytest.mark.postgres


@pytest.fixture
def queued(postgres_db):
    db = postgres_db
    now = utcnow()
    region = Region(code='analysis-region', name='분석 테스트 지역')
    category = Category(code='analysis-category', name='분석 테스트 분류')
    owner = Account(login_id='owner', display_name='점주', role='store_owner', password_hash='test-only')
    operator = Account(login_id='operator', display_name='운영자', role='platform_operator', password_hash='test-only')
    db.add_all([region, category, owner, operator]); db.flush()
    store = Store(code='analysis-store', name='분석 테스트 매장', region_id=region.id, store_type='도심형')
    ofc = Account(login_id='ofc', display_name='담당자', role='ofc', region_id=region.id, password_hash='test-only')
    db.add_all([store, ofc]); db.flush()
    db.add(OFCStoreMapping(account_id=ofc.id, store_id=store.id, changed_by_id=operator.id, reason='테스트 배정'))
    submission = Submission(store_id=store.id, category_id=category.id, submitted_by_id=owner.id, question='앞줄 확인')
    guideline = Guideline(rule_key='facing', title='앞줄', level='HQ', scope_key='HQ', created_by_id=operator.id)
    db.add_all([submission, guideline]); db.flush()
    version = GuidelineVersion(guideline_id=guideline.id, version=1, text='상품 앞줄을 정렬한다.', change_reason='테스트', created_by_id=operator.id)
    db.add(version); db.flush()
    snapshot = {'question': submission.question, 'guidelines': [{'guideline_id':str(guideline.id), 'version_id':str(version.id), 'version':1, 'rule_key':'facing', 'level':'HQ', 'text':version.text}],
                'photos':[{'photo_id':str(uuid4()), 'position':1, 'mime_type':'image/png', 'sha256':'a'*64}], 'references':[], 'previous_review':None}
    digest = hashlib.sha256(json.dumps(snapshot,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    db.add(AnalysisContext(submission_id=submission.id, snapshot=snapshot, snapshot_sha256=digest))
    job = AnalysisJob(submission_id=submission.id, queued_at=now, queue_deadline_at=now+timedelta(seconds=180))
    db.add(job); db.commit()
    criterion = {k: snapshot['guidelines'][0][k] for k in ('guideline_id','version_id','version','rule_key')}
    criterion.update(verdict='unknown', reason='가림으로 판단할 수 없습니다.', evidence=[], actions=[])
    result = dict(schema_version='1.0',question_answer='다른 각도 사진이 필요합니다.',summary='판단할 수 없는 부분이 있습니다.',overall_confidence='low',criteria=[criterion],reference_comparisons=[],limitations=['Reference가 없습니다.'],ofc_review_required=True,follow_up_comparison=None)
    return SimpleNamespace(db=db, job_id=job.id, operator_id=operator.id, owner_id=owner.id, ofc_id=ofc.id, now=now, result=result, submission_id=submission.id)


def response(data, claim):
    return dict(schema_version='1.0',job_id=str(claim.job_id),attempt_id=str(claim.attempt_id),submission_id=str(claim.submission_id),result=data.result,model='test-contract-model',prompt_version='test-1',duration_ms=100,cli_version='test-double')


def count(db, model): return db.scalar(select(func.count()).select_from(model))


def test_two_workers_claim_once_without_waiting_on_other_jobs(queued):
    engine = queued.db.get_bind(); barrier = Barrier(2)
    def claim(worker):
        with Session(engine, expire_on_commit=False) as db:
            barrier.wait()
            return service.claim_next_job(db, worker, now=queued.now)
    with ThreadPoolExecutor(max_workers=2) as pool:
        claims = list(pool.map(claim, ['worker-a','worker-b']))
    assert sum(item is not None for item in claims) == 1
    queued.db.expire_all()
    assert count(queued.db, AnalysisAttempt) == 1
    job = queued.db.get(AnalysisJob, queued.job_id)
    attempt = queued.db.get(AnalysisAttempt, job.current_attempt_id)
    assert (job.status, attempt.status, attempt.attempt_number) == ('running','running',1)
    assert (attempt.deadline_at-attempt.started_at).total_seconds() == 130
    assert (attempt.lease_expires_at-attempt.started_at).total_seconds() == 140


def fail_claim(data):
    claim = service.claim_next_job(data.db,'worker-a',now=data.now)
    assert claim is not None
    assert service.fail_attempt(data.db,claim,'MODEL_EXECUTION_FAILED',now=data.now+timedelta(seconds=2))
    return claim


def test_retry_same_key_is_atomic_replay_and_preserves_old_attempt(queued):
    old = fail_claim(queued)
    engine = queued.db.get_bind(); barrier = Barrier(2)
    def retry(_):
        with Session(engine,expire_on_commit=False) as db:
            account = db.get(Account,queued.operator_id); barrier.wait()
            return service.retry_job(db,account,queued.job_id,'모델 연결 복구 후 재처리','same-retry-key-001',str(uuid4()))[1]
    with ThreadPoolExecutor(max_workers=2) as pool:
        replays = list(pool.map(retry,range(2)))
    assert sorted(replays) == [False,True]
    queued.db.expire_all()
    job = queued.db.get(AnalysisJob,queued.job_id)
    reserved = queued.db.get(AnalysisAttempt,job.current_attempt_id)
    assert (job.status,job.enqueue_generation,reserved.status,reserved.attempt_number) == ('queued',2,'queued',2)
    assert all(getattr(job,key) is None for key in ('started_at','finished_at','error_code','error_message'))
    assert queued.db.get(AnalysisAttempt,old.attempt_id).error_code == 'MODEL_EXECUTION_FAILED'
    assert count(queued.db,AuditEvent) == count(queued.db,IdempotencyRecord) == 1
    assert queued.db.scalar(select(IdempotencyRecord.operation)) == 'analysis.retry'
    next_claim = service.claim_next_job(queued.db,'worker-b')
    assert next_claim.attempt_id == reserved.id
    assert count(queued.db,AnalysisAttempt) == 2


def test_different_retry_keys_only_one_accepted(queued):
    fail_claim(queued)
    engine=queued.db.get_bind(); barrier=Barrier(2)
    def retry(index):
        with Session(engine,expire_on_commit=False) as db:
            account=db.get(Account,queued.operator_id); barrier.wait()
            try:
                service.retry_job(db,account,queued.job_id,'재처리',f'different-key-{index:03d}',str(uuid4()))
                return 'accepted'
            except ApiError as exc:
                db.rollback(); return exc.code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(retry,range(2))) == ['JOB_NOT_RETRYABLE','accepted']


def test_retry_target_hash_and_current_permission(queued):
    fail_claim(queued)
    db=queued.db; account=db.get(Account,queued.operator_id)
    service.retry_job(db,account,queued.job_id,'재처리','target-retry-key-001',str(uuid4()))
    with pytest.raises(ApiError) as caught:
        service.retry_job(db,account,uuid4(),'재처리','target-retry-key-001',str(uuid4()))
    assert caught.value.code == 'IDEMPOTENCY_CONFLICT'; db.rollback()
    account.is_active=False; db.commit()
    with pytest.raises(ApiError) as caught:
        service.retry_job(db,account,queued.job_id,'재처리','target-retry-key-001',str(uuid4()))
    assert caught.value.status_code == 403


def test_queue_timeout_creates_unstarted_expired_attempt_once(queued):
    assert service.sweep_expired(queued.db,now=queued.now+timedelta(seconds=181)) == 1
    assert service.sweep_expired(queued.db,now=queued.now+timedelta(seconds=182)) == 0
    job=queued.db.get(AnalysisJob,queued.job_id)
    attempt=queued.db.get(AnalysisAttempt,job.current_attempt_id)
    assert (job.status,attempt.status,job.error_code)==('failed','expired','QUEUE_TIMEOUT')
    assert attempt.started_at is None and attempt.worker_id is None
    assert count(queued.db,AnalysisAttempt)==1


def test_lease_recovery_and_old_result_cannot_touch_retry(queued):
    claim=service.claim_next_job(queued.db,'dead-worker',now=queued.now)
    assert claim is not None
    assert service.sweep_expired(queued.db,now=queued.now+timedelta(seconds=139))==0
    assert service.sweep_expired(queued.db,now=queued.now+timedelta(seconds=141))==1
    assert queued.db.get(AnalysisAttempt,claim.attempt_id).error_code=='WORKER_INTERRUPTED'
    account=queued.db.get(Account,queued.operator_id)
    service.retry_job(queued.db,account,queued.job_id,'작업자 복구','recover-retry-key-001',str(uuid4()))
    newer=service.claim_next_job(queued.db,'new-worker')
    assert not service.complete_attempt(queued.db,claim,response(queued,claim),now=queued.now+timedelta(seconds=142))
    assert not service.fail_attempt(queued.db,claim,'MODEL_TIMEOUT')
    assert queued.db.get(AnalysisJob,queued.job_id).current_attempt_id==newer.attempt_id
    assert queued.db.get(AnalysisAttempt,newer.attempt_id).status=='running'


def test_deadline_late_success_is_rejected_even_before_lease_expiry(queued):
    claim=service.claim_next_job(queued.db,'worker',now=queued.now)
    assert claim is not None
    assert not service.complete_attempt(queued.db,claim,response(queued,claim),now=queued.now+timedelta(seconds=131))
    assert count(queued.db,ReviewResult)==0


def test_success_saves_review_criterion_issue_notifications_once(queued):
    claim=service.claim_next_job(queued.db,'worker',now=queued.now)
    assert claim is not None
    outcome=response(queued,claim)
    assert service.complete_attempt(queued.db,claim,outcome,now=queued.now+timedelta(seconds=1))
    assert not service.complete_attempt(queued.db,claim,outcome,now=queued.now+timedelta(seconds=2))
    assert not service.fail_attempt(queued.db,claim,'MODEL_TIMEOUT')
    assert count(queued.db,ReviewResult)==count(queued.db,CriterionEvaluation)==count(queued.db,Issue)==1
    assert count(queued.db,Notification)==2
    review=queued.db.scalar(select(ReviewResult))
    assert review.source_kind=='real_ai' and review.compliance_rate is None and review.assessable_rate==0
    assert queued.db.get(AnalysisAttempt,claim.attempt_id).result_applied
    assert queued.db.get(AnalysisJob,claim.job_id).status=='succeeded'
    model=queued.db.scalar(select(ServiceStatus).where(ServiceStatus.service_name=='model'))
    assert model.last_success_at is not None
    with pytest.raises(ApiError) as caught:
        service.retry_job(queued.db,queued.db.get(Account,queued.operator_id),queued.job_id,'성공 덮어쓰기','success-retry-key-001',str(uuid4()))
    assert caught.value.code=='JOB_NOT_RETRYABLE'


def test_success_transaction_rolls_back_when_follow_up_fails(queued,monkeypatch):
    claim=service.claim_next_job(queued.db,'worker',now=queued.now)
    assert claim is not None
    def fail(*args): raise RuntimeError('테스트 후처리 장애')
    monkeypatch.setattr(service,'on_review_ready',fail)
    with pytest.raises(RuntimeError):
        service.complete_attempt(queued.db,claim,response(queued,claim),now=queued.now+timedelta(seconds=1))
    for model in (ReviewResult,CriterionEvaluation,Issue,Notification): assert count(queued.db,model)==0
    assert queued.db.get(AnalysisJob,claim.job_id).status=='running'
    assert not queued.db.get(AnalysisAttempt,claim.attempt_id).result_applied


def test_result_validation_and_identity_are_rechecked_before_storage(queued):
    from packages.review_contract.errors import ContractError
    claim=service.claim_next_job(queued.db,'worker',now=queued.now)
    assert claim is not None
    for mutation in ('wrong_attempt','missing_criterion','mock_source'):
        outcome=copy.deepcopy(response(queued,claim))
        if mutation=='wrong_attempt': outcome['attempt_id']=str(uuid4())
        elif mutation=='missing_criterion': outcome['result']['criteria']=[]
        else: outcome['source_kind']='mock'
        with pytest.raises(ContractError):
            service.complete_attempt(queued.db,claim,outcome,now=queued.now+timedelta(seconds=1))
        assert count(queued.db,ReviewResult)==0


def test_heartbeat_updates_presence_without_extending_absolute_lease(queued):
    claim=service.claim_next_job(queued.db,'worker',now=queued.now)
    assert claim is not None
    assert service.heartbeat(queued.db,'worker',claim,now=queued.now+timedelta(seconds=10))
    attempt=queued.db.get(AnalysisAttempt,claim.attempt_id)
    assert attempt.heartbeat_at==queued.now+timedelta(seconds=10)
    assert attempt.lease_expires_at==queued.now+timedelta(seconds=140)
    assert queued.db.scalar(select(ServiceStatus).where(ServiceStatus.service_name=='worker')).status=='up'


@pytest.fixture
def stored_images(queued,tmp_path,monkeypatch,request):
    from io import BytesIO
    from PIL import Image
    from server.core.config import get_settings
    from server.submissions.models import MediaAsset,SubmissionPhoto
    from server.guidelines.models import ReferencePhoto
    root=tmp_path/'media';root.mkdir()
    monkeypatch.setattr(get_settings(),'media_root',root)
    db=queued.db
    context=db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id==queued.submission_id))
    snapshot=copy.deepcopy(context.snapshot)
    raws=[]
    for position,color in enumerate(('white','gray'),1):
        if request.node.get_closest_marker('real_ai'):
            from server.core.config import PROJECT_ROOT
            name='beverage-before-01.png' if position==1 else 'beverage-reference-01.png'
            raw=(PROJECT_ROOT/'scripts/seed/assets/shelves'/name).read_bytes()
        else:
            buf=BytesIO();Image.new('RGB',(40,40),color).save(buf,format='PNG');raw=buf.getvalue()
        raws.append(raw)
        with Image.open(BytesIO(raw)) as decoded: width,height=decoded.size
        ident=uuid4();key=f'{ident}.png';(root/key).write_bytes(raw)
        media=MediaAsset(
            id=ident,
            storage_key=key,
            thumbnail_key=f'{ident}-thumbnail.jpg',
            sha256=hashlib.sha256(raw).hexdigest(),
            mime_type='image/png',
            byte_size=len(raw),
            width=width, height=height,
            uploaded_by_id=queued.owner_id,
            source_kind='ai_generated_demo' if request.node.get_closest_marker('real_ai') else 'seed_demo',
        )
        db.add(media);db.flush()
        if position==1:
            photo=SubmissionPhoto(id=uuid4(),submission_id=queued.submission_id,media_id=media.id,position=1)
            db.add(photo)
            snapshot['photos']=[dict(photo_id=str(photo.id),media_id=str(media.id),position=1,mime_type='image/png',sha256=media.sha256)]
        else:
            submission=db.get(Submission,queued.submission_id)
            ref=ReferencePhoto(id=uuid4(),lineage_id=uuid4(),photo_id=media.id,category_id=submission.category_id,caption='테스트 Reference',created_by_id=queued.operator_id)
            db.add(ref)
            snapshot['references']=[dict(reference_id=str(ref.id),photo_id=str(media.id),position=1,mime_type='image/png',sha256=media.sha256,caption=ref.caption)]
            queued.result['reference_comparisons']=[dict(reference_id=str(ref.id),verdict='unknown',photo_positions=[],observation='가림으로 비교할 수 없습니다.')]
    context.snapshot=snapshot
    context.snapshot_sha256=hashlib.sha256(json.dumps(snapshot,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    db.commit()
    return raws


def test_load_request_keeps_frozen_reference_and_checks_original_bytes(queued,stored_images,tmp_path):
    from server.analysis_jobs.worker import load_request
    from server.core.config import get_settings
    claim=service.claim_next_job(queued.db,'worker')
    prepared=load_request(queued.db,claim)
    assert prepared.photos==(stored_images[0],) and prepared.references==(stored_images[1],)
    assert prepared.context.question=='앞줄 확인'
    assert prepared.context.guidelines[0].rule_key=='facing'
    from packages.review_contract.errors import ContractError
    path=next(get_settings().media_root.glob('*.png'));path.write_bytes(b'changed')
    with pytest.raises(ContractError) as caught: load_request(queued.db,claim)
    assert caught.value.code=='INVALID_IMAGE'


@pytest.mark.asyncio
async def test_worker_has_no_db_locks_while_network_pending_and_saves_success(queued,stored_images,monkeypatch):
    import asyncio
    from server.analysis_jobs.worker import process_claim
    from server.core.config import get_settings
    from sqlalchemy.orm import sessionmaker
    settings=get_settings();monkeypatch.setattr(settings,'heartbeat_interval_seconds',0.02)
    factory=sessionmaker(bind=queued.db.get_bind(),expire_on_commit=False)
    claim=service.claim_next_job(queued.db,'worker')
    async def analyzer(prepared,settings):
        with factory() as other:
            job=other.scalar(select(AnalysisJob).where(AnalysisJob.id==claim.job_id).with_for_update(nowait=True))
            assert job.status=='running'
            other.rollback()
        assert prepared.photos==(stored_images[0],) and prepared.references==(stored_images[1],)
        await asyncio.sleep(0.08)
        return response(queued,claim)
    assert await process_claim(claim,session_factory=factory,settings=settings,analyzer=analyzer)
    queued.db.expire_all()
    assert queued.db.get(AnalysisJob,claim.job_id).status=='succeeded'
    assert count(queued.db,ReviewResult)==1
    assert queued.db.get(AnalysisAttempt,claim.attempt_id).heartbeat_at>claim.deadline_at-timedelta(seconds=130)


@pytest.mark.asyncio
async def test_worker_cancellation_recovers_through_lease_without_success(queued,stored_images):
    import asyncio
    from server.analysis_jobs.worker import process_claim
    from sqlalchemy.orm import sessionmaker
    factory=sessionmaker(bind=queued.db.get_bind(),expire_on_commit=False)
    claim=service.claim_next_job(queued.db,'worker')
    started=asyncio.Event();cancelled=asyncio.Event()
    async def analyzer(*args):
        started.set()
        try: await asyncio.sleep(30)
        finally: cancelled.set()
    task=asyncio.create_task(process_claim(claim,session_factory=factory,analyzer=analyzer))
    await started.wait();task.cancel()
    with pytest.raises(asyncio.CancelledError): await task
    assert cancelled.is_set()
    queued.db.expire_all()
    assert queued.db.get(AnalysisAttempt,claim.attempt_id).status=='running'
    assert service.sweep_expired(queued.db,now=claim.lease_expires_at+timedelta(seconds=1))==1
    assert queued.db.get(AnalysisAttempt,claim.attempt_id).error_code=='WORKER_INTERRUPTED'
    assert count(queued.db,ReviewResult)==0


@pytest.mark.asyncio
async def test_worker_failure_stores_safe_code_not_remote_message(queued,stored_images):
    from packages.review_contract.errors import ContractError
    from server.analysis_jobs.worker import process_claim
    from sqlalchemy.orm import sessionmaker
    factory=sessionmaker(bind=queued.db.get_bind(),expire_on_commit=False)
    claim=service.claim_next_job(queued.db,'worker')
    async def analyzer(*args): raise ContractError('MODEL_TIMEOUT','private-remote-body')
    assert not await process_claim(claim,session_factory=factory,analyzer=analyzer)
    queued.db.expire_all()
    attempt=queued.db.get(AnalysisAttempt,claim.attempt_id)
    assert attempt.status=='expired' and attempt.error_message==service.ERROR_MESSAGES['MODEL_TIMEOUT']
    assert count(queued.db,ReviewResult)==0


@pytest.mark.real_ai
@pytest.mark.asyncio
async def test_real_worker_generated_images_to_postgres(queued,stored_images):
    """명시적 환경 플래그에서만 실제 인증 모델을 호출한다. 결과를 Mock으로 대체하지 않는다."""
    import os
    if os.environ.get('STORELOOP_RUN_REAL_AI')!='1':
        pytest.skip('실제 모델 검증은 STORELOOP_RUN_REAL_AI=1에서 명시적으로 실행합니다.')
    import time
    from server.analysis_jobs.worker import process_claim
    from server.core.config import PROJECT_ROOT
    from sqlalchemy.orm import sessionmaker
    factory=sessionmaker(bind=queued.db.get_bind(),expire_on_commit=False)
    claim=service.claim_next_job(queued.db,'real-ai-acceptance')
    started=time.monotonic()
    applied=await process_claim(claim,session_factory=factory)
    elapsed=round((time.monotonic()-started)*1000)
    queued.db.expire_all()
    review=queued.db.scalar(select(ReviewResult))
    attempt=queued.db.get(AnalysisAttempt,claim.attempt_id)
    report=dict(status='PASS' if applied else 'FAIL',source_kind='real_ai',image_source_kind='ai_generated_demo',
                tested_at=utcnow().isoformat(),job_id=str(claim.job_id),attempt_id=str(claim.attempt_id),
                worker_elapsed_ms=elapsed,target_30_seconds_met=elapsed<=30000,attempt_status=attempt.status,
                error_code=attempt.error_code,result_applied=attempt.result_applied,
                photo_sha256=hashlib.sha256(stored_images[0]).hexdigest(),reference_sha256=hashlib.sha256(stored_images[1]).hexdigest(),
                review_count=count(queued.db,ReviewResult),criterion_count=count(queued.db,CriterionEvaluation),
                issue_count=count(queued.db,Issue),notification_count=count(queued.db,Notification),
                model_name=review.model_name if review else None,model_latency_ms=review.latency_ms if review else None,
                compliance_rate=float(review.compliance_rate) if review and review.compliance_rate is not None else None,
                assessable_rate=float(review.assessable_rate) if review and review.assessable_rate is not None else None,
                question_answer=review.result['question_answer'] if review else None,
                evidence=review.result['criteria'][0]['evidence'] if review else None,
                reference_comparison=review.result['reference_comparisons'] if review else None,
                database='전용 테스트 schema, 종료 후 삭제',schema_and_reference_validation='PASS' if applied else 'FAIL')
    path=PROJECT_ROOT/'execute/workHitory/analysis-jobs/evidence/real-worker-001.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    assert applied, f'실제 worker 분석 실패: {attempt.error_code}'
    assert review.source_kind=='real_ai' and attempt.result_applied
    assert count(queued.db,ReviewResult)==count(queued.db,CriterionEvaluation)==1
    assert count(queued.db,Notification)>=1


def test_locked_oldest_job_is_skipped_for_another_queued_job(queued):
    from sqlalchemy import text
    db=queued.db
    original=db.get(Submission,queued.submission_id)
    second=Submission(store_id=original.store_id,category_id=original.category_id,submitted_by_id=original.submitted_by_id,question='다음 작업')
    db.add(second);db.flush()
    second_job=AnalysisJob(submission_id=second.id,queued_at=queued.now+timedelta(seconds=1),queue_deadline_at=queued.now+timedelta(seconds=180))
    db.add(second_job);db.commit()
    db.scalar(select(AnalysisJob).where(AnalysisJob.id==queued.job_id).with_for_update())
    with Session(db.get_bind(),expire_on_commit=False) as other:
        other.execute(text("SET LOCAL statement_timeout = '1s'"))
        claim=service.claim_next_job(other,'unblocked-worker',now=queued.now+timedelta(seconds=2))
    assert claim is not None and claim.job_id==second_job.id
    db.rollback()


def test_duplicate_completion_race_applies_one_result(queued):
    claim=service.claim_next_job(queued.db,'worker',now=queued.now)
    engine=queued.db.get_bind();barrier=Barrier(2);outcome=response(queued,claim)
    def complete(_):
        with Session(engine,expire_on_commit=False) as db:
            barrier.wait()
            return service.complete_attempt(db,claim,outcome,now=queued.now+timedelta(seconds=1))
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(complete,range(2)))==[False,True]
    queued.db.expire_all()
    assert count(queued.db,ReviewResult)==count(queued.db,Issue)==1
    assert count(queued.db,Notification)==2


def test_deadline_crossed_during_atomic_follow_up_rolls_back_everything(queued,monkeypatch):
    claim=service.claim_next_job(queued.db,'worker',now=queued.now)
    moments=iter([queued.now+timedelta(seconds=1),queued.now+timedelta(seconds=131)])
    monkeypatch.setattr(service,'utcnow',lambda:next(moments))
    assert not service.complete_attempt(queued.db,claim,response(queued,claim))
    for model in (ReviewResult,CriterionEvaluation,Issue,Notification):
        assert count(queued.db,model)==0
    assert queued.db.get(AnalysisJob,claim.job_id).status=='running'


def test_queue_expiry_reuses_retry_reservation(queued):
    fail_claim(queued)
    account=queued.db.get(Account,queued.operator_id)
    job,_=service.retry_job(queued.db,account,queued.job_id,'복구 확인','expired-reserve-key',str(uuid4()))
    reserved_id=job.current_attempt_id
    assert service.sweep_expired(queued.db,now=job.queue_deadline_at+timedelta(seconds=1))==1
    assert count(queued.db,AnalysisAttempt)==2
    assert queued.db.get(AnalysisAttempt,reserved_id).status=='expired'
    assert queued.db.get(AnalysisAttempt,reserved_id).started_at is None
