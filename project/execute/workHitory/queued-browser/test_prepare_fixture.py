"""실제 DB 없이 fixture 도구의 안전 경계와 추가 전용 계획을 검증한다."""
from datetime import datetime, timezone, timedelta
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import pytest

spec = importlib.util.spec_from_file_location('queued_fixture', Path(__file__).with_name('prepare_fixture.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_only_dedicated_local_test_database_is_allowed():
    module.validate_url('postgresql+psycopg://u:p@127.0.0.1:55432/storeloop_test')
    for value in ('postgresql://u:p@example.com:55432/storeloop_test', 'postgresql://u:p@127.0.0.1:5432/storeloop_test',
                  'postgresql://u:p@127.0.0.1:55432/storeloop', 'sqlite:///:memory:',
                  'postgresql://u:p@127.0.0.1:55432/storeloop_test?host=other'):
        with pytest.raises(module.FixtureConflict):
            module.validate_url(value)


def test_worker_scan_catches_both_production_and_browser_entry_without_exposing_command():
    sample = ' 17 /python /project/scripts/worker_entry.py\n 18 /python -m server.analysis_jobs.worker\n 19 /python -m uvicorn server.main:app\n'
    assert module.worker_pids(sample) == [17, 18]
    with pytest.raises(module.FixtureConflict):
        module.require_stopped(lambda: [17])
    module.require_stopped(lambda: [])


def test_plan_is_expired_insert_only_mock_and_preserves_original_snapshot(monkeypatch):
    now = datetime(2026, 9, 21, 14, tzinfo=timezone.utc)
    sources = SimpleNamespace(owner=SimpleNamespace(id=module.OWNER_ID), store=SimpleNamespace(id=module.STORE_ID),
                              category=SimpleNamespace(id=module.CATEGORY_ID), operator=SimpleNamespace(id=module.OPERATOR_ID),
                              media=SimpleNamespace(id=module.MEDIA_ID, sha256=module.MEDIA_SHA256, mime_type='image/png'))
    def snapshot(db, store, category, question, photos, previous):
        return {'question': question, 'photos': photos, 'previous_review': previous, 'guidelines': [],
                'candidate_guidelines': [], 'references': [], 'store': {'id': str(store.id)}, 'category': {'id': str(category.id)}}
    historical_calls = []
    monkeypatch.setattr(module, 'make_snapshot', snapshot)
    monkeypatch.setattr(module, 'historical_versions', lambda db, value, when: historical_calls.append(when) or value)
    rows = module.build_rows(None, sources, now)
    sub, photo, context, job, audit = rows
    assert sub.source_kind == 'seed_demo' and sub.question.startswith('[Mock 장기 대기 UI 검수]')
    assert sub.parent_submission_id is None and job.is_fixture is True
    assert job.status == 'queued' and job.current_attempt_id is None
    assert job.queue_deadline_at <= now - timedelta(minutes=7)
    assert job.queued_at == job.created_at == sub.created_at == now - timedelta(minutes=10)
    assert historical_calls == [sub.created_at]
    assert context.snapshot_sha256 == module.digest(context.snapshot)
    assert context.snapshot['photos'][0]['photo_id'] == str(photo.id)
    assert photo.media_id == module.MEDIA_ID
    assert audit.after_data['is_fixture'] is True
    assert {row.__tablename__ for row in rows} == {'submissions', 'submission_photos', 'analysis_contexts', 'analysis_jobs', 'audit_events'}


def test_existing_success_is_returned_without_reset_and_changed_context_is_rejected(monkeypatch):
    now = datetime(2026, 9, 21, 14, tzinfo=timezone.utc)
    sub = SimpleNamespace(id=module.IDS['submission'], source_kind='seed_demo', question=module.QUESTION,
                          submitted_by_id=module.OWNER_ID, store_id=module.STORE_ID, category_id=module.CATEGORY_ID, parent_submission_id=None)
    photo = SimpleNamespace(id=module.IDS['photo'], submission_id=sub.id, media_id=module.MEDIA_ID, position=1)
    context = SimpleNamespace(id=module.IDS['context'], submission_id=sub.id, snapshot={'question': module.QUESTION}, snapshot_sha256=module.digest({'question': module.QUESTION}))
    job = SimpleNamespace(id=module.IDS['job'], submission_id=sub.id, is_fixture=True, status='succeeded', queued_at=now, queue_deadline_at=now)
    audit = SimpleNamespace(id=module.IDS['audit'], target_id=sub.id, action='qa.queued_fixture.create',
                            after_data={'fixture_version': module.VERSION, 'snapshot_sha256': context.snapshot_sha256})
    monkeypatch.setattr(module, 'lookup_rows', lambda db: [sub, photo, context, job, audit])
    assert module.existing_fixture(None)[3].status == 'succeeded'
    assert job.status == 'succeeded'
    context.snapshot_sha256 = '0' * 64
    with pytest.raises(module.FixtureConflict):
        module.existing_fixture(None)


def test_partial_namespace_collision_is_rejected(monkeypatch):
    monkeypatch.setattr(module, 'lookup_rows', lambda db: [SimpleNamespace(), None, None, None, None])
    with pytest.raises(module.FixtureConflict):
        module.existing_fixture(None)


def test_sql_guard_rejects_existing_record_mutation_and_ddl():
    for command in ('UPDATE analysis_jobs SET status=\'queued\'', 'DELETE FROM submissions', 'TRUNCATE submissions', 'DROP TABLE submissions'):
        with pytest.raises(module.FixtureConflict):
            module.prohibit_existing_mutation(None, None, command, None, None, False)
    for command in ('SELECT 1', 'INSERT INTO submissions (id) VALUES (:id)'):
        module.prohibit_existing_mutation(None, None, command, None, None, False)


def test_ack_is_required_before_database_connection(monkeypatch):
    monkeypatch.setattr(module.sys, 'argv', ['prepare_fixture.py', '--apply'])
    monkeypatch.setattr(module, 'create_engine', lambda *args, **kwargs: pytest.fail('DB 연결 전에 거부해야 한다'))
    with pytest.raises(module.FixtureConflict, match='EXPLICIT_WORKER_STOP_ACK_REQUIRED'):
        module.main()
