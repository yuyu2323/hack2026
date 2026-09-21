"""장기 대기 UI용 합성 기록을 추가한다. 기본은 읽기 전용 dry-run이다."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from uuid import UUID, uuid5

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from dotenv import dotenv_values
from sqlalchemy import create_engine, event, select, func, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from server.core.models import (Account, Store, Category, MediaAsset, StoreOwnerMapping, Submission,
                                SubmissionPhoto, AnalysisContext, AnalysisJob, AuditEvent)
from server.seed.__main__ import ident, historical_versions
from server.submissions.service import make_snapshot

NAMESPACE = UUID('6436567c-4d97-48c0-9858-aa70aee3f6ee')
VERSION = 'queued-browser-20260921-v1'
IDS = {name: uuid5(NAMESPACE, VERSION + ':' + name) for name in ('submission', 'photo', 'context', 'job', 'audit')}
OWNER_ID = ident('accounts', 'owner.north')
OPERATOR_ID = ident('accounts', 'operator.demo')
STORE_ID = ident('stores', 'spring-station')
CATEGORY_ID = ident('categories', 'beverage')
MEDIA_ID = ident('media_assets', 'beverage-uncertain-01')
MEDIA_SHA256 = '9723404dbd7ca09170f2a2253736518bbcb260f45b5b3ee389dafddf057433a6'
QUESTION = '[Mock 장기 대기 UI 검수] 합성 대기 기록입니다. 실제 새 제출이나 AI 분석 결과가 아닙니다. worker 재시작 후 대기 시간 초과로 종료됩니다.'
MODELS = (Submission, SubmissionPhoto, AnalysisContext, AnalysisJob, AuditEvent)


class FixtureConflict(ValueError):
    """비밀·영업 본문을 포함하지 않는 안전한 중단 코드."""


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def validate_url(value):
    url = make_url(value)
    if (url.drivername not in ('postgresql', 'postgresql+psycopg') or url.host not in ('127.0.0.1', 'localhost')
            or url.port != 55432 or url.database != 'storeloop_test' or url.query):
        raise FixtureConflict('DEDICATED_TEST_DATABASE_REQUIRED')
    return url


def worker_pids(output):
    found = []
    for line in output.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) != 2 or not parts[0].isdigit():
            continue
        if 'worker_entry.py' in parts[1] or 'server.analysis_jobs.worker' in parts[1]:
            found.append(int(parts[0]))
    return found


def scan_workers():
    # 프로세스 argv는 메모리에서만 판별하고 로그에 남기지 않는다.
    result = subprocess.run(['ps', '-axo', 'pid=,command='], capture_output=True, text=True, timeout=5)
    if result.returncode != 0:
        raise FixtureConflict('WORKER_SCAN_UNAVAILABLE')
    return worker_pids(result.stdout)


def require_stopped(scan=scan_workers):
    if scan():
        raise FixtureConflict('WORKER_MUST_BE_STOPPED')


def lookup_rows(db):
    return [db.get(model, IDS[name]) for model, name in zip(MODELS, IDS)]


def existing_fixture(db):
    rows = lookup_rows(db)
    if not any(row is not None for row in rows):
        return None
    if any(row is None for row in rows):
        raise FixtureConflict('PARTIAL_NAMESPACE_COLLISION')
    sub, photo, context, job, audit = rows
    if (sub.source_kind != 'seed_demo' or sub.question != QUESTION or sub.submitted_by_id != OWNER_ID
            or sub.store_id != STORE_ID or sub.category_id != CATEGORY_ID or sub.parent_submission_id is not None
            or photo.submission_id != sub.id or photo.media_id != MEDIA_ID or photo.position != 1
            or context.submission_id != sub.id or context.snapshot_sha256 != digest(context.snapshot)
            or context.snapshot.get('question') != QUESTION
            or job.submission_id != sub.id or not job.is_fixture
            or audit.target_id != sub.id or audit.action != 'qa.queued_fixture.create'
            or audit.after_data.get('fixture_version') != VERSION
            or audit.after_data.get('snapshot_sha256') != context.snapshot_sha256):
        raise FixtureConflict('EXISTING_FIXTURE_CHANGED')
    # 성공·실패·진행 여부와 무관하게 기존 기록을 초기화하지 않는다.
    return rows


def read_sources(db):
    owner, operator = db.get(Account, OWNER_ID), db.get(Account, OPERATOR_ID)
    store, category, media = db.get(Store, STORE_ID), db.get(Category, CATEGORY_ID), db.get(MediaAsset, MEDIA_ID)
    if any(row is None for row in (owner, operator, store, category, media)):
        raise FixtureConflict('SEED_SOURCE_MISSING')
    if (owner.login_id != 'owner.north' or owner.role != 'store_owner' or not owner.is_active
            or operator.role != 'platform_operator' or not operator.is_active or not store.is_active or not category.is_active
            or media.source_kind != 'ai_generated_demo' or media.sha256 != MEDIA_SHA256):
        raise FixtureConflict('SEED_SOURCE_CHANGED')
    mapping = db.scalar(select(func.count()).select_from(StoreOwnerMapping).where(
        StoreOwnerMapping.account_id == owner.id, StoreOwnerMapping.store_id == store.id, StoreOwnerMapping.ended_at.is_(None)))
    if mapping != 1:
        raise FixtureConflict('CURRENT_OWNER_MAPPING_REQUIRED')
    # 새 사진 파일을 쓰지 않고 기존 시드 원본의 무결성만 확인한다.
    folder = (ROOT / '.local/test-media').resolve()
    path = (folder / media.storage_key).resolve()
    if not path.is_relative_to(folder) or not path.is_file():
        raise FixtureConflict('SEED_MEDIA_PATH_INVALID')
    if path.stat().st_size != media.byte_size or hashlib.sha256(path.read_bytes()).hexdigest() != MEDIA_SHA256:
        raise FixtureConflict('SEED_MEDIA_HASH_MISMATCH')
    return SimpleNamespace(owner=owner, operator=operator, store=store, category=category, media=media)


def build_rows(db, sources, now):
    when = now - timedelta(minutes=10)
    sub = Submission(id=IDS['submission'], store_id=STORE_ID, category_id=CATEGORY_ID, submitted_by_id=OWNER_ID,
                     question=QUESTION, source_kind='seed_demo', parent_submission_id=None, created_at=when)
    photo = SubmissionPhoto(id=IDS['photo'], submission_id=sub.id, media_id=MEDIA_ID, position=1)
    photos = [dict(photo_id=str(photo.id), media_id=str(MEDIA_ID), position=1, mime_type=sources.media.mime_type, sha256=MEDIA_SHA256)]
    snapshot = make_snapshot(db, sources.store, sources.category, QUESTION, photos, None)
    # 합성 대기 시각 이후에 만든 기준/Reference를 과거 snapshot에 넣지 않는다.
    historical_versions(db, snapshot, when)
    context = AnalysisContext(id=IDS['context'], submission_id=sub.id, schema_version='1.0',
                              snapshot=snapshot, snapshot_sha256=digest(snapshot), created_at=when)
    job = AnalysisJob(id=IDS['job'], submission_id=sub.id, status='queued', current_attempt_id=None, enqueue_generation=1,
                      queued_at=when, queue_deadline_at=when + timedelta(seconds=180), created_at=when,
                      updated_at=now, is_fixture=True)
    audit = AuditEvent(id=IDS['audit'], actor_id=OPERATOR_ID, action='qa.queued_fixture.create', target_type='submission',
                       target_id=sub.id, reason='Mock 장기 대기 UI 검수용 합성 기록 추가. 실제 AI 호출 없음.',
                       before_data={}, after_data={'fixture_version': VERSION, 'submission_id': str(sub.id), 'job_id': str(job.id),
                                                   'is_fixture': True, 'source_kind': 'seed_demo', 'snapshot_sha256': context.snapshot_sha256},
                       outcome='succeeded', request_id=uuid5(NAMESPACE, VERSION + ':request'), created_at=now)
    return [sub, photo, context, job, audit]


def prohibit_existing_mutation(conn, cursor, statement, parameters, context, executemany):
    # 작성 권한은 추가 전용이다. 실수로 기존 행 수정·삭제·DDL이 섞이면 전체 rollback한다.
    command = statement.lstrip().split(None, 1)[0].upper()
    if command not in ('SELECT', 'SHOW', 'SET', 'INSERT'):
        raise FixtureConflict('INSERT_ONLY_GUARD')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='새 합성 기록 5행을 추가한다. 기본 dry-run.')
    parser.add_argument('--worker-stopped', action='store_true', help='담당자가 worker 종료를 확인했음을 명시한다. 실제 프로세스도 재검사한다.')
    args = parser.parse_args()
    if args.apply and not args.worker_stopped:
        raise FixtureConflict('EXPLICIT_WORKER_STOP_ACK_REQUIRED')
    if args.apply:
        require_stopped()
    value = dotenv_values(ROOT / '.local/runtime.env').get('STORELOOP_TEST_DATABASE_URL')
    validate_url(value)
    options = '-c search_path=public -c statement_timeout=10000'
    if not args.apply:
        options += ' -c default_transaction_read_only=on'
    engine = create_engine(value, hide_parameters=True, connect_args={'options': options})
    event.listen(engine, 'before_cursor_execute', prohibit_existing_mutation)
    output = {'fixture_version': VERSION, 'database_alias': 'test', 'mode': 'apply' if args.apply else 'dry-run',
              'account': 'owner.north', 'ids': {key: str(value) for key, value in IDS.items()}, 'ai_calls': 0}
    with engine.connect().execution_options(isolation_level='SERIALIZABLE' if args.apply else 'REPEATABLE READ') as conn, conn.begin():
        if not args.apply:
            conn.exec_driver_sql('SET TRANSACTION READ ONLY')
        output['read_only'] = conn.exec_driver_sql('SHOW transaction_read_only').scalar() == 'on'
        if args.apply:
            # 동시 실행도 하나의 안정 ID 묶음만 추가한다.
            conn.execute(text('SELECT pg_advisory_xact_lock(20450921, 55001)'))
        with Session(bind=conn, autoflush=False) as db:
            rows = existing_fixture(db)
            if rows:
                output.update(status='existing-preserved', insert_count=0, current_status=rows[3].status)
            else:
                sources = read_sources(db)
                active = db.scalar(select(func.count()).select_from(AnalysisJob).where(AnalysisJob.status.in_(['queued', 'running'])))
                output['other_active_job_count'] = active
                if active and args.apply:
                    raise FixtureConflict('OTHER_ACTIVE_JOB_EXISTS')
                rows = build_rows(db, sources, datetime.now(timezone.utc))
                if args.apply:
                    require_stopped()
                    if db.dirty or db.deleted:
                        raise FixtureConflict('EXISTING_ROW_MUTATION')
                    db.add(rows[0]); db.flush()
                    db.add_all(rows[1:]); db.flush()
                output.update(status='created' if args.apply else 'ready', insert_count=5 if args.apply else 0, planned_insert_count=5)
            output.update(submission_source_kind=rows[0].source_kind, is_fixture=rows[3].is_fixture,
                          queued_at=rows[3].queued_at.isoformat(), queue_deadline_at=rows[3].queue_deadline_at.isoformat(),
                          snapshot_sha256=rows[2].snapshot_sha256,
                          expected_after_worker_restart='failed / QUEUE_TIMEOUT / attempt expired; 해당 fixture의 AI 호출 없음',
                          urls=[f'http://127.0.0.1:{port}/store-owner/submissions/{IDS["submission"]}' for port in range(5173, 5178)])
    engine.dispose()
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except FixtureConflict as exc:
        print(json.dumps({'status': 'refused', 'code': str(exc)}, ensure_ascii=False))
        raise SystemExit(2) from None
    except Exception:
        print(json.dumps({'status': 'failed', 'code': 'FIXTURE_OPERATION_FAILED'}, ensure_ascii=False))
        raise SystemExit(2) from None
