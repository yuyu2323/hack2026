from typing import Annotated, Literal
from uuid import UUID
from fastapi import APIRouter, Depends, Form, File, UploadFile, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from server.core.db import get_db
from server.core.auth import get_current_account, require_csrf
from server.accounts.models import Account
from server.guidelines.models import GuidelineVersion
from server.guidelines.schemas import GuidelineCreate, GuidelineVersionCreate, GuidelineStatus, ReferenceCreate, ReferenceChange, ReferenceStatus
from server.guidelines import service
from server.business_common import page, fields, metadata_json

router = APIRouter(prefix='/api', tags=['guidelines'], dependencies=[Depends(require_csrf)])
DB = Annotated[Session, Depends(get_db)]
USER = Annotated[Account, Depends(get_current_account)]

@router.get('/guidelines')
def listing(db: DB, account: USER, page_number: int = Query(1, alias='page', ge=1), page_size: int = Query(20, ge=1, le=100), store_id: UUID | None = None, region_id: UUID | None = None, category_id: UUID | None = None, level: Literal['HQ','REGION','STORE','CATEGORY'] | None = None, is_active: bool | None = None):
    return page(service.list_guidelines(db, account, store_id, region_id, category_id, level, is_active), page_number, page_size)

@router.post('/guidelines', status_code=201)
def create(data: GuidelineCreate, request: Request, db: DB, account: USER):
    return service.create_guideline(db, account, data, request.state.request_id)

@router.get('/guidelines/{ident}')
def detail(ident: UUID, db: DB, account: USER):
    return service.guideline_dto(db, service.get_guideline(db, account, ident))

@router.get('/guidelines/{ident}/versions')
def versions(ident: UUID, db: DB, account: USER, page_number: int = Query(1, alias='page', ge=1), page_size: int = Query(20, ge=1, le=100)):
    service.get_guideline(db, account, ident)
    rows = db.scalars(select(GuidelineVersion).where(GuidelineVersion.guideline_id == ident).order_by(GuidelineVersion.version.desc())).all()
    return page([dict(version_id=str(row.id), **fields(row, 'version text change_reason created_at created_by_id')) for row in rows], page_number, page_size)

@router.post('/guidelines/{ident}/versions', status_code=201)
def revise(ident: UUID, data: GuidelineVersionCreate, request: Request, db: DB, account: USER):
    return service.revise_guideline(db, account, ident, data, request.state.request_id)

@router.patch('/guidelines/{ident}')
def status(ident: UUID, data: GuidelineStatus, request: Request, db: DB, account: USER):
    return service.revise_guideline(db, account, ident, data, request.state.request_id, True)

@router.get('/references')
def references(db: DB, account: USER, page_number: int = Query(1, alias='page', ge=1), page_size: int = Query(20, ge=1, le=100), category_id: UUID | None = None, store_id: UUID | None = None, include_inactive: bool = False):
    return page(service.list_references(db, account, category_id, store_id, include_inactive), page_number, page_size)

@router.get('/references/{ident}')
def reference(ident: UUID, db: DB, account: USER):
    return service.reference_dto(db, service.get_reference(db, account, ident))

@router.post('/references', status_code=201)
def reference_create(request: Request, db: DB, account: USER, metadata: str = Form(...), photo: UploadFile = File(...)):
    return service.create_reference(db, account, metadata_json(metadata, ReferenceCreate), photo, request.state.request_id)

@router.patch('/references/{ident}/status')
def reference_status(ident: UUID, data: ReferenceStatus, request: Request, db: DB, account: USER):
    return service.change_reference(db, account, ident, data, request.state.request_id, status_only=True)

@router.patch('/references/{ident}')
def reference_change(ident: UUID, request: Request, db: DB, account: USER, metadata: str = Form(...), photo: UploadFile | None = File(None)):
    return service.change_reference(db, account, ident, metadata_json(metadata, ReferenceChange), request.state.request_id, photo)
