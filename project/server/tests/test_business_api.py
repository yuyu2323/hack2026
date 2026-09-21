"""실제 인증을 거친 제출·스냅샷·미디어·집계 경계를 검증한다."""
from io import BytesIO
import json
from uuid import uuid4
import pytest
from PIL import Image
from server.core.config import get_settings
from server.core.db import utcnow
from server.stores.models import Category, StoreOwnerMapping
from server.guidelines.models import Guideline, GuidelineVersion

@pytest.fixture
def business(db, make_client, account_factory, store_factory, login_as, tmp_path, monkeypatch):
    from server.main import app
    client = make_client(app)
    monkeypatch.setattr(get_settings(), 'media_root', tmp_path / 'media')
    owner = account_factory()
    store = store_factory()
    db.add(StoreOwnerMapping(account_id=owner.id, store_id=store.id, changed_by_id=owner.id, reason='검증'))
    category = Category(code='beverage', name='음료', description='')
    db.add(category); db.commit()
    headers = login_as(owner, client)
    stream = BytesIO(); Image.new('RGB', (64, 64), '#336699').save(stream, format='PNG')
    def submit(key=None, **extra):
        data = {'store_id': str(store.id), 'category_id': str(category.id), 'question': '앞줄 정렬은 어떤가요?', **extra}
        return client.post('/api/submissions', data={'metadata': json.dumps(data)}, files=[('photos', ('shelf.png', stream.getvalue(), 'image/png'))], headers={**headers, 'Idempotency-Key': key or str(uuid4())})
    return client, owner, store, category, headers, submit

def test_submission_snapshot_replay_and_current_scope(business, db):
    client, owner, store, category, headers, submit = business
    rule = Guideline(rule_key='facing', title='앞줄 정렬', level='HQ', scope_key='HQ:*:*', created_by_id=owner.id)
    db.add(rule); db.flush()
    version = GuidelineVersion(guideline_id=rule.id, version=1, text='앞줄을 정렬한다.', change_reason='검증', created_by_id=owner.id)
    db.add(version); db.commit()
    key = str(uuid4()); first = submit(key)
    assert first.status_code == 202, first.text
    sid = first.json()['submission_id']
    replay = submit(key)
    assert replay.status_code == 202 and replay.json()['submission_id'] == sid
    assert replay.headers['Idempotency-Replayed'] == 'true'
    assert submit(key, question='다른 질문').status_code == 409
    detail = client.get('/api/submissions/' + sid).json()
    assert detail['context']['guidelines'][0]['version_id'] == str(version.id)
    assert detail['review'] is None and detail['job']['status'] == 'queued'
    photo = detail['photos'][0]
    assert client.get(photo['url']).status_code == 200
    mapping = db.query(StoreOwnerMapping).filter_by(account_id=owner.id).one()
    mapping.ended_at = utcnow(); db.commit()
    assert client.get('/api/submissions/' + sid).status_code == 404
    assert client.get(photo['url']).status_code == 404
    assert client.get(photo['thumbnail_url']).status_code == 404

def test_empty_null_rates_and_operator_denied(business, account_factory, login_as):
    client, owner, store, category, headers, submit = business
    dashboard = client.get('/api/dashboard').json()
    assert dashboard['kpis']['store_count'] == 1
    assert dashboard['kpis']['compliance_rate'] is None
    assert dashboard['stores'][0]['status'] == 'not_submitted'
    assert dashboard['filters']['is_active'] is True
    correlation = client.get('/api/analytics/correlation').json()
    assert correlation['mock'] is True and correlation['n'] == 0
    assert correlation['reason'] == 'insufficient_samples'
    login_as(account_factory(role='platform_operator'), client)
    for path in ('/api/submissions', '/api/dashboard', '/api/analytics/trends', '/api/issues', '/api/notifications'):
        assert client.get(path).status_code == 403, path

def test_owner_inquiry_and_follow_up(business):
    client, owner, store, category, headers, submit = business
    first = submit().json()['submission_id']
    child = submit(parent_submission_id=first)
    assert child.status_code == 202
    detail = client.get('/api/submissions/' + first).json()
    assert detail['children'][0]['id'] == child.json()['submission_id']
    comparison = client.get('/api/submissions/' + child.json()['submission_id'] + '/comparison').json()
    assert comparison['parent']['submission_id'] == first
    issue = client.post('/api/issues', json={'submission_id': first, 'title': '진열 문의', 'description': '확인이 필요합니다.'}, headers={**headers, 'Idempotency-Key': str(uuid4())})
    assert issue.status_code == 201, issue.text
    assert client.get('/api/issues?unresolved=true').json()['total'] == 1
    assert client.get('/api/dashboard').json()['kpis']['open_issue_count'] == 1

def test_bad_images_and_missing_idempotency_do_not_create(business):
    client, owner, store, category, headers, submit = business
    body = json.dumps({'store_id': str(store.id), 'category_id': str(category.id)})
    bad = client.post('/api/submissions', data={'metadata': body}, files=[('photos', ('bad.png', b'not-image', 'image/png'))], headers={**headers, 'Idempotency-Key': str(uuid4())})
    assert bad.status_code == 415
    assert client.get('/api/submissions').json()['total'] == 0

def test_criterion_and_reference_versions_preserve_submission_context(business, db, account_factory, login_as):
    client, owner, store, category, headers, submit = business
    hq = account_factory(role='hq')
    manager_headers = login_as(hq, client)
    guideline = client.post('/api/guidelines', json={'rule_key':'facing','title':'앞줄 정렬','level':'HQ','text':'앞면을 정렬한다.','reason':'최초 등록'}, headers=manager_headers)
    assert guideline.status_code == 201, guideline.text
    guideline = guideline.json()
    stream = BytesIO(); Image.new('RGB',(64,64),'green').save(stream,format='PNG')
    reference = client.post('/api/references', data={'metadata':json.dumps({'category_id':str(category.id),'caption':'최초 Reference','reason':'최초 등록'})}, files={'photo':('reference.png',stream.getvalue(),'image/png')}, headers=manager_headers)
    assert reference.status_code == 201, reference.text
    reference = reference.json()
    headers.update(login_as(owner, client))
    first = submit().json()['submission_id']
    original_detail = client.get('/api/submissions/'+first).json()
    original = original_detail['context']
    expected_reference_photos = [{'reference_id':reference['id'], 'photo':reference['photo']}]
    assert original_detail['reference_photos'] == expected_reference_photos
    manager_headers = login_as(hq, client)
    revised = client.post('/api/guidelines/'+guideline['id']+'/versions',json={'version':guideline['version'],'text':'앞면과 간격을 정렬한다.','reason':'기준 보완'},headers=manager_headers)
    assert revised.status_code == 201
    assert client.post('/api/guidelines/'+guideline['id']+'/versions',json={'version':guideline['version'],'text':'동시 수정','reason':'충돌 확인'},headers=manager_headers).status_code == 409
    reference2 = client.patch('/api/references/'+reference['id'],data={'metadata':json.dumps({'state_version':reference['state_version'],'caption':'개선 Reference 설명','reason':'설명 보완'})},headers=manager_headers)
    assert reference2.status_code == 200, reference2.text
    assert reference2.json()['id'] != reference['id']
    assert client.patch('/api/references/'+reference['id']+'/status',json={'state_version':1,'is_active':True,'reason':'구버전 변경'},headers=manager_headers).status_code == 409
    headers.update(login_as(owner, client))
    child = submit(parent_submission_id=first).json()['submission_id']
    preserved_detail = client.get('/api/submissions/'+first).json()
    assert preserved_detail['context'] == original
    assert preserved_detail['reference_photos'] == expected_reference_photos
    newer = client.get('/api/submissions/'+child).json()['context']
    assert newer['guidelines'][0]['version'] == 2
    assert newer['references'][0]['reference_id'] == reference2.json()['id']
    assert client.get(reference['photo']['url']).status_code == 200

def test_manager_issue_resolution_version_and_notifications(business, account_factory, login_as):
    client, owner, store, category, headers, submit = business
    submission = submit().json()['submission_id']
    issue = client.post('/api/issues',json={'submission_id':submission,'title':'확인 요청','description':'진열 확인 부탁드립니다.'},headers={**headers,'Idempotency-Key':str(uuid4())}).json()
    manager_headers = login_as(account_factory(role='hq'),client)
    url = '/api/issues/'+issue['id']
    assert client.patch(url,json={'version':issue['version'],'status':'resolved'},headers=manager_headers).status_code == 422
    resolved = client.patch(url,json={'version':issue['version'],'status':'resolved','resolution':'정렬을 확인했습니다.'},headers=manager_headers)
    assert resolved.status_code == 200, resolved.text
    assert resolved.json()['actions'][0]['to_status'] == 'resolved'
    assert client.patch(url,json={'version':issue['version'],'status':'open'},headers=manager_headers).status_code == 409
    same = client.patch(url,json={'version':resolved.json()['version'],'status':'resolved'},headers=manager_headers)
    assert same.json()['version'] == resolved.json()['version']
    candidates = client.get(url+'/assignees').json()
    assert candidates['total'] >= 1 and candidates['page'] == 1
    headers.update(login_as(owner,client))
    inbox = client.get('/api/notifications').json()
    assert inbox['unread_count'] == 1
    notice = inbox['items'][0]
    read = client.post('/api/notifications/'+notice['id']+'/read',json={},headers=headers).json()
    reread = client.post('/api/notifications/'+notice['id']+'/read',json={},headers=headers).json()
    assert read['read_at'] == reread['read_at']

def test_cross_scope_ids_are_hidden_and_inactive_history_remains(business, store_factory, db):
    client, owner, store, category, headers, submit = business
    submission = submit().json()['submission_id']
    other = store_factory()
    assert client.get('/api/dashboard?store_id='+str(other.id)).status_code == 404
    assert client.get('/api/submissions?store_id='+str(other.id)).status_code == 404
    store.is_active = False; db.commit()
    assert client.get('/api/submissions/'+submission).status_code == 200
    assert client.get('/api/submissions').json()['total'] == 1
    assert client.get('/api/dashboard').json()['kpis']['store_count'] == 0
    assert submit().status_code == 422
