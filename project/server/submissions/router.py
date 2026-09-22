from typing import Annotated, Literal
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Header, Response, Form, File, UploadFile, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import Session
from server.core.db import get_db
from server.core.auth import get_current_account, require_csrf
from server.core.errors import ApiError
from server.accounts.models import Account
from server.analysis_jobs.models import AnalysisJob
from server.reviews.models import ReviewResult
from server.submissions import service
from server.submissions.schemas import SubmissionCreate
from server.submissions.storage import authorize_media, read_media
from server.business_common import BusinessFilter, page, metadata_json

router = APIRouter(prefix='/api', tags=['submissions'], dependencies=[Depends(require_csrf)])
DB = Annotated[Session, Depends(get_db)]
USER = Annotated[Account, Depends(get_current_account)]

@router.post('/submissions', status_code=202)
def create(background_tasks: BackgroundTasks, response: Response, db: DB, account: USER, metadata: str = Form(...), photos: list[UploadFile] = File(...), key: str | None = Header(None, alias='Idempotency-Key')):
    result, replayed = service.create_submission(db, account, metadata_json(metadata, SubmissionCreate), photos, key)
    from server.vercel_runtime import schedule_analysis
    schedule_analysis(background_tasks, result['job']['id'])
    if replayed:
        response.headers['Idempotency-Replayed'] = 'true'
    return result

@router.get('/submissions')
def listing(db: DB, account: USER, filters: Annotated[BusinessFilter, Depends()], page_number: int = Query(1, alias='page', ge=1), page_size: int = Query(20, ge=1, le=100), status: Literal['queued','running','succeeded','failed'] | None = None, needs_ofc_review: bool | None = None):
    rows = service.filtered_submissions(db, account, filters)
    results = []
    for row in rows:
        summary = service.summary(db, row)
        if status is not None and summary['job']['status'] != status:
            continue
        if needs_ofc_review is not None and (summary['review_summary'] is None or summary['review_summary']['needs_ofc_review'] != needs_ofc_review):
            continue
        results.append(summary)
    return page(results, page_number, page_size)

@router.get('/submissions/{ident}')
def detail(ident: UUID, db: DB, account: USER):
    return service.detail(db, account, ident)

@router.get('/submissions/{ident}/comparison')
def comparison(ident: UUID, db: DB, account: USER):
    from server.reviews.service import compare
    return compare(db, account, ident)

@router.get('/jobs/{ident}')
def job(background_tasks: BackgroundTasks, ident: UUID, db: DB, account: USER):
    from server.core.permissions import require_business
    require_business(account)
    row = db.get(AnalysisJob, ident)
    if row is None:
        raise ApiError(404, 'NOT_FOUND', '작업을 찾을 수 없습니다.')
    service.get_submission(db, account, row.submission_id)
    from server.vercel_runtime import schedule_analysis
    schedule_analysis(background_tasks, row.id)
    return service.job_dto(db, row)

@router.get('/media/{ident}')
def media(ident: UUID, db: DB, account: USER, variant: Literal['original','thumbnail'] = 'original'):
    row = authorize_media(db, account, ident)
    return Response(read_media(db, row, variant == 'thumbnail'), media_type='image/jpeg' if variant == 'thumbnail' else row.mime_type,
                        headers={'Cache-Control': 'private, no-store', 'X-Content-Type-Options': 'nosniff'})
