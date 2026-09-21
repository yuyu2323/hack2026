"""미사용 과거 Reference의 관리 범위와 사진 인가를 독립 검증한다."""
from io import BytesIO
import json

import pytest
from PIL import Image
from sqlalchemy import func, select

from server.core.config import get_settings
from server.core.db import utcnow
from server.stores.models import Category, OFCStoreMapping, StoreOwnerMapping
from server.submissions.models import AnalysisContext, Submission


@pytest.fixture
def unused_reference_history(db, make_client, account_factory, store_factory,
                             login_as, tmp_path, monkeypatch):
    from server.main import app

    client = make_client(app)
    monkeypatch.setattr(get_settings(), 'media_root', tmp_path / 'media')
    hq = account_factory(role='hq')
    store = store_factory()
    category = Category(code='independent-reference', name='검증 카테고리', description='')
    db.add(category)
    db.commit()

    def create_history(common=False):
        headers = login_as(hq, client)
        first_image, second_image = BytesIO(), BytesIO()
        Image.new('RGB', (64, 64), '#225588').save(first_image, format='PNG')
        Image.new('RGB', (64, 64), '#88aa44').save(second_image, format='PNG')
        first = client.post(
            '/api/references',
            data={'metadata': json.dumps({'category_id': str(category.id),
                  'store_id': None if common else str(store.id),
                  'caption': '합성 첫 Reference', 'reason': '독립 회귀 등록'})},
            files={'photo': ('first.png', first_image.getvalue(), 'image/png')},
            headers=headers,
        )
        assert first.status_code == 201
        first = first.json()
        second = client.patch(
            '/api/references/' + first['id'],
            data={'metadata': json.dumps({'state_version': first['state_version'],
                  'caption': '합성 교체 Reference', 'reason': '제출 전 사진 교체'})},
            files={'photo': ('second.png', second_image.getvalue(), 'image/png')},
            headers=headers,
        )
        assert second.status_code == 200
        second = second.json()
        assert second['lineage_id'] == first['lineage_id']
        assert second['version'] == 2 and second['photo']['media_id'] != first['photo']['media_id']
        # 이전 사진에 제출/분석 이력이 없으므로 별도 허용 경로가 개입하지 않는다.
        assert db.scalar(select(func.count()).select_from(Submission)) == 0
        assert db.scalar(select(func.count()).select_from(AnalysisContext)) == 0
        return first, second

    return client, hq, store, create_history


def media_statuses(client, photo):
    return {variant: client.get(photo[key]).status_code
            for variant, key in [('original', 'url'), ('thumbnail', 'thumbnail_url')]}


@pytest.mark.parametrize(('role', 'common'), [
    ('hq', True), ('hq', False), ('regional', False), ('ofc', False),
])
def test_manager_can_read_unused_inactive_reference_images_in_current_scope(
        unused_reference_history, db, account_factory, login_as, role, common):
    client, hq, store, create_history = unused_reference_history
    first, second = create_history(common)
    manager = hq if role == 'hq' else account_factory(role=role, region_id=store.region_id)
    if role == 'ofc':
        db.add(OFCStoreMapping(account_id=manager.id, store_id=store.id,
                              changed_by_id=hq.id, reason='현재 담당 연결'))
        db.commit()
    login_as(manager, client)
    current = client.get('/api/references').json()['items']
    assert {row['id'] for row in current} == {second['id']}
    history = client.get('/api/references?include_inactive=true').json()['items']
    old = next(row for row in history if row['id'] == first['id'])
    assert old['is_active'] is False
    assert old['photo'] == first['photo']
    assert old['photo']['source_kind'] == 'user_upload'
    detail = client.get('/api/references/' + first['id'])
    assert detail.status_code == 200 and detail.json()['photo'] == old['photo']
    assert media_statuses(client, second['photo']) == {'original': 200, 'thumbnail': 200}
    assert media_statuses(client, old['photo']) == {'original': 200, 'thumbnail': 200}


@pytest.mark.parametrize('scenario', [
    'owner', 'operator', 'other_region', 'unassigned_ofc', 'ended_ofc',
])
def test_inactive_reference_media_does_not_expand_other_roles_or_current_scope(
        unused_reference_history, db, account_factory, login_as, scenario):
    client, hq, store, create_history = unused_reference_history
    first, second = create_history()
    if scenario == 'owner':
        account = account_factory()
        db.add(StoreOwnerMapping(account_id=account.id, store_id=store.id,
                                 changed_by_id=hq.id, reason='현재 점주 연결'))
    elif scenario == 'operator':
        account = account_factory(role='platform_operator')
    elif scenario == 'other_region':
        account = account_factory(role='regional')
        assert account.region_id != store.region_id
    else:
        account = account_factory(role='ofc', region_id=store.region_id)
        if scenario == 'ended_ofc':
            db.add(OFCStoreMapping(account_id=account.id, store_id=store.id,
                                  changed_by_id=hq.id, reason='종료한 담당 연결', ended_at=utcnow()))
    db.commit()
    login_as(account, client)
    status = 403 if scenario == 'operator' else 404
    assert media_statuses(client, first['photo']) == {'original': status, 'thumbnail': status}
    reference_status = 403 if scenario in ('owner', 'operator') else 404
    assert client.get('/api/references/' + first['id']).status_code == reference_status
    if scenario == 'owner':
        # 점주의 활성 사용 가능 Reference 열람은 유지하지만 미사용 과거 사진까지 넓히지 않는다.
        assert media_statuses(client, second['photo']) == {'original': 200, 'thumbnail': 200}
    else:
        assert media_statuses(client, second['photo']) == {'original': status, 'thumbnail': status}
