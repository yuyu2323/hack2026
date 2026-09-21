from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from server.core.db import get_db
from server.core.auth import get_current_account, require_csrf
from server.accounts.models import Account
from server.notifications import service
from server.business_common import page

router = APIRouter(prefix='/api/notifications', tags=['notifications'], dependencies=[Depends(require_csrf)])
DB = Annotated[Session, Depends(get_db)]
USER = Annotated[Account, Depends(get_current_account)]

@router.get('')
def listing(db: DB, account: USER, page_number: int = Query(1, alias='page', ge=1), page_size: int = Query(20, ge=1, le=100), unread_only: bool = False):
    rows = service.visible_notifications(db, account)
    count = sum(row.read_at is None for row in rows)
    result = page([service.dto(row) for row in rows if not unread_only or row.read_at is None], page_number, page_size)
    result['unread_count'] = count
    return result

@router.post('/{ident}/read')
def read(ident: UUID, db: DB, account: USER):
    return service.mark_read(db, account, ident)
