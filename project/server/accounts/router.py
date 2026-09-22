import secrets
from fastapi import APIRouter,Depends,Request,Response
from sqlalchemy.orm import Session
from sqlalchemy import select
from server.accounts.models import Account
from server.core.errors import ApiError
from server.accounts.schemas import LoginInput,EmptyInput
from server.accounts.service import new_session,authenticate,account_me
from server.core.db import get_db,utcnow
from server.core.auth import session_for_request,require_csrf,get_current_account,validate_origin,cookie_name_for_request,DEMO_ROLE_LOGINS
from server.core.security import hash_token
from server.core.serialization import scalar
from server.core.config import get_settings

router=APIRouter(prefix='/api/auth',tags=['accounts'])

@router.get('/csrf')
def csrf(request:Request,response:Response,db:Session=Depends(get_db)):
    validate_origin(request,required=False)
    session=session_for_request(request,db,required=False)
    if session:
        token=secrets.token_urlsafe(32); session.csrf_hash=hash_token(token); expiry=session.expires_at
    else: token,expiry=new_session(db,response,cookie_name=cookie_name_for_request(request))
    db.commit()
    return {'csrf_token':token,'expires_at':scalar(expiry)}

@router.post('/login')
def login(data:LoginInput,request:Request,response:Response,db:Session=Depends(get_db),old_session=Depends(require_csrf)):
    if request.headers.get('x-storeloop-role') is not None:
        raise ApiError(403,'FORBIDDEN','기본 로그인 화면을 이용해 주세요.')
    account=authenticate(db,data)
    old_session.revoked_at=utcnow()
    token,expiry=new_session(db,response,account)
    db.commit()
    return {'account':account_me(db,account),'csrf_token':token,'expires_at':scalar(expiry)}

@router.get('/me')
def me(db:Session=Depends(get_db),account=Depends(get_current_account)):
    return account_me(db,account)

@router.post('/logout',status_code=204)
def logout(data:EmptyInput,request:Request,response:Response,db:Session=Depends(get_db),session=Depends(require_csrf)):
    session.revoked_at=utcnow(); db.commit()
    response.delete_cookie(cookie_name_for_request(request),path='/',httponly=True,secure=get_settings().session_cookie_secure,samesite='lax')


@router.post('/demo-sessions')
def demo_sessions(data:EmptyInput,request:Request,response:Response,db:Session=Depends(get_db),session=Depends(require_csrf)):
    settings=get_settings()
    account=db.get(Account,session.account_id) if session.account_id else None
    private_allowed=bool(account and account.is_active and account.role=='platform_operator' and account.login_id=='operator.demo')
    if (not settings.demo_multi_role_enabled or request.headers.get('x-storeloop-role') is not None
        or not (settings.demo_public_access_enabled or private_allowed)):
        raise ApiError(403,'FORBIDDEN','시연 운영자의 기본 로그인이 필요합니다.')
    accounts=[]
    for role,login_id in DEMO_ROLE_LOGINS.items():
        target=db.scalar(select(Account).where(Account.login_id==login_id,Account.role==role,Account.is_active.is_(True)))
        if target is None:
            raise ApiError(409,'DEMO_UNAVAILABLE','시연 계정 구성을 확인해 주세요.')
        accounts.append((role,target))
    for role,target in accounts:
        new_session(db,response,target,cookie_name=settings.session_cookie_name+'_'+role)
    if settings.demo_public_access_enabled:
        session.revoked_at=utcnow()
        # 기본 진입 화면도 운영자 데모로 연결하되 역할 쿠키는 독립 세션을 유지한다.
        operator=next(target for role,target in accounts if role=='platform_operator')
        new_session(db,response,operator,cookie_name=settings.session_cookie_name)
    db.commit()
    return {'enabled':True}
