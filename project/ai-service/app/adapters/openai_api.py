"""유료 자동 재시도 없이 OpenAI Responses API를 한 번 호출한다."""
import asyncio
import base64
import json
import hashlib
import re
import time

import httpx

from app.adapters.codex import PROMPT_VERSION, build_prompt
from packages.review_contract.errors import ContractError
from packages.review_contract.schema import result_json_schema
from packages.review_contract.validation import parse_result, strict_json_loads, validate_result

ENDPOINT = "https://api.openai.com/v1/responses"


def log_usage(body, request_id, job_id, api_key, *, project=None, organization=None):
    """원문을 복사하지 않고 허용된 식별자와 정수 사용량만 기록한다."""
    def identifier(value, pattern):
        return value if isinstance(value, str) and len(value) <= 256 and re.fullmatch(pattern, value) and api_key not in value else None
    usage = body.get('usage')
    usage = usage if isinstance(usage, dict) else {}
    def tokens(name):
        value = usage.get(name)
        return value if type(value) is int and 0 <= value <= 2**63-1 else None
    record = {
        'event': 'openai_response_usage', 'job_id': str(job_id),
        'model': identifier(body.get('model'), r'[A-Za-z0-9][A-Za-z0-9._:-]{0,119}'),
        'request_id': identifier(request_id, r'req_[A-Za-z0-9_-]+'),
        'response_id': identifier(body.get('id'), r'resp_[A-Za-z0-9_-]+'),
        'project_id': identifier(project, r'proj_[A-Za-z0-9_-]+'),
        'organization_id': identifier(organization, r'org[-_][A-Za-z0-9_-]+'),
        'key_fingerprint': hashlib.sha256(api_key.encode()).hexdigest()[:12],
        'input_tokens': tokens('input_tokens'), 'output_tokens': tokens('output_tokens'),
        'total_tokens': tokens('total_tokens'),
    }
    try:
        print(json.dumps(record, ensure_ascii=True, separators=(',', ':')), flush=True)
    except OSError:
        # 로그 sink 오류로 이미 성공한 유료 분석을 실패시키지 않는다.
        pass


class OpenAIRunner:
    def __init__(self, settings, transport=None):
        self.settings = settings
        self.transport = transport

    def payload(self, context, photos, references):
        if len(photos) != len(context.photos) or len(references) != len(context.references):
            raise ContractError("INVALID_IMAGE", "사진 파일 개수를 확인할 수 없습니다.")
        content = [{"type": "input_text", "text": build_prompt(context)}]
        for metadata, images in ((context.photos, photos), (context.references, references)):
            for item, data in zip(metadata, images):
                encoded = base64.b64encode(data).decode("ascii")
                content.append({"type": "input_image", "image_url": f"data:{item.mime_type};base64,{encoded}", "detail": "auto"})
        return {
            "model": self.settings.openai_model,
            "store": False,
            "max_output_tokens": self.settings.openai_max_output_tokens,
            "input": [{"role": "user", "content": content}],
            "text": {"format": {"type": "json_schema", "name": "storeloop_review", "strict": True, "schema": result_json_schema()}},
        }

    async def analyze(self, context, photos, references):
        if not self.settings.ai_requests_enabled:
            raise ContractError("MODEL_EXECUTION_FAILED", "분석 호출이 비활성화되어 있습니다.")
        key = self.settings.openai_api_key.get_secret_value().strip()
        if not key:
            raise ContractError("MODEL_AUTH_FAILED", "분석 서비스 인증 설정이 필요합니다.")
        payload = self.payload(context, photos, references)
        started = time.monotonic()
        try:
            async with asyncio.timeout(self.settings.ai_model_timeout_seconds):
                async with httpx.AsyncClient(transport=self.transport, timeout=self.settings.ai_model_timeout_seconds,
                                             follow_redirects=False, trust_env=False) as client:
                    async with client.stream("POST", ENDPOINT, json=payload, headers={"Authorization": "Bearer " + key}) as response:
                        if response.status_code in (401, 403):
                            raise ContractError("MODEL_AUTH_FAILED", "분석 서비스 인증을 확인하고 있습니다.")
                        if response.status_code != 200:
                            raise ContractError("MODEL_EXECUTION_FAILED", "분석 서비스 요청을 완료하지 못했습니다.")
                        request_id = response.headers.get('x-request-id')
                        project_id = response.headers.get('openai-project')
                        organization_id = response.headers.get('openai-organization')
                        data = bytearray()
                        async for chunk in response.aiter_bytes():
                            data.extend(chunk)
                            if len(data) > 2 * 1024 * 1024:
                                raise ContractError("INVALID_RESULT", "분석 결과 크기를 초과했습니다.")
        except (TimeoutError, httpx.TimeoutException):
            raise ContractError("MODEL_TIMEOUT", "분석 시간이 초과되었습니다.") from None
        except httpx.RequestError:
            raise ContractError("MODEL_EXECUTION_FAILED", "분석 서비스에 연결하지 못했습니다.") from None
        # 제공자 오류 본문·인증 값·원본 응답은 로그나 오류 메시지에 노출하지 않는다.
        try:
            body = strict_json_loads(bytes(data))
            if body.get("status") != "completed" or body.get("error"):
                raise ValueError
            texts = []
            for item in body["output"]:
                if item.get("type") == "reasoning":
                    continue
                if item.get("type") != "message" or item.get("role") != "assistant" or item.get("status") != "completed":
                    raise ValueError
                for part in item["content"]:
                    if part.get("type") != "output_text":
                        raise ValueError
                    texts.append(part["text"])
            if len(texts) != 1 or not isinstance(texts[0], str):
                raise ValueError
            result = validate_result(parse_result(texts[0].encode()), context)
        except (ValueError, KeyError, TypeError, AttributeError):
            raise ContractError("INVALID_RESULT", "분석 결과 형식과 참조를 확인할 수 없습니다.") from None
        log_usage(body, request_id, context.job_id, key, project=project_id, organization=organization_id)
        return {
            "result": result.model_dump(), "model": self.settings.openai_model,
            "prompt_version": PROMPT_VERSION, "cli_version": "not-applicable:openai-responses",
            "duration_ms": int((time.monotonic() - started) * 1000),
        }
