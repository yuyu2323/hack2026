import asyncio
import secrets
import shutil
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, Request
from pydantic import ValidationError
from starlette.datastructures import UploadFile
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from app.adapters.codex import CodexRunner
from app.config import get_settings
from app.services.images import validate_image
from packages.review_contract.errors import ContractError
from packages.review_contract.models import AnalysisInput
from packages.review_contract.validation import strict_json_loads, validate_result


def error_response(code, message, status, request_id=None):
    return JSONResponse({"error": {"code": code, "message": message, "request_id": request_id or str(uuid4())}}, status_code=status)


class InternalBoundary:
    def __init__(self, app, settings):
        self.app = app
        self.settings = settings

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["path"] != "/internal/analyze":
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers", []))
        token = self.settings.ai_service_token
        if not token:
            return await error_response("SERVICE_UNAVAILABLE", "내부 분석 인증 설정이 필요합니다.", 503)(scope, receive, send)
        expected = ("Bearer " + token).encode()
        if not secrets.compare_digest(headers.get(b"authorization", b""), expected):
            return await error_response("UNAUTHENTICATED", "내부 인증이 필요합니다.", 401)(scope, receive, send)
        chunks = []
        total = 0
        while True:
            event = await receive()
            if event["type"] == "http.disconnect":
                return
            chunk = event.get("body", b"")
            total += len(chunk)
            if total > self.settings.ai_max_request_bytes:
                return await error_response("FILE_TOO_LARGE", "요청 크기 제한을 초과했습니다.", 413)(scope, receive, send)
            chunks.append(chunk)
            if not event.get("more_body", False):
                break
        body = b"".join(chunks)
        delivered = False

        async def limited_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        return await self.app(scope, limited_receive, send)


def create_app(settings=None, runner=None):
    settings = settings or get_settings()
    runner = runner or CodexRunner(settings)
    app = FastAPI(title="StoreLoop local AI", docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(InternalBoundary, settings=settings)
    app.state.analysis_lock = asyncio.Lock()
    app.state.last_success_at = None
    app.state.last_failure_at = None
    app.state.last_error_code = None

    @app.get("/health")
    async def health():
        return {
            "status": "up", "cli_available": shutil.which(settings.codex_bin) is not None,
            "model_readiness": "unknown" if app.state.last_success_at is None and app.state.last_failure_at is None
            else ("unavailable" if app.state.last_error_code else "available"),
            "busy": app.state.analysis_lock.locked(),
            "last_success_at": app.state.last_success_at, "last_failure_at": app.state.last_failure_at,
            "last_error_code": app.state.last_error_code,
        }

    @app.post("/internal/analyze")
    async def analyze(request: Request):
        request_id = str(uuid4())
        if app.state.analysis_lock.locked():
            return error_response("AI_BUSY", "다른 분석을 처리하고 있습니다.", 409, request_id)
        async with app.state.analysis_lock:
            try:
                async with request.form(max_files=8, max_fields=1, max_part_size=128 * 1024) as form:
                    if set(form) - {"metadata", "photos", "references"} or len(form.getlist("metadata")) != 1:
                        raise ValueError
                    text = form["metadata"]
                    if not isinstance(text, str) or len(text.encode()) > 128 * 1024:
                        raise ValueError
                    try:
                        context = AnalysisInput.model_validate(strict_json_loads(text))
                    except ContractError:
                        raise ValueError("잘못된 요청 JSON") from None
                    groups = []
                    for key, expected in (("photos", context.photos), ("references", context.references)):
                        uploads = form.getlist(key)
                        if len(uploads) != len(expected):
                            raise ValueError
                        images = []
                        for upload, meta in zip(uploads, expected):
                            if not isinstance(upload, UploadFile) or upload.content_type != meta.mime_type:
                                raise ContractError("INVALID_IMAGE", "사진 파일 형식을 확인할 수 없습니다.")
                            data = await upload.read(10 * 1024 * 1024 + 1)
                            images.append(validate_image(data, meta, upload.filename or ""))
                        groups.append(images)
                model_task = asyncio.create_task(runner.analyze(context, groups[0], groups[1]))

                async def disconnected():
                    while True:
                        if (await request.receive())["type"] == "http.disconnect":
                            return

                disconnect_task = asyncio.create_task(disconnected())
                try:
                    completed, _ = await asyncio.wait((model_task, disconnect_task), return_when=asyncio.FIRST_COMPLETED)
                    if model_task not in completed:
                        model_task.cancel()
                        await asyncio.gather(model_task, return_exceptions=True)
                        raise asyncio.CancelledError
                    outcome = await model_task
                finally:
                    for task in (model_task, disconnect_task):
                        if not task.done():
                            task.cancel()
                    await asyncio.gather(model_task, disconnect_task, return_exceptions=True)
                result = validate_result(outcome["result"], context)
                app.state.last_success_at = datetime.now(timezone.utc).isoformat()
                app.state.last_error_code = None
                return {
                    "schema_version": "1.0", "job_id": context.job_id,
                    "attempt_id": context.attempt_id, "submission_id": context.submission_id,
                    **outcome, "result": result.model_dump(),
                }
            except (ValidationError, ValueError, HTTPException) as exc:
                if isinstance(exc, ContractError):
                    code, message = exc.code, exc.message
                    status = 422 if code == "INVALID_IMAGE" else (504 if code == "MODEL_TIMEOUT" else 502)
                else:
                    code, message, status = "INVALID_REQUEST", "입력 metadata와 파일 목록을 확인해 주세요.", 422
                app.state.last_failure_at = datetime.now(timezone.utc).isoformat()
                app.state.last_error_code = code
                return error_response(code, message, status, request_id)
            except asyncio.CancelledError:
                raise
            except Exception:
                app.state.last_failure_at = datetime.now(timezone.utc).isoformat()
                app.state.last_error_code = "MODEL_EXECUTION_FAILED"
                return error_response("MODEL_EXECUTION_FAILED", "분석을 완료하지 못했습니다.", 502, request_id)

    return app


app = create_app()
