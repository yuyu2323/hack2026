def test_login_has_pre_authentication_csrf_session(client):
    response = client.get('/api/auth/csrf')
    assert response.status_code == 200
    assert len(response.json()['csrf_token']) >= 32
    assert 'HttpOnly' in response.headers['set-cookie']


def test_session_rotates_and_current_activation_is_checked(client,db,account_factory,login_as):
    account=account_factory()
    client.get('/api/auth/csrf')
    old=client.cookies.get('storeloop_session')
    headers=login_as(account)
    assert client.cookies.get('storeloop_session')!=old
    assert client.get('/api/auth/me').status_code==200
    account.is_active=False;db.commit()
    assert client.get('/api/auth/me').status_code==401
    assert client.get('/api/auth/me').json()['error']['code']=='ACCOUNT_INACTIVE'


def test_login_rejects_missing_csrf_and_origin(client,account_factory):
    from server.tests.conftest import TEST_PASSWORD
    account=account_factory()
    csrf=client.get('/api/auth/csrf').json()['csrf_token']
    body={'login_id':account.login_id,'password':TEST_PASSWORD}
    assert client.post('/api/auth/login',json=body,headers={'Origin':'http://testserver'}).status_code==403
    assert client.post('/api/auth/login',json=body,headers={'X-CSRF-Token':csrf,'Origin':'https://untrusted.invalid'}).status_code==403


def test_logout_revokes_session_and_password_is_never_serialized(client,db,account_factory,login_as):
    from sqlalchemy import select
    from server.accounts.models import AuthSession
    account=account_factory();headers=login_as(account)
    body=client.get('/api/auth/me').json()
    assert 'password_hash' not in body and 'password' not in body
    assert client.post('/api/auth/logout',json={},headers=headers).status_code==204
    assert client.get('/api/auth/me').status_code==401
    assert any(row.revoked_at for row in db.scalars(select(AuthSession)))


def test_expired_session_is_rejected_without_leaking_token(client,db,account_factory,login_as):
    from datetime import timedelta
    from sqlalchemy import select
    from server.accounts.models import AuthSession
    from server.core.db import utcnow
    account=account_factory();login_as(account)
    session=db.scalar(select(AuthSession).where(AuthSession.account_id==account.id,AuthSession.revoked_at.is_(None)))
    session.created_at=utcnow()-timedelta(hours=2);session.expires_at=utcnow()-timedelta(seconds=1);db.commit()
    response=client.get('/api/auth/me')
    assert response.status_code==401 and response.json()['error']['code']=='SESSION_EXPIRED'
    assert session.token_hash not in response.text and session.csrf_hash not in response.text


def test_validation_error_omits_password_input(client):
    secret='invalid-short'
    token=client.get('/api/auth/csrf').json()['csrf_token']
    response=client.post('/api/auth/login',json={'login_id':'valid.name','password':secret,'unexpected':'not allowed'},headers={'Origin':'http://testserver','X-CSRF-Token':token})
    assert response.status_code==422
    assert secret not in response.text and 'input' not in response.json()['error']
