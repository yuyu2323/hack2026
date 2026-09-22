"""제출 시점의 사진·기준을 고정하고 결과와 이력을 조회한다."""
from datetime import timedelta
import hashlib
import json
from uuid import UUID, uuid4
from sqlalchemy import select, func, or_
from server.core.errors import ApiError
from server.core.db import utcnow, as_utc
from server.core.config import get_settings
from server.core.permissions import require_store_access, require_business
from server.business_common import encode, fields, active_category, scoped_stores, period, lock_idempotency, save_idempotency, request_hash
from server.stores.models import Store, Category
from server.guidelines.models import Guideline, GuidelineVersion, ReferencePhoto
from server.guidelines.resolution import resolve_guidelines
from server.submissions.models import Submission, SubmissionPhoto, MediaAsset, AnalysisContext
from server.submissions.media import normalize_image, LIMIT
from server.submissions.storage import store_media, cleanup, photo_dto
from server.analysis_jobs.models import AnalysisJob, AnalysisAttempt
from server.reviews.models import ReviewResult
from server.issues.models import Issue


def get_submission(db, account, ident):
    require_business(account)
    item = db.get(Submission, ident)
    if item is None:
        raise ApiError(404, 'NOT_FOUND', '제출을 찾을 수 없습니다.')
    require_store_access(db, account, item.store_id)
    return item


def make_snapshot(db, store, category, question, photos, previous):
    candidates = []
    query = select(Guideline).where(Guideline.is_active == True, or_(Guideline.category_id.is_(None), Guideline.category_id == category.id))
    for item in db.scalars(query):
        applies = (item.level == 'HQ' or (item.level == 'REGION' and item.region_id == store.region_id)
                   or (item.level == 'STORE' and item.store_id == store.id)
                   or (item.level == 'CATEGORY' and item.store_id in (None, store.id)))
        if not applies:
            continue
        version = db.scalar(select(GuidelineVersion).where(GuidelineVersion.guideline_id == item.id, GuidelineVersion.version == item.current_version))
        candidates.append(dict(guideline_id=str(item.id), version_id=str(version.id), version=version.version,
                               level=item.level, rule_key=item.rule_key, text=version.text,
                               store_id=str(item.store_id) if item.store_id else None,
                               category_id=str(item.category_id) if item.category_id else None))
    try:
        effective, history = resolve_guidelines(candidates)
    except ValueError as exc:
        raise ApiError(422, 'GUIDELINE_LIMIT', str(exc)) from exc
    allowed_keys = ('guideline_id', 'version_id', 'version', 'level', 'rule_key', 'text')
    effective = [{key: row[key] for key in allowed_keys} for row in effective]
    history = [{key: row[key] for key in (*allowed_keys, 'selected', 'selection_reason')} for row in history]
    refs = list(db.scalars(select(ReferencePhoto).where(ReferencePhoto.is_active == True, ReferencePhoto.category_id == category.id,
                           or_(ReferencePhoto.store_id.is_(None), ReferencePhoto.store_id == store.id))
                           .order_by(ReferencePhoto.store_id.is_(None), ReferencePhoto.created_at.desc(), ReferencePhoto.id).limit(3)))
    references = []
    for position, reference in enumerate(refs, 1):
        media = db.get(MediaAsset, reference.photo_id)
        references.append(dict(reference_id=str(reference.id), photo_id=str(media.id), position=position,
                               caption=reference.caption, mime_type=media.mime_type, sha256=media.sha256))
    return dict(store={'id': str(store.id), 'region_id': str(store.region_id), 'name': store.name},
                category={'id': str(category.id), 'name': category.name}, question=question,
                photos=photos, candidate_guidelines=history, guidelines=effective, references=references, previous_review=previous)


def create_submission(db, account, data, uploads, key):
    if account.role != 'store_owner':
        raise ApiError(403, 'FORBIDDEN', '점주만 사진을 제출할 수 있습니다.')
    store = require_store_access(db, account, data.store_id, write=True)
    category = active_category(db, data.category_id)
    if not 1 <= len(uploads) <= 5:
        raise ApiError(422, 'VALIDATION_ERROR', '사진을 1~5장 선택해 주세요.')
    previous = None
    if data.parent_submission_id:
        parent = get_submission(db, account, data.parent_submission_id)
        if parent.submitted_by_id != account.id or parent.store_id != store.id or parent.category_id != category.id:
            raise ApiError(404, 'NOT_FOUND', '이전 제출을 연결할 수 없습니다.')
        review = db.scalar(select(ReviewResult).where(ReviewResult.submission_id == parent.id))
        if review:
            previous = dict(submission_id=str(parent.id), review_id=str(review.id), criteria=review.result['criteria'])
    hashes = []
    for upload in uploads:
        raw = upload.file.read(LIMIT + 1)
        upload.file.seek(0)
        try:
            hashes.append(normalize_image(raw, upload.filename, upload.content_type)['sha256'])
        except ValueError as exc:
            raise ApiError(413 if len(raw) > LIMIT else 415, 'FILE_TOO_LARGE' if len(raw) > LIMIT else 'UNSUPPORTED_MEDIA', str(exc)) from exc
    digest = request_hash('POST', '/submissions', data.model_dump(mode='json'), hashes)
    replay = lock_idempotency(db, account, 'submissions.create', key, digest)
    if replay:
        item = get_submission(db, account, replay.resource_id)
        return submission_accepted(db, item), True
    paths = []
    try:
        from server.analysis_jobs.quota import consume_public_analysis
        consume_public_analysis(db)
        item = Submission(id=uuid4(), store_id=store.id, category_id=category.id, submitted_by_id=account.id,
                          question=data.question, parent_submission_id=data.parent_submission_id)
        db.add(item)
        db.flush()
        photo_inputs = []
        kinds = []
        for position, upload in enumerate(uploads, 1):
            media = store_media(db, account, upload, paths)
            photo = SubmissionPhoto(id=uuid4(), submission_id=item.id, media_id=media.id, position=position)
            db.add(photo)
            kinds.append(media.source_kind)
            photo_inputs.append(dict(photo_id=str(photo.id), media_id=str(media.id), position=position, mime_type=media.mime_type, sha256=media.sha256))
        item.source_kind = 'ai_generated_demo' if all(kind == 'ai_generated_demo' for kind in kinds) else 'user_upload'
        snapshot = make_snapshot(db, store, category, data.question, photo_inputs, previous)
        digest_context = hashlib.sha256(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
        db.add(AnalysisContext(id=uuid4(), submission_id=item.id, snapshot=snapshot, snapshot_sha256=digest_context, schema_version='1.0'))
        now = utcnow()
        db.add(AnalysisJob(id=uuid4(), submission_id=item.id, status='queued', queued_at=now,
                           queue_deadline_at=now + timedelta(seconds=get_settings().queue_timeout_seconds)))
        save_idempotency(db, account, 'submissions.create', key, digest, item.id, 202)
        db.commit()
        return submission_accepted(db, item), False
    except Exception:
        db.rollback()
        cleanup(paths)
        raise


def job_dto(db, job):
    result = fields(job, 'id submission_id status queued_at started_at finished_at error_code error_message current_attempt_id')
    result['attempt_count'] = db.scalar(select(func.count()).select_from(AnalysisAttempt).where(AnalysisAttempt.job_id == job.id))
    elapsed = int(((as_utc(job.finished_at) if job.finished_at else utcnow()) - as_utc(job.created_at)).total_seconds() * 1000)
    result.update(elapsed_ms=max(elapsed, 0), delayed=elapsed >= 30000 and job.status in ('queued', 'running'))
    return result


def submission_accepted(db, item):
    job = db.scalar(select(AnalysisJob).where(AnalysisJob.submission_id == item.id))
    return {'submission_id': str(item.id), 'job': job_dto(db, job), 'created_at': encode(item.created_at)}


def review_dto(review):
    return fields(review, 'id submission_id attempt_id schema_version result compliance_rate assessable_rate pass_count fail_count unknown_count needs_ofc_review source_kind model_name prompt_version latency_ms created_at')


def summary(db, item):
    store, category = db.get(Store, item.store_id), db.get(Category, item.category_id)
    photos = list(db.scalars(select(SubmissionPhoto).where(SubmissionPhoto.submission_id == item.id).order_by(SubmissionPhoto.position)))
    job = db.scalar(select(AnalysisJob).where(AnalysisJob.submission_id == item.id))
    review = db.scalar(select(ReviewResult).where(ReviewResult.submission_id == item.id))
    result = fields(item, 'id store_id category_id submitted_by_id created_at parent_submission_id source_kind')
    result.update(store_name=store.name, category_name=category.name, photo_count=len(photos),
                  thumbnail=photo_dto(db, photos[0].media_id, photos[0].position, photos[0].id) if photos else None,
                  job=job_dto(db, job), review_summary=fields(review, 'id compliance_rate assessable_rate needs_ofc_review source_kind') if review else None,
                  open_issue_count=db.scalar(select(func.count()).select_from(Issue).where(Issue.submission_id == item.id, Issue.status != 'resolved')))
    return result


def detail(db, account, ident):
    item = get_submission(db, account, ident)
    result = summary(db, item)
    context = db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id == ident))
    review = db.scalar(select(ReviewResult).where(ReviewResult.submission_id == ident))
    photos = db.scalars(select(SubmissionPhoto).where(SubmissionPhoto.submission_id == ident).order_by(SubmissionPhoto.position)).all()
    parent = db.get(Submission, item.parent_submission_id) if item.parent_submission_id else None
    children = db.scalars(select(Submission).where(Submission.parent_submission_id == ident).order_by(Submission.created_at)).all()
    from server.issues.service import issue_summary
    issues = db.scalars(select(Issue).where(Issue.submission_id == ident).order_by(Issue.created_at)).all()
    result.update(question=item.question, photos=[photo_dto(db, photo.media_id, photo.position, photo.id) for photo in photos],
                  context=dict(context.snapshot, schema_version=context.schema_version, snapshot_sha256=context.snapshot_sha256),
                  reference_photos=[{'reference_id':ref['reference_id'],
                                     'photo':photo_dto(db, UUID(ref['photo_id']))}
                                    for ref in context.snapshot.get('references', [])],
                  review=review_dto(review) if review else None, parent=fields(parent, 'id created_at') if parent else None,
                  children=[fields(child, 'id created_at') for child in children], issues=[issue_summary(db, issue) for issue in issues])
    return result


def filtered_submissions(db, account, filters):
    stores = scoped_stores(db, account, filters)
    start, end = period(filters)
    query = select(Submission).where(Submission.store_id.in_([store.id for store in stores]), Submission.created_at >= start, Submission.created_at < end)
    if filters.category_id:
        query = query.where(Submission.category_id == filters.category_id)
    return list(db.scalars(query.order_by(Submission.created_at.desc(), Submission.id)))
