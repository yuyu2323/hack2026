"""DB 세션과 현재 계정 권한, 세션에 결합된 CSRF 검증."""
import hmac
from urllib.parse import urlsplit
from fastapi import Request, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from server.core.config import get_settings
from server.core.db import get_db, utcnow, as_utc
from server.core.errors import ApiError
from server.core.security import hash_token
from server.accounts.models import Account, AuthSession


def session_for_request(request: Request, db: Session, required=True):
    token=request.cookies.get(get_settings().session_cookie_name)
    session=db.scalar(select(AuthSession).where(AuthSession.token_hash==hash_token(token))) if token and len(token)<=256 else None
    if not session:
        if required: raise ApiError(401,'UNAUTHENTICATED','로그인이 필요합니다.')
        return None
    if session.revoked_at is not None or as_utc(session.expires_at)<=utcnow():
        if required: raise ApiError(401,'SESSION_EXPIRED','로그인 시간이 만료되었습니다.')
        return None
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
    if request.method in ('GET','HEAD','OPTIONS'):
        return None
    validate_origin(request)
    session=session_for_request(request,db)
    token=request.headers.get('x-csrf-token','')
    if not token or len(token)>256 or not hmac.compare_digest(hash_token(token),session.csrf_hash):
        raise ApiError(403,'CSRF_INVALID','요청 인증이 만료되었습니다. 화면을 새로고침해 주세요.')
    return session


def get_current_account(request: Request, db: Session=Depends(get_db)) -> Account:
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
