"""인증된 요청의 ASGI 수명 안에서 지정한 작업 하나만 처리한다."""
import asyncio
import logging
import os
from pathlib import Path
import sys
from uuid import UUID, uuid4

from packages.review_contract.errors import ContractError
from server.analysis_jobs import service, worker
from server.core.db import SessionLocal

logger = logging.getLogger(__name__)


def enabled():
    return os.environ.get('VERCEL_REQUEST_ANALYSIS', '').lower() == 'true'


def ai_settings():
    path = str(Path(__file__).resolve().parents[1] / 'ai-service')
    if path not in sys.path:
        sys.path.insert(0, path)
    from app.config import Settings
    # 로컬 runtime.env를 배포 환경에 섞지 않는다. 비활성화가 기본값이다.
    return Settings(_env_file=None, ai_provider='openai',
                    ai_requests_enabled=os.environ.get('AI_REQUESTS_ENABLED', 'false').lower() == 'true')


async def analyze_in_process(prepared, settings):
    config = ai_settings()
    from app.adapters.openai_api import OpenAIRunner
    from app.services.images import validate_image
    if not config.ai_requests_enabled:
        raise ContractError('MODEL_EXECUTION_FAILED', '분석 호출이 비활성화되어 있습니다.')
    for metadata, images in ((prepared.context.photos, prepared.photos),
                             (prepared.context.references, prepared.references)):
        for item, data in zip(metadata, images):
            suffix = '.png' if item.mime_type == 'image/png' else '.jpg'
            validate_image(data, item, 'image' + suffix)
    result = await OpenAIRunner(config).analyze(prepared.context, prepared.photos, prepared.references)
    context = prepared.context
    return {'schema_version': '1.0', 'job_id': context.job_id,
            'attempt_id': context.attempt_id, 'submission_id': context.submission_id, **result}


def _claim(factory, job_id, worker_id):
    with factory() as db:
        service.sweep_expired(db, job_id=job_id)
        service.heartbeat(db, worker_id)
        return service.claim_next_job(db, worker_id, job_id=job_id)


async def process_job(job_id, *, session_factory=None, analyzer=analyze_in_process):
    """전역 큐를 소비하지 않으며 결과 저장은 기존 소유권 검증을 통과해야 한다."""
    if not enabled():
        return False
    factory = session_factory or SessionLocal
    worker_id = 'request-' + uuid4().hex
    try:
        claim = await asyncio.to_thread(_claim, factory, UUID(str(job_id)), worker_id)
        if claim is None:
            return False
        return await worker.process_claim(claim, session_factory=factory, analyzer=analyzer)
    except asyncio.CancelledError:
        # 다음 인증된 조회에서 만료 lease를 회수한다. 자동 유료 재시도는 없다.
        raise
    except Exception:
        logger.warning('request_analysis_failed')
        return False


def schedule_analysis(background_tasks, job_id):
    """호출부가 계정·작업 접근권한을 검증한 뒤에만 예약한다."""
    if enabled():
        background_tasks.add_task(process_job, UUID(str(job_id)))
