"""요청 실행의 작업 범위·소유권·권한·비활성화 경계. 유료 호출 없음."""
from datetime import timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import BackgroundTasks
from sqlalchemy.orm import sessionmaker

from packages.review_contract.errors import ContractError
from server.analysis_jobs import service
from server.analysis_jobs.models import AnalysisJob
from server.core.db import utcnow
from server.submissions.models import Submission
from server.vercel_runtime import schedule_analysis, process_job, analyze_in_process


def test_schedule_requires_explicit_mode(monkeypatch):
    tasks = BackgroundTasks()
    monkeypatch.delenv('VERCEL_REQUEST_ANALYSIS', raising=False)
    schedule_analysis(tasks, uuid4())
    assert tasks.tasks == []
    monkeypatch.setenv('VERCEL_REQUEST_ANALYSIS', 'true')
    ident = uuid4()
    schedule_analysis(tasks, ident)
    assert len(tasks.tasks) == 1 and tasks.tasks[0].args == (ident,)


@pytest.fixture
def queued(db, account_factory, store_factory):
    from server.stores.models import Category
    owner, store = account_factory(), store_factory()
    category = Category(code='request-tests', name='테스트')
    db.add(category); db.flush()
    jobs = []
    for _ in range(2):
        submission = Submission(store_id=store.id, category_id=category.id,
                                submitted_by_id=owner.id, question='테스트')
        db.add(submission); db.flush()
        job = AnalysisJob(submission_id=submission.id, queued_at=utcnow(),
                          queue_deadline_at=utcnow() + timedelta(seconds=180))
        db.add(job); db.flush(); jobs.append(job)
    db.commit()
    return jobs


def test_claim_only_authorized_target_and_no_duplicate(db, queued):
    first, target = queued
    claim = service.claim_next_job(db, 'request-test', job_id=target.id)
    assert claim.job_id == target.id
    assert db.get(AnalysisJob, first.id).status == 'queued'
    assert service.claim_next_job(db, 'duplicate', job_id=target.id) is None
    assert service.claim_next_job(db, 'missing', job_id=uuid4()) is None


def test_expiry_scoped_to_requested_job(db, queued):
    for job in queued:
        job.queue_deadline_at = utcnow() - timedelta(seconds=1)
    db.commit()
    assert service.sweep_expired(db, job_id=queued[1].id) == 1
    assert queued[0].status == 'queued' and queued[1].status == 'failed'


@pytest.mark.asyncio
async def test_process_single_claim_uses_existing_worker(db, queued, monkeypatch):
    from server import vercel_runtime
    monkeypatch.setenv('VERCEL_REQUEST_ANALYSIS', 'true')
    seen = []
    async def fake_process(claim, **kwargs):
        seen.append(claim.job_id)
        return True
    monkeypatch.setattr(vercel_runtime.worker, 'process_claim', fake_process)
    factory = sessionmaker(db.get_bind(), expire_on_commit=False)
    assert await process_job(queued[1].id, session_factory=factory)
    assert not await process_job(queued[1].id, session_factory=factory)
    assert seen == [queued[1].id]


@pytest.mark.asyncio
async def test_disabled_ai_never_invokes_model(monkeypatch):
    monkeypatch.setenv('AI_REQUESTS_ENABLED', 'false')
    with pytest.raises(ContractError) as error:
        await analyze_in_process(SimpleNamespace(), None)
    assert error.value.code == 'MODEL_EXECUTION_FAILED'


def test_anonymous_operator_status_does_not_schedule(client, monkeypatch):
    from server import vercel_runtime
    called = []
    monkeypatch.setattr(vercel_runtime, 'schedule_analysis', lambda *args: called.append(args))
    assert client.get('/api/operations/jobs/' + str(uuid4())).status_code == 401
    assert called == []


def test_business_account_operator_status_does_not_schedule(client, account_factory, login_as, monkeypatch):
    from server import vercel_runtime
    called = []
    login_as(account_factory())
    monkeypatch.setattr(vercel_runtime, 'schedule_analysis', lambda *args: called.append(args))
    assert client.get('/api/operations/jobs/' + str(uuid4())).status_code == 403
    assert called == []


def test_request_dashboard_has_no_external_ai_health_probe(db, monkeypatch):
    from server.operations import service as operations
    monkeypatch.setenv('VERCEL_REQUEST_ANALYSIS', 'true')
    monkeypatch.setenv('AI_REQUESTS_ENABLED', 'false')
    def forbidden(*args, **kwargs):
        raise AssertionError('request mode must not contact a separate AI host')
    monkeypatch.setattr(operations.httpx, 'get', forbidden)
    result = operations.service_dashboard(db)
    states = {item['name']: item['status'] for item in result['services']}
    assert states['worker'] == 'up' and states['ai'] == 'down'
    assert result['model']['readiness'] == 'unknown'
