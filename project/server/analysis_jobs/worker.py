"""DB 연결을 닫은 뒤 로컬 AI를 호출하는 단일 처리 작업자."""
import argparse
import asyncio
from dataclasses import dataclass
import hashlib
import json
import logging
import signal
import socket
from uuid import UUID, uuid4

import httpx
from sqlalchemy import select

from packages.review_contract.errors import ContractError
from packages.review_contract.models import AnalysisInput
from packages.review_contract.validation import strict_json_loads
from server.analysis_jobs import service
from server.core.config import get_settings
from server.core.db import SessionLocal, utcnow
from server.submissions.models import MediaAsset, SubmissionPhoto
from server.submissions.storage import protected_path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PreparedRequest:
    context: AnalysisInput
    photos: tuple[bytes, ...]
    references: tuple[bytes, ...]


def load_request(db, claim):
    """저장 시점 snapshot과 보호 파일 hash를 확인하고 파일 내용만 반환한다."""
    snapshot = service.snapshot_for(db, claim)
    context = service.analysis_input(claim, snapshot)
    groups = []
    try:
        for name, metadata in (('photos', context.photos), ('references', context.references)):
            images = []
            for index, meta in enumerate(metadata):
                source = snapshot[name][index]
                if name == 'photos':
                    link = db.get(SubmissionPhoto, UUID(meta.photo_id))
                    if (link is None or link.submission_id != claim.submission_id or link.position != meta.position
                        or str(link.media_id) != source['media_id']):
                        raise ValueError('제출 사진 연결 불일치')
                    media_id = link.media_id
                else:
                    media_id = UUID(meta.photo_id)
                media = db.get(MediaAsset, media_id)
                if media is None or media.sha256 != meta.sha256 or media.mime_type != meta.mime_type:
                    raise ValueError('미디어 정보 불일치')
                with protected_path(media).open('rb') as file:
                    data = file.read(10 * 1024 * 1024 + 1)
                if len(data) != media.byte_size or hashlib.sha256(data).hexdigest() != meta.sha256:
                    raise ValueError('파일 hash 불일치')
                images.append(data)
            groups.append(tuple(images))
    except Exception:
        raise ContractError('INVALID_IMAGE', service.ERROR_MESSAGES['INVALID_IMAGE']) from None
    return PreparedRequest(context, groups[0], groups[1])


async def call_analyzer(prepared, settings, *, client=None):
    """내부 토큰과 실제 multipart 파일을 전송하고 원문 오류는 보존하지 않는다."""
    context = prepared.context
    files = []
    for name, metadata, contents in (('photos', context.photos, prepared.photos),
                                     ('references', context.references, prepared.references)):
        for meta, content in zip(metadata, contents):
            extension = 'png' if meta.mime_type == 'image/png' else 'jpg'
            files.append((name, (f'{name}-{meta.position}.{extension}', content, meta.mime_type)))
    owns_client = client is None
    client = client or httpx.AsyncClient(trust_env=False, follow_redirects=False,
                                        timeout=httpx.Timeout(settings.ai_http_timeout_seconds, connect=5))
    try:
        async with client.stream('POST', settings.ai_service_url.rstrip('/') + '/internal/analyze',
                                 headers={'Authorization': 'Bearer ' + settings.ai_service_token},
                                 data={'metadata': context.model_dump_json()}, files=files) as response:
            raw = bytearray()
            async for chunk in response.aiter_bytes():
                raw.extend(chunk)
                if len(raw) > 600 * 1024:
                    raise ContractError('INVALID_RESULT', service.ERROR_MESSAGES['INVALID_RESULT'])
            try:
                result = strict_json_loads(bytes(raw))
            except ContractError:
                code = 'INVALID_JSON' if response.status_code == 200 else 'AI_UNAVAILABLE'
                raise ContractError(code, service.ERROR_MESSAGES[code]) from None
            if response.status_code != 200:
                error = result.get('error', {}) if isinstance(result, dict) else {}
                code = error.get('code') if isinstance(error, dict) else None
                if response.status_code not in (422, 502, 504) or code not in service.ERROR_MESSAGES:
                    code = 'AI_UNAVAILABLE'
                raise ContractError(code, service.ERROR_MESSAGES[code])
            return result
    except httpx.TimeoutException:
        raise ContractError('MODEL_TIMEOUT', service.ERROR_MESSAGES['MODEL_TIMEOUT']) from None
    except httpx.HTTPError:
        raise ContractError('AI_UNAVAILABLE', service.ERROR_MESSAGES['AI_UNAVAILABLE']) from None
    finally:
        if owns_client:
            await client.aclose()


def _database_call(factory, operation, *args, **kwargs):
    with factory() as db:
        return operation(db, *args, **kwargs)


async def _pulse(factory, claim, stop, interval):
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval)
        except asyncio.TimeoutError:
            try:
                await asyncio.to_thread(_database_call, factory, service.heartbeat, claim.worker_id, claim)
            except Exception:
                # DB 재연결 실패도 자격값을 포함할 수 있는 원문 traceback으로 출력하지 않는다.
                logger.warning('worker_heartbeat_failed worker=%s', claim.worker_id)


async def process_claim(claim, *, session_factory=SessionLocal, settings=None, analyzer=call_analyzer):
    settings = settings or get_settings()
    stop_pulse = asyncio.Event()
    pulse = asyncio.create_task(_pulse(session_factory, claim, stop_pulse, settings.heartbeat_interval_seconds))
    try:
        prepared = await asyncio.to_thread(_database_call, session_factory, load_request, claim)
        remaining = (claim.deadline_at - utcnow()).total_seconds()
        if remaining <= 0:
            raise ContractError('MODEL_TIMEOUT', service.ERROR_MESSAGES['MODEL_TIMEOUT'])
        # 사진 읽기 시간까지 포함한 절대 수용 기한이다. 대기 중에는 DB 연결/잠금을 보유하지 않는다.
        response = await asyncio.wait_for(analyzer(prepared, settings), timeout=remaining)
        applied = await asyncio.to_thread(_database_call, session_factory, service.complete_attempt, claim, response)
        if not applied and utcnow() >= claim.deadline_at:
            await asyncio.to_thread(_database_call, session_factory, service.fail_attempt, claim, 'MODEL_TIMEOUT')
        return applied
    except asyncio.CancelledError:
        # 강제 중단에서는 lease 만료와 복구 sweep가 시도를 종료한다.
        raise
    except (ContractError, asyncio.TimeoutError) as exc:
        code = exc.code if isinstance(exc, ContractError) else 'MODEL_TIMEOUT'
        await asyncio.to_thread(_database_call, session_factory, service.fail_attempt, claim, code)
        return False
    except Exception:
        # 원자 저장이 실패하면 rollback된 상태에서 실패 표시를 시도한다. DB 자체 장애는 lease로 복구한다.
        logger.warning('analysis_attempt_failed job=%s attempt=%s', claim.job_id, claim.attempt_id)
        try:
            await asyncio.to_thread(_database_call, session_factory, service.fail_attempt, claim, 'MODEL_EXECUTION_FAILED')
        except Exception:
            logger.warning('analysis_failure_save_failed job=%s attempt=%s', claim.job_id, claim.attempt_id)
        return False
    finally:
        stop_pulse.set()
        await pulse


async def run_worker(*, once=False, session_factory=SessionLocal, settings=None, worker_id=None):
    settings = settings or get_settings()
    worker_id = worker_id or ('local-' + socket.gethostname()[:60] + '-' + uuid4().hex[:12])
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, stop.set)
    logger.info('worker_started worker=%s', worker_id)
    try:
        while not stop.is_set():
            try:
                await asyncio.to_thread(_database_call, session_factory, service.heartbeat, worker_id)
                await asyncio.to_thread(_database_call, session_factory, service.sweep_expired)
                claim = await asyncio.to_thread(_database_call, session_factory, service.claim_next_job, worker_id)
                if claim:
                    # 종료 신호는 신규 점유를 멈추고 현재 분석은 절대 기한 안에 마무리한다.
                    await process_claim(claim, session_factory=session_factory, settings=settings)
                elif not once:
                    try:
                        await asyncio.wait_for(stop.wait(), timeout=2)
                    except asyncio.TimeoutError:
                        pass
            except Exception:
                logger.warning('worker_iteration_failed worker=%s', worker_id)
                if not once:
                    try:
                        await asyncio.wait_for(stop.wait(), timeout=2)
                    except asyncio.TimeoutError:
                        pass
            if once:
                break
    finally:
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.remove_signal_handler(sig)
        logger.info('worker_stopped worker=%s', worker_id)


def main():
    parser = argparse.ArgumentParser(description='StoreLoop 로컬 분석 작업자')
    parser.add_argument('--once', action='store_true', help='복구 sweep와 작업 최대 1건 처리 후 종료')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(name)s %(message)s')
    logging.getLogger('httpx').setLevel(logging.WARNING)
    asyncio.run(run_worker(once=args.once))


if __name__ == '__main__':
    main()
