from fastapi import Request
from starlette.requests import Request as StarletteRequest
from server.core.config import get_settings
from server.core.auth import DEMO_ROLE_LOGINS, cookie_name_for_request
from server.core.errors import ApiError
import pytest

@pytest.fixture
def demo_accounts(account_factory, monkeypatch):
    monkeypatch.setattr(get_settings(), 'demo_multi_role_enabled', True)
    return {role: account_factory(role=role, login_id=login) for role, login in DEMO_ROLE_LOGINS.items()}

def bootstrap(client, login_as, demo_accounts):
    headers = login_as(demo_accounts['platform_operator'])
    response = client.post('/api/auth/demo-sessions', json={}, headers=headers)
    assert response.status_code == 200, response.text
    return headers

def role_headers(client, role):
    headers = {'X-StoreLoop-Role': role}
    csrf = client.get('/api/auth/csrf', headers=headers)
    assert csrf.status_code == 200
    return {**headers, 'Origin':'http://testserver', 'X-CSRF-Token':csrf.json()['csrf_token']}

def test_bootstrap_anonymous_and_owner_forbidden(client, login_as, demo_accounts):
    assert client.post('/api/auth/demo-sessions',json={},headers={'Origin':'http://testserver'}).status_code in (401,403)
    headers=login_as(demo_accounts['store_owner'])
    assert client.post('/api/auth/demo-sessions',json={},headers=headers).status_code==403

def test_optout_and_unknown_role_fail_closed(client,login_as,demo_accounts,monkeypatch):
    headers=login_as(demo_accounts['platform_operator'])
    monkeypatch.setattr(get_settings(),'demo_multi_role_enabled',False)
    assert client.post('/api/auth/demo-sessions',json={},headers=headers).status_code==403
    assert client.get('/api/auth/me',headers={'X-StoreLoop-Role':'platform_operator'}).status_code==403
    assert client.get('/api/auth/me').json()['demo_multi_role_enabled'] is False
    monkeypatch.setattr(get_settings(),'demo_multi_role_enabled',True)
    assert client.get('/api/auth/me',headers={'X-StoreLoop-Role':'hq'}).status_code==403

def test_role_sessions_permissions_csrf_logout(client,login_as,demo_accounts):
    base_headers=bootstrap(client,login_as,demo_accounts)
    base=get_settings().session_cookie_name
    assert len({client.cookies.get(base+'_'+r) for r in DEMO_ROLE_LOGINS})==3
    for role in DEMO_ROLE_LOGINS:
        assert client.get('/api/auth/me',headers={'X-StoreLoop-Role':role}).json()['role']==role
    owner=role_headers(client,'store_owner')
    operator=role_headers(client,'platform_operator')
    assert client.get('/api/operations/accounts',headers=owner).status_code==403
    assert client.get('/api/operations/accounts',headers=operator).status_code==200
    assert client.post('/api/auth/logout',json={},headers={**owner,'X-CSRF-Token':operator['X-CSRF-Token']}).status_code==403
    assert client.post('/api/auth/demo-sessions',json={},headers=operator).status_code==403
    assert client.post('/api/auth/logout',json={},headers=owner).status_code==204
    assert client.get('/api/auth/me',headers={'X-StoreLoop-Role':'store_owner'}).status_code==401
    assert client.get('/api/auth/me',headers=operator).status_code==200
    assert client.get('/api/auth/me').json()['role']=='platform_operator'

def test_inactive_target_prevents_all_bootstrap(client,db,login_as,demo_accounts):
    headers=login_as(demo_accounts['platform_operator'])
    demo_accounts['ofc'].is_active=False;db.commit()
    assert client.post('/api/auth/demo-sessions',json={},headers=headers).status_code==409
    assert client.cookies.get(get_settings().session_cookie_name+'_store_owner') is None

def test_normal_login_role_cookie_and_wrong_role_token(client,account_factory,login_as,monkeypatch):
    monkeypatch.setattr(get_settings(),'demo_multi_role_enabled',True)
    account=account_factory()
    login_as(account)
    base=get_settings().session_cookie_name
    assert client.cookies.get(base)==client.cookies.get(base+'_store_owner')
    result=client.get('/api/auth/me',headers={'X-StoreLoop-Role':'store_owner'})
    assert result.status_code==200 and result.json()['demo_multi_role_enabled'] is False
    token=client.cookies.get(base)
    result=client.get('/api/auth/me',headers={'X-StoreLoop-Role':'platform_operator','Cookie':base+'_platform_operator='+token})
    assert result.status_code==403

def test_media_selector_is_scoped_and_conflict_rejected(monkeypatch):
    monkeypatch.setattr(get_settings(),'demo_multi_role_enabled',True)
    def request(path,query,headers=[]):
        return StarletteRequest({'type':'http','method':'GET','path':path,'query_string':query,'headers':headers})
    base=get_settings().session_cookie_name
    assert cookie_name_for_request(request('/api/media/123',b'demo_role=ofc'))==base+'_ofc'
    assert cookie_name_for_request(request('/api/auth/me',b'demo_role=ofc'))==base
    with pytest.raises(ApiError):
        cookie_name_for_request(request('/api/media/123',b'demo_role=ofc',[(b'x-storeloop-role',b'store_owner')]))

def test_public_bootstrap_still_requires_csrf_and_origin(client,demo_accounts,monkeypatch):
    monkeypatch.setattr(get_settings(),'demo_public_access_enabled',True)
    assert client.post('/api/auth/demo-sessions',json={},headers={'Origin':'http://testserver'}).status_code==401
    token=client.get('/api/auth/csrf').json()['csrf_token']
    assert client.post('/api/auth/demo-sessions',json={},headers={'Origin':'https://other.invalid','X-CSRF-Token':token}).status_code==403
    response=client.post('/api/auth/demo-sessions',json={},headers={'Origin':'http://testserver','X-CSRF-Token':token})
    assert response.status_code==200
    assert client.get('/api/auth/me').json()['role']=='platform_operator'
    assert client.get('/api/auth/me').json()['demo_public_access_enabled'] is True
    for role in DEMO_ROLE_LOGINS:
        assert client.get('/api/auth/me',headers={'X-StoreLoop-Role':role}).json()['role']==role
    headers=role_headers(client,'platform_operator')
    assert client.post('/api/operations/accounts',json={},headers=headers).status_code==403
    assert client.patch('/api/operations/stores/00000000-0000-0000-0000-000000000000',json={},headers=headers).status_code==403
    assert client.post('/api/auth/logout',json={},headers=headers).status_code==204

def test_public_bootstrap_requires_multi_role_flag(client,demo_accounts,monkeypatch):
    monkeypatch.setattr(get_settings(),'demo_public_access_enabled',True)
    monkeypatch.setattr(get_settings(),'demo_multi_role_enabled',False)
    token=client.get('/api/auth/csrf').json()['csrf_token']
    assert client.post('/api/auth/demo-sessions',json={},headers={'Origin':'http://testserver','X-CSRF-Token':token}).status_code==403

def test_public_session_cannot_be_reused_after_disable(client,db,demo_accounts,monkeypatch):
    from sqlalchemy import select
    from server.accounts.models import AuthSession
    from server.core.security import hash_token
    monkeypatch.setattr(get_settings(),'demo_public_access_enabled',True)
    csrf=client.get('/api/auth/csrf').json()['csrf_token']
    assert client.post('/api/auth/demo-sessions',json={},headers={'Origin':'http://testserver','X-CSRF-Token':csrf}).status_code==200
    base=get_settings().session_cookie_name
    token=client.cookies.get(base)
    base_csrf=client.get('/api/auth/csrf').json()['csrf_token']
    assert db.scalar(select(AuthSession).where(AuthSession.token_hash==hash_token(token))).is_public_demo
    monkeypatch.setattr(get_settings(),'demo_public_access_enabled',False)
    assert client.get('/api/auth/me').status_code==401
    assert client.post('/api/operations/accounts',json={},headers={'Origin':'http://testserver','X-CSRF-Token':base_csrf}).status_code==401
    role_token=client.cookies.get(base+'_platform_operator')
    assert client.get('/api/auth/me',headers={'Cookie':base+'='+role_token}).status_code==401

def test_normal_login_during_public_mode_also_expires(client,login_as,demo_accounts,monkeypatch):
    monkeypatch.setattr(get_settings(),'demo_public_access_enabled',True)
    login_as(demo_accounts['platform_operator'])
    assert client.get('/api/auth/me').status_code==200
    monkeypatch.setattr(get_settings(),'demo_public_access_enabled',False)
    assert client.get('/api/auth/me').status_code==401
