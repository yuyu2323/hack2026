from typing import Annotated, Literal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from server.core.db import get_db
from server.core.auth import get_current_account
from server.accounts.models import Account
from server.business_common import BusinessFilter
from server.analytics import service

router = APIRouter(prefix='/api/analytics', tags=['analytics'])
DB = Annotated[Session, Depends(get_db)]
USER = Annotated[Account, Depends(get_current_account)]
FILTER = Annotated[BusinessFilter, Depends()]

@router.get('/trends')
def trends(db: DB, account: USER, filters: FILTER):
    return service.trends(db, account, filters)

@router.get('/correlation')
def correlation(db: DB, account: USER, filters: FILTER):
    return service.correlate(db, account, filters)

@router.get('/report')
def report(db: DB, account: USER, filters: FILTER, group_by: Literal['store','region','category'] = 'store'):
    return service.report(db, account, filters, group_by)
