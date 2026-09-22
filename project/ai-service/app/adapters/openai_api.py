"""유료 자동 재시도 없이 OpenAI Responses API를 한 번 호출한다."""
import asyncio
import base64
import time

import httpx

from app.adapters.codex import PROMPT_VERSION, build_prompt
from packages.review_contract.errors import ContractError
from packages.review_contract.schema import result_json_schema
from packages.review_contract.validation import parse_result, strict_json_loads, validate_result

ENDPOINT = "https://api.openai.com/v1/responses"


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
        return {
            "result": result.model_dump(), "model": self.settings.openai_model,
            "prompt_version": PROMPT_VERSION, "cli_version": "not-applicable:openai-responses",
            "duration_ms": int((time.monotonic() - started) * 1000),
        }
