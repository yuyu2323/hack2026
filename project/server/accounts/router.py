import secrets
from fastapi import APIRouter,Depends,Request,Response
from sqlalchemy.orm import Session
from server.accounts.schemas import LoginInput,EmptyInput
from server.accounts.service import new_session,authenticate,account_me
from server.core.db import get_db,utcnow
from server.core.auth import session_for_request,require_csrf,get_current_account,validate_origin
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
    else: token,expiry=new_session(db,response)
    db.commit()
    return {'csrf_token':token,'expires_at':scalar(expiry)}

@router.post('/login')
def login(data:LoginInput,request:Request,response:Response,db:Session=Depends(get_db),old_session=Depends(require_csrf)):
    account=authenticate(db,data)
    old_session.revoked_at=utcnow()
    token,expiry=new_session(db,response,account)
    db.commit()
    return {'account':account_me(db,account),'csrf_token':token,'expires_at':scalar(expiry)}

@router.get('/me')
def me(db:Session=Depends(get_db),account=Depends(get_current_account)):
    return account_me(db,account)

@router.post('/logout',status_code=204)
def logout(data:EmptyInput,response:Response,db:Session=Depends(get_db),session=Depends(require_csrf)):
    session.revoked_at=utcnow(); db.commit()
    response.delete_cookie(get_settings().session_cookie_name,path='/',httponly=True,secure=get_settings().session_cookie_secure,samesite='lax')
