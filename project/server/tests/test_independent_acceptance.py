"""다른 작성자의 영업 API·시드를 독립 PostgreSQL 스키마에서 검증한다."""
from datetime import timedelta
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import UUID, uuid4
import hashlib
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session
from PIL import Image

from server.core.config import get_settings
from server.core.db import get_db, as_utc, utcnow
from server.core.models import (
    Account, Region, Store, Category, StoreOwnerMapping, Submission,
    AnalysisContext, AnalysisJob, AnalysisAttempt, Guideline, GuidelineVersion, ReviewResult, Issue, Notification,
    SalesMock, MediaAsset, ReferencePhoto,
)
from server.core.security import hash_password

pytestmark = pytest.mark.postgres
TEST_PASSWORD = 'independent-synthetic-test-password'


@pytest.fixture
def isolated_business(postgres_db, monkeypatch):
    from server.main import app
    db = postgres_db
    region = Region(code='independent-region', name='독립 검증 지역')
    db.add(region); db.flush()
    store = Store(code='independent-store', name='독립 검증 매장', region_id=region.id,
                  store_type='도심형', address='')
    category = Category(code='independent-category', name='검증 상품군', description='')
    owner = Account(login_id='independent.owner', display_name='검증 점주', role='store_owner',
                    password_hash=hash_password(TEST_PASSWORD))
    hq = Account(login_id='independent.hq', display_name='검증 본사', role='hq',
                 password_hash=hash_password(TEST_PASSWORD))
    operator = Account(login_id='independent.operator', display_name='검증 운영자', role='platform_operator',
                       password_hash=hash_password(TEST_PASSWORD))
    db.add_all([store, category, owner, hq, operator]); db.flush()
    mapping = StoreOwnerMapping(account_id=owner.id, store_id=store.id, changed_by_id=operator.id,
                                reason='독립 검증용 현재 매핑')
    submission = Submission(store_id=store.id, category_id=category.id, submitted_by_id=owner.id,
                            question='검증 질문')
    db.add_all([mapping, submission]); db.flush()
    db.add(AnalysisJob(submission_id=submission.id, status='queued', queued_at=utcnow(),
                       queue_deadline_at=utcnow()+timedelta(seconds=180)))
    issue = Issue(submission_id=submission.id, type='owner_question', status='resolved', priority='normal',
                  title='독립 검증 문의', description='검증용 문의', created_by_id=owner.id,
                  resolution='진열 조정을 확인했습니다.', resolved_at=utcnow()-timedelta(hours=1))
    db.add(issue); db.flush()
    notification = Notification(recipient_id=owner.id, kind='issue_updated', submission_id=submission.id,
                                issue_id=issue.id, title='독립 검증 알림', dedupe_key='independent:'+str(uuid4()))
    db.add(notification); db.commit()
    previous = app.dependency_overrides.copy()
    def override_db():
        yield db
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(get_settings(), 'allowed_origins_value', 'http://testserver')
    monkeypatch.setattr(get_settings(), 'session_cookie_secure', False)
    try:
        with TestClient(app) as client:
            def login(account):
                csrf = client.get('/api/auth/csrf').json()['csrf_token']
                response = client.post('/api/auth/login', json={'login_id':account.login_id, 'password':TEST_PASSWORD},
                                       headers={'Origin':'http://testserver', 'X-CSRF-Token':csrf})
                assert response.status_code == 200
                return {'Origin':'http://testserver', 'X-CSRF-Token':response.json()['csrf_token']}
            yield db, client, login, owner, hq, operator, mapping, issue, notification
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@pytest.mark.parametrize('explicit_status', [False, True])
def test_resolved_issue_cannot_clear_resolution(isolated_business, explicit_status):
    db, client, login, owner, hq, operator, mapping, issue, notification = isolated_business
    headers = login(hq)
    before = issue.resolution
    body = {'version':issue.version, 'resolution':None}
    if explicit_status:
        body['status'] = 'resolved'
    response = client.patch('/api/issues/'+str(issue.id), json=body, headers=headers)
    assert response.status_code == 422, '해결 상태에서 조치 내용 제거를 거부해야 합니다.'
    db.refresh(issue)
    assert issue.status == 'resolved' and issue.resolution == before


def test_notification_inbox_rechecks_mapping_and_operator_role(isolated_business):
    db, client, login, owner, hq, operator, mapping, issue, notification = isolated_business
    headers = login(owner)
    url = '/api/notifications/'+str(notification.id)+'/read'
    assert client.get('/api/notifications').json()['unread_count'] == 1
    mapping.ended_at = utcnow(); db.commit()
    inbox = client.get('/api/notifications').json()
    assert inbox['total'] == 0 and inbox['unread_count'] == 0
    assert client.post(url, json={}, headers=headers).status_code == 404
    operator_headers = login(operator)
    assert client.get('/api/notifications').status_code == 403
    assert client.post(url, json={}, headers=operator_headers).status_code == 403


@pytest.mark.parametrize('field', ['status', 'priority'])
def test_issue_nonnullable_fields_return_validation_error(isolated_business, field):
    db, client, login, owner, hq, operator, mapping, issue, notification = isolated_business
    headers = login(hq)
    response = client.patch('/api/issues/'+str(issue.id), json={'version':issue.version, field:None}, headers=headers)
    assert response.status_code == 422
    db.refresh(issue)
    assert getattr(issue, field) is not None


def test_analytics_excludes_missing_and_unknown_pairs_and_preserves_null(isolated_business):
    db, client, login, owner, hq, operator, mapping, issue, notification = isolated_business
    original = db.get(Submission, issue.submission_id)
    monday = utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    monday -= timedelta(days=monday.weekday())
    for index, passed in enumerate([1, 2, 3, 4, 0]):
        when = monday-timedelta(weeks=index)+timedelta(days=2)
        submission = Submission(store_id=original.store_id, category_id=original.category_id,
                                submitted_by_id=owner.id, question='통계 경계 검증', created_at=when)
        db.add(submission); db.flush()
        db.add(AnalysisJob(submission_id=submission.id, status='succeeded', queued_at=when,
                           queue_deadline_at=when+timedelta(seconds=180), started_at=when,
                           finished_at=when+timedelta(seconds=1)))
        # 집계 입력의 분모·결측만 확인하는 합성 결과로 실제 AI 결과로 세지 않는다.
        db.add(ReviewResult(submission_id=submission.id, result={'criteria':[]},
                            source_kind='mock', prompt_version='independent-aggregate', latency_ms=0,
                            compliance_rate=passed*25 if index < 4 else None,
                            assessable_rate=100 if index < 4 else 0, pass_count=passed,
                            fail_count=4-passed if index < 4 else 0, unknown_count=4 if index == 4 else 0,
                            needs_ofc_review=index == 4))
        if index != 3:
            db.add(SalesMock(store_id=original.store_id, category_id=original.category_id,
                             week_start=when.date()-timedelta(days=2), amount=(index+1)*100))
    db.commit(); login(hq)
    params = {'date_from':(monday-timedelta(weeks=4)).date().isoformat(),
              'date_to':(monday+timedelta(days=6)).date().isoformat(),
              'store_id':str(original.store_id), 'category_id':str(original.category_id), 'is_active':'true'}
    response = client.get('/api/analytics/correlation', params=params)
    assert response.status_code == 200
    report = response.json()
    assert report['mock'] is True and report['n'] == 3 and report['r'] == 1.0
    assert report['excluded_missing_count'] == 1 and report['excluded_unassessable_count'] == 1
    assert all(point['review_count'] == 1 for point in report['points'])
    for sales in db.scalars(select(SalesMock)):
        sales.amount = 100
    db.commit()
    report = client.get('/api/analytics/correlation', params=params).json()
    assert report['n'] == 3 and report['r'] is None and report['reason'] == 'zero_variance'
    unknown_only = dict(params, date_from=(monday-timedelta(weeks=4)).date().isoformat(),
                        date_to=(monday-timedelta(weeks=4)+timedelta(days=6)).date().isoformat())
    summary = client.get('/api/dashboard', params=unknown_only).json()
    assert summary['kpis']['compliance_rate'] is None and summary['kpis']['assessable_rate'] == 0
    assert summary['sample_count'] == 1


def test_failed_snapshot_validation_removes_new_uploads(isolated_business, tmp_path, monkeypatch):
    db, client, login, owner, hq, operator, mapping, issue, notification = isolated_business
    original = db.get(Submission, issue.submission_id)
    root = tmp_path/'independent-upload-media'
    monkeypatch.setattr(get_settings(), 'media_root', root)
    for index in range(4):
        rule = Guideline(rule_key='independent_'+str(index), title='검증 기준', level='HQ',
                         scope_key='HQ:all:all', created_by_id=hq.id)
        db.add(rule); db.flush()
        db.add(GuidelineVersion(guideline_id=rule.id, version=1, text='가'*10000,
                                change_reason='총합 한도 검증', created_by_id=hq.id))
    db.commit()
    headers = login(owner)
    image = BytesIO(); Image.new('RGB', (64,64), '#aabbee').save(image, format='PNG')
    before = db.scalar(select(func.count()).select_from(Submission))
    response = client.post('/api/submissions', data={'metadata':json.dumps({
        'store_id':str(original.store_id), 'category_id':str(original.category_id), 'question':'검증'})},
        files=[('photos',('independent.png',image.getvalue(),'image/png'))],
        headers={**headers,'Idempotency-Key':str(uuid4())})
    assert response.status_code == 422
    assert db.scalar(select(func.count()).select_from(Submission)) == before
    assert db.scalar(select(func.count()).select_from(MediaAsset)) == 0
    assert not root.exists() or not list(root.iterdir())


def test_concurrent_issue_creation_replays_one_resource(isolated_business):
    from server.issues.service import create_issue
    from server.issues.schemas import IssueCreate
    db, client, login, owner, hq, operator, mapping, issue, notification = isolated_business
    engine, owner_id, submission_id = db.get_bind(), owner.id, issue.submission_id
    before = db.scalar(select(func.count()).select_from(Issue))
    db.commit()
    key, barrier = str(uuid4()), Barrier(2)
    def create():
        with Session(engine, expire_on_commit=False) as session:
            actor = session.get(Account, owner_id)
            barrier.wait(timeout=10)
            result, replayed = create_issue(session, actor, IssueCreate(
                submission_id=submission_id, title='동시 문의', description='동일 요청 재전송'), key)
            return result['id'], replayed
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: create(), range(2)))
    assert len({result[0] for result in results}) == 1
    assert sorted(result[1] for result in results) == [False, True]
    assert db.scalar(select(func.count()).select_from(Issue)) == before+1


def test_concurrent_guideline_revision_has_one_winner(isolated_business):
    from server.guidelines.service import revise_guideline
    from server.guidelines.schemas import GuidelineVersionCreate
    from server.core.errors import ApiError
    db, client, login, owner, hq, operator, mapping, issue, notification = isolated_business
    rule = Guideline(rule_key='concurrent_facing', title='동시성 기준', level='HQ',
                     scope_key='HQ:all:all', created_by_id=hq.id)
    db.add(rule); db.flush()
    db.add(GuidelineVersion(guideline_id=rule.id, version=1, text='처음 기준',
                            change_reason='독립 검증', created_by_id=hq.id)); db.commit()
    engine, actor_id, rule_id = db.get_bind(), hq.id, rule.id
    barrier = Barrier(2)
    def revise(index):
        with Session(engine, expire_on_commit=False) as session:
            actor = session.get(Account, actor_id)
            barrier.wait(timeout=10)
            try:
                result = revise_guideline(session, actor, rule_id,
                    GuidelineVersionCreate(version=1, text='경쟁 수정 '+str(index), reason='독립 경합 검증'), uuid4())
                return result['current_version']
            except ApiError as error:
                return error.status_code
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(revise, range(2)))
    assert sorted(results) == [2, 409]
    assert db.scalar(select(func.count()).select_from(GuidelineVersion).where(GuidelineVersion.guideline_id == rule_id)) == 2


@pytest.mark.parametrize('scope_filter', ['region_id', 'store_id'])
def test_guideline_scope_filters_exclude_other_regions(isolated_business, scope_filter):
    db, client, login, owner, hq, operator, mapping, issue, notification = isolated_business
    own_store = db.get(Store, mapping.store_id)
    other_region = Region(code='independent-other-region', name='다른 지역')
    db.add(other_region); db.flush()
    other_store = Store(code='independent-other-store', name='다른 지역 매장',
                        region_id=other_region.id, store_type='주택가형', address='')
    db.add(other_store); db.flush()
    def rule(level, target=None):
        row = Guideline(rule_key='scope_filter', title='범위 필터 검증', level=level,
                        scope_key=f'{level}:{target or "all"}:all', created_by_id=hq.id,
                        store_id=target if level == 'STORE' else None,
                        region_id=target if level == 'REGION' else None)
        db.add(row); db.flush()
        db.add(GuidelineVersion(guideline_id=row.id, version=1, text='진열 정렬 확인',
                                change_reason='독립 범위 검증', created_by_id=hq.id))
        return row.id
    global_id, own_id = rule('HQ'), rule('STORE', own_store.id)
    outside = {rule('STORE', other_store.id), rule('REGION', other_region.id)}
    db.commit(); login(hq)
    value = own_store.id if scope_filter == 'store_id' else own_store.region_id
    response = client.get('/api/guidelines', params={scope_filter:str(value), 'page_size':100})
    assert response.status_code == 200
    identifiers = {UUID(item['id']) for item in response.json()['items']}
    assert {global_id, own_id} <= identifiers
    assert not identifiers & outside, '선택 지역·매장에 적용할 수 없는 다른 지역 기준은 제외해야 합니다.'


def test_seed_chronology_replay_and_snapshot_integrity(postgres_db, tmp_path, monkeypatch):
    from server.seed import __main__ as seeder
    (tmp_path/'scripts').mkdir()
    (tmp_path/'scripts/seed').symlink_to(seeder.PROJECT_ROOT/'scripts/seed', target_is_directory=True)
    monkeypatch.setattr(seeder, 'PROJECT_ROOT', tmp_path)
    monkeypatch.setattr(get_settings(), 'media_root', tmp_path/'media')
    db = postgres_db
    created = seeder.seed(db)
    assert created['created'] > 500
    contexts = list(db.scalars(select(AnalysisContext)))
    boundary_errors = []
    pending = db.scalar(select(AnalysisJob).where(AnalysisJob.status == 'queued'))
    assert pending is not None and pending.is_fixture
    if pending.current_attempt_id is not None:
        boundary_errors.append('최초 대기 작업은 점유 전 Attempt를 갖지 않아야 합니다.')
    empty = [row for row in contexts if not row.snapshot['guidelines'] and not row.snapshot['references']]
    assert len(empty) == 1
    empty_submission = db.get(Submission, empty[0].submission_id)
    earlier_reference = db.scalar(select(ReferencePhoto.id).where(
        ReferencePhoto.category_id == empty_submission.category_id,
        or_(ReferencePhoto.store_id.is_(None), ReferencePhoto.store_id == empty_submission.store_id),
        ReferencePhoto.created_at <= empty_submission.created_at,
    ).limit(1))
    if earlier_reference:
        boundary_errors.append('비교 자료 도입 전 사례보다 먼저 등록된 적용 Reference가 존재합니다.')
    empty_review = db.scalar(select(ReviewResult).where(ReviewResult.submission_id == empty_submission.id))
    assert empty_review.compliance_rate is None and empty_review.assessable_rate is None
    assert empty_review.needs_ofc_review and empty_review.source_kind == 'mock'
    assert not boundary_errors, ' '.join(boundary_errors)
    original = {row.id:row.snapshot_sha256 for row in contexts}
    count = db.scalar(select(func.count()).select_from(Submission))
    store = db.scalar(select(Store).order_by(Store.code))
    store.name = '독립 검증에서 변경한 매장명'; db.commit()
    replayed = seeder.seed(db)
    assert replayed.get('created', 0) == 0 and store.name == '독립 검증에서 변경한 매장명'
    assert db.scalar(select(func.count()).select_from(Submission)) == count
    assert original == {row.id:row.snapshot_sha256 for row in db.scalars(select(AnalysisContext))}
    assert set(db.scalars(select(ReviewResult.source_kind))) == {'mock'}
    future_versions = []
    for context in contexts:
        submission = db.get(Submission, context.submission_id)
        digest = hashlib.sha256(json.dumps(context.snapshot, ensure_ascii=False, sort_keys=True,
                                           separators=(',', ':')).encode()).hexdigest()
        assert digest == context.snapshot_sha256
        for item in context.snapshot['guidelines'] + context.snapshot['candidate_guidelines']:
            version = db.get(GuidelineVersion, UUID(item['version_id']))
            if as_utc(version.created_at) > as_utc(submission.created_at):
                future_versions.append((str(submission.id), version.version))
    assert not future_versions, f'기준 생성 전 제출에서 미래 기준을 사용한 항목 수: {len(future_versions)}'
    from server.submissions.service import detail
    from server.submissions.storage import authorize_media
    context = next(row for row in contexts if row.snapshot['references'])
    submission = db.get(Submission, context.submission_id)
    owner = db.get(Account, submission.submitted_by_id)
    snapshot_before = json.dumps(context.snapshot, sort_keys=True)
    reference = db.get(ReferencePhoto, UUID(context.snapshot['references'][0]['reference_id']))
    reference.is_active = False; reference.state_version += 1; db.commit()
    result = detail(db, owner, submission.id)
    assert len(result['reference_photos']) == len(context.snapshot['references'])
    for metadata, original_reference in zip(result['reference_photos'], context.snapshot['references']):
        assert metadata['reference_id'] == original_reference['reference_id']
        assert metadata['photo']['media_id'] == original_reference['photo_id']
        assert metadata['photo']['source_kind'] == 'ai_generated_demo'
        assert authorize_media(db, owner, UUID(original_reference['photo_id'])).id == UUID(original_reference['photo_id'])
    assert json.dumps(context.snapshot, sort_keys=True) == snapshot_before
    assert context.snapshot_sha256 == original[context.id]
    from server.analysis_jobs.service import claim_next_job, sweep_expired
    # 만료된 시연 대기는 실제 모델 실행 후보로 점유되지 않는다.
    assert claim_next_job(db, 'independent-seed-worker', now=seeder.BASE) is None
    sweep_expired(db, now=seeder.BASE)
    db.refresh(pending)
    assert pending.status == 'failed' and pending.error_code == 'QUEUE_TIMEOUT'
    expired = db.get(AnalysisAttempt, pending.current_attempt_id)
    assert expired.status == 'expired' and expired.started_at is None
    assert expired.attempt_number == 1
    replayed = seeder.seed(db)
    assert replayed.get('created', 0) == 0 and pending.status == 'failed'


def test_start_rejects_unmanaged_healthy_api_instead_of_mixing_databases(tmp_path, monkeypatch):
    import importlib
    from server.core.config import PROJECT_ROOT
    monkeypatch.syspath_prepend(str(PROJECT_ROOT/'scripts'))
    services = importlib.import_module('services')
    (tmp_path/'pids').mkdir()
    monkeypatch.setattr(services, 'LOCAL', tmp_path)
    monkeypatch.setattr(services, 'healthy', lambda port: True)
    # 기존 프로세스나 소켓에 접근하지 않고 미관리 health 응답만 재현한다.
    with pytest.raises(SystemExit):
        services.launch('api', ['synthetic-python','-m','uvicorn','server.main:app'], 'server.main:app', 8000)


def test_secret_scanner_rejects_synthetic_input_without_output(capsys):
    from scripts import security_guard
    binary = security_guard.scanner()
    security_guard.scan(binary, ['stdin'], b'ordinary synthetic documentation\n')
    candidate = ('token = "' + 'ghp_' + 'aB3dE6gH9jK2mN5pQ8sT1vW4yZ7cF0iL3oR6' + '"\n').encode()
    with pytest.raises(RuntimeError):
        security_guard.scan(binary, ['stdin'], candidate)
    # 검사 대상 값은 실제 서비스에서 유효하지 않으며 로그에도 전달되지 않아야 한다.
    output = capsys.readouterr()
    assert not output.out and not output.err
