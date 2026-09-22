"""짧은 DB 트랜잭션으로 분석 큐·시도·결과의 단일 소유권을 보장한다."""
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
import logging
from uuid import UUID, uuid4

from pydantic import ValidationError
from sqlalchemy import func, or_, select

from packages.review_contract.errors import ContractError
from packages.review_contract.models import AnalysisInput
from packages.review_contract.validation import derive_metrics, validate_result
from server.accounts.models import Account
from server.analysis_jobs.models import AnalysisAttempt, AnalysisJob
from server.business_common import audit, lock_idempotency, request_hash, save_idempotency
from server.core.config import get_settings
from server.core.db import as_utc, utcnow
from server.core.errors import ApiError
from server.issues.service import on_review_ready
from server.operations.models import ServiceStatus
from server.reviews.models import CriterionEvaluation, ReviewResult
from server.submissions.models import AnalysisContext, Submission

logger = logging.getLogger(__name__)
ERROR_MESSAGES = {
    'QUEUE_TIMEOUT': '분석 대기 시간이 초과되었습니다.',
    'MODEL_TIMEOUT': '분석 시간이 초과되었습니다.',
    'AI_UNAVAILABLE': '분석 서비스 연결을 확인하고 있습니다.',
    'CLI_UNAVAILABLE': '분석 실행 환경을 확인하고 있습니다.',
    'MODEL_AUTH_FAILED': '분석 서비스 인증을 확인하고 있습니다.',
    'MODEL_EXECUTION_FAILED': '분석을 완료하지 못했습니다.',
    'EMPTY_RESPONSE': '분석 결과를 받지 못했습니다.',
    'INVALID_JSON': '분석 결과 형식을 확인할 수 없습니다.',
    'INVALID_RESULT': '분석 결과를 검증하지 못했습니다.',
    'INVALID_IMAGE': '사진 파일을 확인할 수 없습니다.',
    'WORKER_INTERRUPTED': '분석 작업이 중단되었습니다.',
}


@dataclass(frozen=True)
class Claim:
    job_id: UUID
    attempt_id: UUID
    submission_id: UUID
    worker_id: str
    deadline_at: datetime
    lease_expires_at: datetime


def _locked_job(db, job_id):
    return db.scalar(select(AnalysisJob).where(AnalysisJob.id == job_id)
                     .with_for_update().execution_options(populate_existing=True))


def _attempt(db, job):
    return db.scalar(select(AnalysisAttempt).where(AnalysisAttempt.id == job.current_attempt_id)
                     .with_for_update().execution_options(populate_existing=True)) if job.current_attempt_id else None


def _next_number(db, job):
    return (db.scalar(select(func.max(AnalysisAttempt.attempt_number)).where(AnalysisAttempt.job_id == job.id)) or 0) + 1


def _presence(db, name, now, **values):
    # 여러 작업자의 첫 heartbeat도 service_name 고유 제약과 충돌하지 않는다.
    if db.bind.dialect.name == 'postgresql':
        from sqlalchemy.dialects.postgresql import insert
    else:
        from sqlalchemy.dialects.sqlite import insert
    update = {'checked_at': now, **values}
    stmt = insert(ServiceStatus).values(id=uuid4(), service_name=name, details={}, is_fixture=False, **update)
    db.execute(stmt.on_conflict_do_update(index_elements=['service_name'], set_=update))


def retry_job(db, account, job_id, reason, idempotency_key, request_id):
    """실패 작업만 예약하며, 기존 성공·종료 시도는 수정하지 않는다."""
    try:
        current = db.scalar(select(Account).where(Account.id == account.id).with_for_update()
                            .execution_options(populate_existing=True))
        if current is None or not current.is_active or current.role != 'platform_operator':
            raise ApiError(403, 'FORBIDDEN', '플랫폼 운영자만 재처리할 수 있습니다.')
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 500:
            raise ApiError(422, 'VALIDATION_ERROR', '재처리 사유를 입력해 주세요.')
        digest = request_hash('POST', f'/operations/jobs/{job_id}/retry', {'reason': reason})
        existing = lock_idempotency(db, current, 'analysis.retry', idempotency_key, digest)
        if existing:
            job = db.get(AnalysisJob, existing.resource_id)
            db.commit()
            return job, True
        job = _locked_job(db, job_id)
        if job is None:
            raise ApiError(404, 'NOT_FOUND', '분석 작업을 찾을 수 없습니다.')
        if job.status != 'failed':
            raise ApiError(409, 'JOB_NOT_RETRYABLE', '실패한 분석 작업만 재처리할 수 있습니다.')
        from server.analysis_jobs.quota import consume_public_analysis
        consume_public_analysis(db)
        now = utcnow()
        previous = {'status': job.status, 'current_attempt_id': job.current_attempt_id, 'enqueue_generation': job.enqueue_generation}
        attempt = AnalysisAttempt(id=uuid4(), job_id=job.id, attempt_number=_next_number(db, job),
                                  status='queued', requested_by_id=current.id, queued_at=now)
        db.add(attempt); db.flush()
        job.status = 'queued'
        job.current_attempt_id = attempt.id
        job.enqueue_generation += 1
        job.queued_at = now
        job.queue_deadline_at = now + timedelta(seconds=get_settings().queue_timeout_seconds)
        job.started_at = job.finished_at = job.error_code = job.error_message = None
        audit(db, current, 'analysis_job.retry', 'analysis_job', job.id, reason, before=previous,
              after={'status': job.status, 'current_attempt_id': attempt.id, 'enqueue_generation': job.enqueue_generation}, request_id=request_id)
        save_idempotency(db, current, 'analysis.retry', idempotency_key, digest, job.id, 202)
        db.commit()
        return job, False
    except Exception:
        db.rollback()
        raise


def claim_next_job(db, worker_id, now=None, *, job_id=None):
    now = now or utcnow()
    try:
        query = select(AnalysisJob).where(AnalysisJob.status == 'queued', AnalysisJob.queue_deadline_at > now)
        if job_id is not None:
            query = query.where(AnalysisJob.id == job_id)
        job = db.scalar(query
                        .order_by(AnalysisJob.queued_at, AnalysisJob.id).with_for_update(skip_locked=True)
                        .limit(1).execution_options(populate_existing=True))
        if job is None:
            db.commit()
            return None
        attempt = _attempt(db, job)
        if attempt is None:
            attempt = AnalysisAttempt(id=uuid4(), job_id=job.id, attempt_number=_next_number(db, job),
                                      status='running', queued_at=job.queued_at)
            db.add(attempt)
        elif attempt.status != 'queued':
            raise RuntimeError('대기 작업과 시도 상태가 일치하지 않습니다.')
        attempt.status = 'running'
        attempt.worker_id = worker_id
        attempt.started_at = attempt.heartbeat_at = now
        attempt.deadline_at = now + timedelta(seconds=get_settings().ai_http_timeout_seconds)
        attempt.lease_expires_at = now + timedelta(seconds=get_settings().lease_timeout_seconds)
        db.flush()
        job.status, job.started_at, job.current_attempt_id = 'running', now, attempt.id
        claim = Claim(job.id, attempt.id, job.submission_id, worker_id, attempt.deadline_at, attempt.lease_expires_at)
        db.commit()
        return claim
    except Exception:
        db.rollback()
        raise


def _owned(db, claim):
    job = _locked_job(db, claim.job_id)
    if job is None or job.status != 'running' or job.current_attempt_id != claim.attempt_id:
        return None, None
    attempt = _attempt(db, job)
    if attempt is None or attempt.status != 'running' or attempt.worker_id != claim.worker_id:
        return None, None
    return job, attempt


def _finish_failure(job, attempt, code, now, expired=False):
    job.status, attempt.status = 'failed', 'expired' if expired else 'failed'
    job.finished_at = attempt.finished_at = now
    job.error_code = attempt.error_code = code
    job.error_message = attempt.error_message = ERROR_MESSAGES[code]
    attempt.result_applied = False


def fail_attempt(db, claim, code, now=None):
    now = now or utcnow()
    code = code if code in ERROR_MESSAGES else 'MODEL_EXECUTION_FAILED'
    try:
        job, attempt = _owned(db, claim)
        if job is None:
            db.commit()
            return False
        # lease를 잃은 작업자는 실패 상태도 바꾸지 못하며 복구 sweep가 종료한다.
        if as_utc(attempt.lease_expires_at) <= now:
            db.commit()
            return False
        _finish_failure(job, attempt, code, now, expired=code == 'MODEL_TIMEOUT')
        _presence(db, 'model', now, status='down', last_failure_at=now, error_code=code)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise


def sweep_expired(db, now=None, *, job_id=None):
    now = now or utcnow()
    try:
        # job→attempt 잠금 순서를 점유·성공 저장·재처리와 일치시킨다.
        query = select(AnalysisJob).where(or_(
            (AnalysisJob.status == 'queued') & (AnalysisJob.queue_deadline_at <= now),
            (AnalysisJob.status == 'running') & AnalysisJob.current_attempt_id.in_(
                select(AnalysisAttempt.id).where(AnalysisAttempt.status == 'running', AnalysisAttempt.lease_expires_at <= now))))
        if job_id is not None:
            query = query.where(AnalysisJob.id == job_id)
        jobs = db.scalars(query
            .order_by(AnalysisJob.id).with_for_update(skip_locked=True).execution_options(populate_existing=True)).all()
        changed = 0
        for job in jobs:
            attempt = _attempt(db, job)
            if job.status == 'queued' and as_utc(job.queue_deadline_at) <= now:
                if attempt is None:
                    attempt = AnalysisAttempt(id=uuid4(), job_id=job.id, attempt_number=_next_number(db, job), status='expired', queued_at=job.queued_at)
                    db.add(attempt); db.flush(); job.current_attempt_id = attempt.id
                if attempt.status not in ('queued', 'expired'):
                    continue
                _finish_failure(job, attempt, 'QUEUE_TIMEOUT', now, expired=True)
                changed += 1
            elif job.status == 'running' and attempt and attempt.status == 'running' and as_utc(attempt.lease_expires_at) <= now:
                _finish_failure(job, attempt, 'WORKER_INTERRUPTED', now, expired=True)
                changed += 1
        db.commit()
        return changed
    except Exception:
        db.rollback()
        raise


def heartbeat(db, worker_id, claim=None, now=None):
    now = now or utcnow()
    try:
        owned = True
        if claim:
            job, attempt = _owned(db, claim)
            owned = bool(job and attempt and attempt.worker_id == worker_id and as_utc(attempt.lease_expires_at) > now)
            if owned:
                attempt.heartbeat_at = now
        _presence(db, 'worker', now, status='up', heartbeat_at=now, error_code=None)
        db.commit()
        return owned
    except Exception:
        db.rollback()
        raise


def snapshot_for(db, claim):
    context = db.scalar(select(AnalysisContext).where(AnalysisContext.submission_id == claim.submission_id))
    if context is None:
        raise ContractError('INVALID_RESULT', ERROR_MESSAGES['INVALID_RESULT'])
    snapshot = context.snapshot
    digest = hashlib.sha256(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    if digest != context.snapshot_sha256:
        raise ContractError('INVALID_RESULT', ERROR_MESSAGES['INVALID_RESULT'])
    return snapshot


def analysis_input(claim, snapshot):
    try:
        return AnalysisInput.model_validate({
            'schema_version': '1.0', 'job_id': str(claim.job_id), 'attempt_id': str(claim.attempt_id),
            'submission_id': str(claim.submission_id), 'question': snapshot['question'],
            'guidelines': snapshot['guidelines'], 'references': snapshot['references'],
            'photos': [{key: photo[key] for key in ('photo_id','position','mime_type','sha256')} for photo in snapshot['photos']],
            'previous_review': snapshot.get('previous_review'),
        })
    except (KeyError, TypeError, ValueError, ValidationError):
        raise ContractError('INVALID_RESULT', ERROR_MESSAGES['INVALID_RESULT']) from None


def _validate_envelope(response, claim):
    required = {'schema_version','job_id','attempt_id','submission_id','model','prompt_version','duration_ms','cli_version','result'}
    if (not isinstance(response, dict) or set(response) != required or response['schema_version'] != '1.0'
        or response['job_id'] != str(claim.job_id)
        or response['attempt_id'] != str(claim.attempt_id) or response['submission_id'] != str(claim.submission_id)
        or type(response['duration_ms']) is not int or response['duration_ms'] < 0
        or any(not isinstance(response[key], str) or not response[key].strip() or len(response[key]) > limit
               for key, limit in (('model',120),('prompt_version',32),('cli_version',120)))):
        raise ContractError('INVALID_RESULT', ERROR_MESSAGES['INVALID_RESULT'])


def complete_attempt(db, claim, response, now=None):
    supplied_time = now
    try:
        job, attempt = _owned(db, claim)
        now = supplied_time or utcnow()
        if job is None or as_utc(attempt.deadline_at) <= now or as_utc(attempt.lease_expires_at) <= now:
            db.commit()
            logger.info('analysis_result_discarded job=%s attempt=%s received_at=%s', claim.job_id, claim.attempt_id, now.isoformat())
            return False
        _validate_envelope(response, claim)
        snapshot = snapshot_for(db, claim)
        context = analysis_input(claim, snapshot)
        result = validate_result(response['result'], context)
        metrics = derive_metrics(result, context)
        review = ReviewResult(id=uuid4(), submission_id=claim.submission_id, attempt_id=claim.attempt_id,
                              schema_version='1.0', result=result.model_dump(), source_kind='real_ai',
                              model_name=response['model'], prompt_version=response['prompt_version'],
                              latency_ms=response['duration_ms'], **metrics)
        db.add(review); db.flush()
        for criterion in result.criteria:
            db.add(CriterionEvaluation(review_id=review.id, guideline_id=UUID(criterion.guideline_id),
                   version_id=UUID(criterion.version_id), rule_key=criterion.rule_key, verdict=criterion.verdict,
                   evidence=[item.model_dump() for item in criterion.evidence], actions=criterion.actions))
        db.flush()
        on_review_ready(db, db.get(Submission, claim.submission_id), review)
        # 결과 검증·후처리 중에도 기한이 지났다면 전체 저장을 취소한다.
        if supplied_time is None and utcnow() >= as_utc(attempt.deadline_at):
            db.rollback()
            logger.info('analysis_result_discarded job=%s attempt=%s reason=deadline', claim.job_id, claim.attempt_id)
            return False
        job.status = attempt.status = 'succeeded'
        job.finished_at = attempt.finished_at = now
        job.error_code = job.error_message = attempt.error_code = attempt.error_message = None
        attempt.result_applied = True
        _presence(db, 'model', now, status='up', last_success_at=now, error_code=None)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
