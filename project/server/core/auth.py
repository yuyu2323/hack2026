"""DB 세션과 현재 계정 권한, 세션에 결합된 CSRF 검증."""
import hmac
import re
from urllib.parse import urlsplit
from fastapi import Request, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from server.core.config import get_settings
from server.core.db import get_db, utcnow, as_utc
from server.core.errors import ApiError
from server.core.security import hash_token
from server.accounts.models import Account, AuthSession

DEMO_ROLE_LOGINS = {'store_owner': 'owner.north', 'ofc': 'ofc.north', 'platform_operator': 'operator.demo'}


def restrict_public_demo_write(request):
    if not get_settings().demo_public_access_enabled or request.method in ('GET','HEAD','OPTIONS'):
        return
    path = request.url.path.rstrip('/')
    allowed = request.method == 'POST' and (path in (
        '/api/auth/login', '/api/auth/logout', '/api/auth/demo-sessions', '/api/submissions')
        or re.fullmatch(r'/api/operations/jobs/[0-9a-fA-F-]{36}/retry', path))
    if not allowed:
        raise ApiError(403, 'DEMO_READ_ONLY', '공개 시연에서는 운영 설정을 변경할 수 없습니다.')


def role_for_request(request):
    role = request.headers.get('x-storeloop-role')
    query_role = request.query_params.get('demo_role') if request.url.path.startswith('/api/media/') and request.method in ('GET','HEAD') else None
    if query_role is not None:
        if role is not None and role != query_role:
            raise ApiError(403, 'FORBIDDEN', '시연 역할이 일치하지 않습니다.')
        role = query_role
    return role


def cookie_name_for_request(request):
    settings = get_settings()
    role = role_for_request(request)
    if role is None:
        return settings.session_cookie_name
    if not settings.demo_multi_role_enabled or role not in DEMO_ROLE_LOGINS:
        raise ApiError(403, 'FORBIDDEN', '허용되지 않은 시연 역할입니다.')
    return settings.session_cookie_name + '_' + role


def session_for_request(request: Request, db: Session, required=True):
    token=request.cookies.get(cookie_name_for_request(request))
    session=db.scalar(select(AuthSession).where(AuthSession.token_hash==hash_token(token))) if token and len(token)<=256 else None
    if not session:
        if required: raise ApiError(401,'UNAUTHENTICATED','로그인이 필요합니다.')
        return None
    if session.revoked_at is not None or as_utc(session.expires_at)<=utcnow():
        if required: raise ApiError(401,'SESSION_EXPIRED','로그인 시간이 만료되었습니다.')
        return None
    if session.is_public_demo and not get_settings().demo_public_access_enabled:
        if required: raise ApiError(401,'SESSION_EXPIRED','공개 시연이 종료되었습니다. 다시 로그인해 주세요.')
        return None
    role = role_for_request(request)
    if role is not None and session.account_id:
        account = db.get(Account, session.account_id)
        if not account or account.role != role:
            raise ApiError(403, 'FORBIDDEN', '시연 세션의 역할이 일치하지 않습니다.')
    return session


def validate_origin(request: Request, required=True):
    origin=request.headers.get('origin')
    if not origin:
        referer=request.headers.get('referer')
        if referer:
            parsed=urlsplit(referer)
            origin=f'{parsed.scheme}://{parsed.netloc}'
    if request.headers.get('sec-fetch-site')=='cross-site' or (origin and origin not in get_settings().allowed_origins) or (required and not origin):
        raise ApiError(403,'ORIGIN_DENIED','허용되지 않은 요청 출처입니다.')


def require_csrf(request: Request, db: Session=Depends(get_db)):
    restrict_public_demo_write(request)
    if request.method in ('GET','HEAD','OPTIONS'):
        return None
    validate_origin(request)
    session=session_for_request(request,db)
    token=request.headers.get('x-csrf-token','')
    if not token or len(token)>256 or not hmac.compare_digest(hash_token(token),session.csrf_hash):
        raise ApiError(403,'CSRF_INVALID','요청 인증이 만료되었습니다. 화면을 새로고침해 주세요.')
    return session


def get_current_account(request: Request, db: Session=Depends(get_db)) -> Account:
    restrict_public_demo_write(request)
    session=session_for_request(request,db)
    account=db.get(Account,session.account_id) if session.account_id else None
    if not account: raise ApiError(401,'UNAUTHENTICATED','로그인이 필요합니다.')
    if not account.is_active: raise ApiError(401,'ACCOUNT_INACTIVE','이용이 중지된 계정입니다.')
    return account


def require_roles(*roles):
    def dependency(account: Account=Depends(get_current_account)):
        if account.role not in roles: raise ApiError(403,'FORBIDDEN','이 기능을 이용할 권한이 없습니다.')
        return account
    return dependency
