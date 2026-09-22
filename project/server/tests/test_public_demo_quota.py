"""공개 시연 신규 요청 quota의 전역 한도·롤백·경쟁 검증."""
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import select
from sqlalchemy.orm import Session
import pytest
from server.analysis_jobs.quota import consume_public_analysis
from server.analysis_jobs.models import DailyAnalysisUsage
from server.core.config import get_settings
from server.core.errors import ApiError
from server.core.db import utcnow

@pytest.fixture
def public_mode(monkeypatch):
    monkeypatch.setattr(get_settings(),'demo_public_access_enabled',True)

def test_daily_limit_and_transaction_rollback(db,public_mode):
    consume_public_analysis(db);db.rollback()
    assert db.scalar(select(DailyAnalysisUsage)) is None
    for _ in range(20):
        consume_public_analysis(db);db.commit()
    with pytest.raises(ApiError) as error:
        consume_public_analysis(db)
    assert error.value.status_code==429
    db.rollback()
    assert db.scalar(select(DailyAnalysisUsage.used))==20

def test_public_optout_does_not_consume(db):
    consume_public_analysis(db);db.commit()
    assert db.scalar(select(DailyAnalysisUsage)) is None

def test_daily_limit_is_atomic_across_sessions(db,public_mode):
    engine=db.get_bind()
    def consume(_):
        with Session(engine) as session:
            try:
                consume_public_analysis(session);session.commit();return True
            except ApiError:
                session.rollback();return False
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(consume,range(24)))
    assert sum(results)==20
    assert db.scalar(select(DailyAnalysisUsage.used))==20

def test_retry_idempotency_does_not_double_consume(db,public_mode,account_factory,store_factory):
    from datetime import timedelta
    from uuid import uuid4
    from server.stores.models import Category
    from server.submissions.models import Submission
    from server.analysis_jobs.models import AnalysisJob
    from server.analysis_jobs.service import retry_job
    operator=account_factory(role='platform_operator')
    owner=account_factory()
    store=store_factory()
    category=Category(code='quota-retry',name='테스트')
    db.add(category);db.flush()
    submission=Submission(store_id=store.id,category_id=category.id,submitted_by_id=owner.id,question='테스트')
    db.add(submission);db.flush()
    job=AnalysisJob(submission_id=submission.id,status='failed',queued_at=utcnow(),queue_deadline_at=utcnow()+timedelta(seconds=180))
    db.add(job);db.commit()
    _,replayed=retry_job(db,operator,job.id,'테스트 재처리','retry-quota-key-001',str(uuid4()))
    assert replayed is False
    _,replayed=retry_job(db,operator,job.id,'테스트 재처리','retry-quota-key-001',str(uuid4()))
    assert replayed is True
    assert db.scalar(select(DailyAnalysisUsage.used))==1
