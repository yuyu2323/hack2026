from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.core.db import get_db
from server.core.auth import get_current_account
from server.accounts.models import Account
from server.business_common import BusinessFilter
from server.dashboard.service import dashboard

router = APIRouter(prefix='/api/dashboard', tags=['dashboard'])

@router.get('')
def get_dashboard(db: Annotated[Session, Depends(get_db)], account: Annotated[Account, Depends(get_current_account)], filters: Annotated[BusinessFilter, Depends()]):
    return dashboard(db, account, filters)
