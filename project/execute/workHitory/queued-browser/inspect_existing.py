"""기존 queued 시드와 해당 계정/미디어의 메타데이터만 읽는다."""
from pathlib import Path
import json
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from dotenv import dotenv_values
from sqlalchemy import create_engine, select, func
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from server.core.models import Account, AnalysisJob, AnalysisAttempt, AnalysisContext, Submission, ReviewResult, Store, Category, StoreOwnerMapping, MediaAsset
from server.seed.__main__ import ident


def main():
    url = dotenv_values(ROOT / '.local/runtime.env').get('STORELOOP_TEST_DATABASE_URL')
    parsed = make_url(url)
    if parsed.host not in ('127.0.0.1', 'localhost') or parsed.port != 55432 or parsed.database != 'storeloop_test':
        raise ValueError('대상 DB 불일치')
    engine = create_engine(url, hide_parameters=True, connect_args={'options': '-c default_transaction_read_only=on -c statement_timeout=10000'})
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'database_alias': 'test', 'scope': 'READ ONLY / 비밀·본문 출력 없음'}
    with engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn, conn.begin():
        conn.exec_driver_sql('SET TRANSACTION READ ONLY')
        report['read_only'] = conn.exec_driver_sql('SHOW transaction_read_only').scalar() == 'on'
        with Session(bind=conn, autoflush=False) as db:
            sub = db.get(Submission, ident('submissions', 'boundary-pending'))
            job = db.scalar(select(AnalysisJob).where(AnalysisJob.submission_id == sub.id)) if sub else None
            report['existing_boundary'] = None if not job else {
                'submission_id': str(sub.id), 'job_id': str(job.id), 'status': job.status, 'error_code': job.error_code,
                'is_fixture': job.is_fixture, 'source_kind': sub.source_kind,
                'queued_at': job.queued_at.isoformat(), 'queue_deadline_at': job.queue_deadline_at.isoformat(),
                'attempt_count': db.scalar(select(func.count()).select_from(AnalysisAttempt).where(AnalysisAttempt.job_id == job.id)),
                'review_count': db.scalar(select(func.count()).select_from(ReviewResult).where(ReviewResult.submission_id == sub.id)),
                'snapshot_sha256': db.scalar(select(AnalysisContext.snapshot_sha256).where(AnalysisContext.submission_id == sub.id)),
            }
            report['queued_jobs'] = [{'job_id': str(j.id), 'submission_id': str(j.submission_id), 'is_fixture': j.is_fixture,
                                      'queue_deadline_at': j.queue_deadline_at.isoformat()} for j in db.scalars(select(AnalysisJob).where(AnalysisJob.status == 'queued'))]
            owner = db.get(Account, ident('accounts', 'owner.north'))
            store = db.get(Store, ident('stores', 'spring-station'))
            category = db.get(Category, ident('categories', 'beverage'))
            media = db.get(MediaAsset, ident('media_assets', 'beverage-uncertain-01'))
            report['candidate_source'] = {'account_login': owner.login_id, 'account_id': str(owner.id), 'role': owner.role,
                'account_active': owner.is_active, 'store_id': str(store.id), 'store_active': store.is_active,
                'category_id': str(category.id), 'category_active': category.is_active,
                'current_owner_mapping': db.scalar(select(func.count()).select_from(StoreOwnerMapping).where(
                    StoreOwnerMapping.account_id == owner.id, StoreOwnerMapping.store_id == store.id, StoreOwnerMapping.ended_at.is_(None))) == 1,
                'media_id': str(media.id), 'media_source_kind': media.source_kind, 'media_sha256': media.sha256}
    engine.dispose()
    path = ROOT / 'execute/workHitory/queued-browser/existing-metadata.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    path.chmod(0o600)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        raise SystemExit('READ_ONLY_INSPECTION_FAILED: 연결·시드 대상 확인 필요. 민감 오류 원문은 출력하지 않았습니다.') from None
