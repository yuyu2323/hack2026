"""세션 발급과 계정 공개 DTO."""
import secrets
from datetime import timedelta
from sqlalchemy import select
from server.accounts.models import Account,AuthSession
from server.core.config import get_settings
from server.core.db import utcnow
from server.core.security import hash_token,verify_password,hash_password
from server.core.errors import ApiError
from server.core.permissions import accessible_store_ids
from server.core.serialization import fields,scalar

_DUMMY_HASH=hash_password('external-invalid-timing-dummy')


def account_me(db,account):
    from server.core.auth import DEMO_ROLE_LOGINS
    result=fields(account,['id','login_id','display_name','role','region_id','is_active','version'])
    result['store_ids']=[str(value) for value in accessible_store_ids(db,account)]
    result['demo_multi_role_enabled'] = bool(get_settings().demo_multi_role_enabled and account.is_active
                                            and DEMO_ROLE_LOGINS.get(account.role) == account.login_id)
    result['demo_public_access_enabled'] = get_settings().demo_public_access_enabled
    result['permissions']={'store_owner':['submit','view_business'],'ofc':['manage_guidelines','manage_issues','view_business'],'regional':['manage_guidelines','manage_issues','view_business'],'hq':['manage_guidelines','manage_issues','view_business'],'platform_operator':['operate']}[account.role]
    return result


def new_session(db,response,account=None,*,cookie_name=None):
    settings=get_settings()
    token=secrets.token_urlsafe(32); csrf=secrets.token_urlsafe(32)
    now=utcnow(); expires=now+timedelta(hours=12) if account else now+timedelta(minutes=30)
    session=AuthSession(token_hash=hash_token(token),csrf_hash=hash_token(csrf),account_id=account.id if account else None,created_at=now,expires_at=expires,
                        is_public_demo=settings.demo_public_access_enabled)
    db.add(session)
    response.set_cookie(cookie_name or settings.session_cookie_name,token,httponly=True,secure=settings.session_cookie_secure,samesite='lax',path='/',max_age=int((expires-now).total_seconds()))
    if cookie_name is None and account is not None and settings.demo_multi_role_enabled:
        from server.core.auth import DEMO_ROLE_LOGINS
        if account.role in DEMO_ROLE_LOGINS:
            response.set_cookie(settings.session_cookie_name+'_'+account.role,token,httponly=True,
                                secure=settings.session_cookie_secure,samesite='lax',path='/',
                                max_age=int((expires-now).total_seconds()))
    return csrf,expires


def authenticate(db,data):
    account=db.scalar(select(Account).where(Account.login_id==data.login_id))
    valid=verify_password(data.password,account.password_hash if account else _DUMMY_HASH)
    if not account or not valid or not account.is_active:
        raise ApiError(401,'INVALID_CREDENTIALS','로그인 정보를 확인해 주세요.')
    return account
