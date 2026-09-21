from typing import Annotated, Literal
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Header, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from server.core.db import get_db
from server.core.auth import get_current_account, require_csrf
from server.core.errors import ApiError
from server.accounts.models import Account
from server.submissions.models import Submission
from server.submissions.service import filtered_submissions
from server.issues.models import Issue
from server.issues.schemas import IssueCreate, IssueChange, ActionCreate
from server.issues import service
from server.business_common import BusinessFilter, page, fields

router = APIRouter(prefix='/api/issues', tags=['issues'], dependencies=[Depends(require_csrf)])
DB = Annotated[Session, Depends(get_db)]
USER = Annotated[Account, Depends(get_current_account)]

@router.get('')
def listing(db: DB, account: USER, filters: Annotated[BusinessFilter, Depends()], page_number: int = Query(1, alias='page', ge=1), page_size: int = Query(20, ge=1, le=100), status: Literal['open','in_progress','resolved'] | None = None, unresolved: bool | None = None, assignee_id: UUID | None = None, priority: Literal['normal','high'] | None = None):
    if unresolved is not None and status:
        raise ApiError(422, 'VALIDATION_ERROR', '상태와 미해결 필터는 함께 지정할 수 없습니다.')
    submissions = filtered_submissions(db, account, filters)
    query = select(Issue).where(Issue.submission_id.in_([row.id for row in submissions]))
    if status:
        query = query.where(Issue.status == status)
    if unresolved is not None:
        query = query.where(Issue.status != 'resolved') if unresolved else query.where(Issue.status == 'resolved')
    if assignee_id:
        query = query.where(Issue.assignee_id == assignee_id)
    if priority:
        query = query.where(Issue.priority == priority)
    return page([service.issue_summary(db, row) for row in db.scalars(query.order_by(Issue.updated_at.desc(), Issue.id))], page_number, page_size)

@router.post('', status_code=201)
def create(data: IssueCreate, response: Response, db: DB, account: USER, key: str | None = Header(None, alias='Idempotency-Key')):
    result, replayed = service.create_issue(db, account, data, key)
    if replayed:
        response.headers['Idempotency-Replayed'] = 'true'
    return result

@router.get('/{ident}')
def detail(ident: UUID, db: DB, account: USER):
    return service.issue_detail(db, service.get_issue(db, account, ident))

@router.get('/{ident}/assignees')
def candidates(ident: UUID, db: DB, account: USER, page_number: int = Query(1, alias='page', ge=1), page_size: int = Query(20, ge=1, le=100)):
    if account.role not in ('ofc','regional','hq'):
        raise ApiError(403, 'FORBIDDEN', '영업 관리자 권한이 필요합니다.')
    issue = service.get_issue(db, account, ident)
    submission = db.get(Submission, issue.submission_id)
    return page([fields(row, 'id display_name role') for row in service.assignees(db, submission.store_id)], page_number, page_size)

@router.patch('/{ident}')
def update(ident: UUID, data: IssueChange, db: DB, account: USER):
    return service.update_issue(db, account, ident, data)

@router.post('/{ident}/actions', status_code=201)
def action(ident: UUID, data: ActionCreate, db: DB, account: USER):
    return service.add_action(db, account, ident, data.body)
