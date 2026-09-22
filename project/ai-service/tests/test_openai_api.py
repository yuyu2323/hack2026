"""외부 통신 없이 API 입력·비용 제어·실패 경계를 검증한다."""
import asyncio
import base64
import copy
import json

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError

from app.adapters.openai_api import OpenAIRunner
from app.config import Settings
from app.main import create_app
from packages.review_contract.errors import ContractError
from packages.review_contract.models import AnalysisInput


def settings(**kwargs):
    return Settings(_env_file=None, ai_provider="openai", openai_api_key=SecretStr("invalid-test-only"), **kwargs)


def response_body(payload):
    return {"status": "completed", "output": [{"type": "message", "role": "assistant", "status": "completed", "content": [{"type": "output_text", "text": json.dumps(payload)}]}]}


@pytest.mark.asyncio
async def test_exact_images_schema_no_store_and_single_request(context, payload):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=response_body(payload))
    runner = OpenAIRunner(settings(openai_max_output_tokens=4000), httpx.MockTransport(handler))
    result = await runner.analyze(AnalysisInput.model_validate(context), [b"photo"], [b"reference"])
    assert result["result"] == payload
    assert result["cli_version"] == "not-applicable:openai-responses"
    assert len(calls) == 1
    body = json.loads(calls[0].content)
    assert str(calls[0].url) == "https://api.openai.com/v1/responses"
    assert body["store"] is False and body["max_output_tokens"] == 4000
    assert "tools" not in body
    assert body["text"]["format"]["strict"] is True
    assert body["text"]["format"]["schema"]["additionalProperties"] is False
    content = body["input"][0]["content"]
    assert context["question"] in content[0]["text"]
    assert context["guidelines"][0]["text"] in content[0]["text"]
    assert [base64.b64decode(x["image_url"].split(",",1)[1]) for x in content[1:]] == [b"photo", b"reference"]


@pytest.mark.asyncio
@pytest.mark.parametrize("status,code", [(401,"MODEL_AUTH_FAILED"),(403,"MODEL_AUTH_FAILED"),(429,"MODEL_EXECUTION_FAILED"),(500,"MODEL_EXECUTION_FAILED"),(302,"MODEL_EXECUTION_FAILED")])
async def test_errors_are_redacted_and_never_retried(context, status, code):
    calls=[]
    def handler(request):
        calls.append(request)
        return httpx.Response(status, text="provider-private-message", headers={"Location":"https://other.invalid"})
    runner=OpenAIRunner(settings(),httpx.MockTransport(handler))
    with pytest.raises(ContractError) as error:
        await runner.analyze(AnalysisInput.model_validate(context),[b"p"],[b"r"])
    assert error.value.code==code
    assert "provider-private-message" not in str(error.value)
    assert len(calls)==1


@pytest.mark.asyncio
@pytest.mark.parametrize("case",["disabled","missing-key","count"])
async def test_configuration_and_input_fail_before_network(context,case):
    config=settings()
    if case=="disabled":config.ai_requests_enabled=False
    if case=="missing-key":config.openai_api_key=SecretStr("")
    def handler(_):pytest.fail("통신이 발생하면 안 됩니다.")
    with pytest.raises(ContractError):
        await OpenAIRunner(config,httpx.MockTransport(handler)).analyze(AnalysisInput.model_validate(context),[] if case=="count" else [b"p"],[b"r"])


@pytest.mark.asyncio
@pytest.mark.parametrize("case",["incomplete","refusal","tool","invalid-json","reference","large","array"])
async def test_invalid_responses_are_not_repaired(context,payload,case):
    body=response_body(payload)
    if case=="incomplete":body["status"]="incomplete"
    if case=="refusal":body["output"][0]["content"]=[{"type":"refusal","refusal":"no"}]
    if case=="tool":body["output"][0]["type"]="function_call"
    if case=="invalid-json":body["output"][0]["content"][0]["text"]="not json"
    if case=="reference":
        bad=copy.deepcopy(payload);bad["criteria"][0]["evidence"][0]["photo_position"]=5
        body=response_body(bad)
    if case=="array":body=[]
    calls=[]
    def handler(request):
        calls.append(request)
        return httpx.Response(200,content=b"x"*(2*1024*1024+1)) if case=="large" else httpx.Response(200,json=body)
    with pytest.raises(ContractError) as error:
        await OpenAIRunner(settings(),httpx.MockTransport(handler)).analyze(AnalysisInput.model_validate(context),[b"p"],[b"r"])
    assert error.value.code=="INVALID_RESULT"
    assert len(calls)==1


@pytest.mark.asyncio
async def test_total_timeout_cancels_without_retry(context):
    calls=[]
    async def handler(request):
        calls.append(request);await asyncio.sleep(1)
        return httpx.Response(200,json={})
    with pytest.raises(ContractError) as error:
        await OpenAIRunner(settings(ai_model_timeout_seconds=.01),httpx.MockTransport(handler)).analyze(AnalysisInput.model_validate(context),[b"p"],[b"r"])
    assert error.value.code=="MODEL_TIMEOUT" and len(calls)==1


def test_provider_configuration_and_health_do_not_call_external_api(monkeypatch):
    def no_network(*args,**kwargs):pytest.fail("외부 API 호출 금지")
    monkeypatch.setattr(httpx.AsyncClient,"stream",no_network)
    client=TestClient(create_app(settings(ai_requests_enabled=False,ai_service_token="invalid-internal-test")))
    data=client.get("/health").json()
    assert data["provider"]=="openai" and data["configuration_ready"]
    assert not data["cli_available"] and data["model_readiness"]=="unknown"
    result=client.post("/internal/analyze",headers={"Authorization":"Bearer invalid-internal-test"})
    assert result.status_code==503
    assert "invalid-test-only" not in str(data)
    with pytest.raises(ValidationError):Settings(_env_file=None,ai_provider="typo")
