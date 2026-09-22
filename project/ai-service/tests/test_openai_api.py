"""외부 통신 없이 API 입력·비용 제어·실패 경계를 검증한다."""
import asyncio
import base64
import copy
import json
import hashlib

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

@pytest.mark.asyncio
async def test_safe_usage_telemetry_preserves_result_contract(context,payload,capsys):
    body=response_body(payload)
    body.update(id='resp_test001',model='gpt-4.1-mini-2025-04-14',usage={
        'input_tokens':1234,'output_tokens':567,'total_tokens':1801,
        'private_metadata':'do-not-log-private-metadata'})
    body['private']='do-not-log-provider-body'
    runner=OpenAIRunner(settings(),httpx.MockTransport(lambda request:httpx.Response(200,json=body,headers={'x-request-id':'req_test001','openai-project':'proj_test001','openai-organization':'org-test001'})))
    result=await runner.analyze(AnalysisInput.model_validate(context),[b'private-photo-bytes'],[b'private-reference-bytes'])
    lines=capsys.readouterr().out.splitlines()
    assert len(lines)==1
    record=json.loads(lines[0])
    assert record=={'event':'openai_response_usage','job_id':context['job_id'],'model':'gpt-4.1-mini-2025-04-14',
                   'request_id':'req_test001','response_id':'resp_test001','input_tokens':1234,'output_tokens':567,'total_tokens':1801,
                   'project_id':'proj_test001','organization_id':'org-test001','key_fingerprint':hashlib.sha256(b'invalid-test-only').hexdigest()[:12]}
    assert set(result)=={'result','model','prompt_version','cli_version','duration_ms'}
    assert result['result']==payload
    for private in ['invalid-test-only','private-photo-bytes','private-reference-bytes','do-not-log',context['question']]:
        assert private not in lines[0]

@pytest.mark.asyncio
async def test_malformed_usage_identifiers_are_not_logged(context,payload,capsys):
    body=response_body(payload)
    body.update(id='resp_invalid-test-only',model='private model\ntext',usage={'input_tokens':True,'output_tokens':-1,'total_tokens':{'private':'value'}})
    runner=OpenAIRunner(settings(),httpx.MockTransport(lambda request:httpx.Response(200,json=body,headers={'x-request-id':'req_invalid-test-only','openai-project':'proj_invalid-test-only','openai-organization':'org-invalid-test-only'})))
    await runner.analyze(AnalysisInput.model_validate(context),[b'p'],[b'r'])
    record=json.loads(capsys.readouterr().out)
    assert all(record[field] is None for field in ('model','response_id','request_id','project_id','organization_id','input_tokens','output_tokens','total_tokens'))

@pytest.mark.asyncio
@pytest.mark.parametrize('case,stage',[('incomplete','response_envelope'),('reference','result_references'),('schema','result_schema')])
async def test_billed_invalid_response_logs_usage_before_validation_failure(context,payload,capsys,case,stage):
    bad=copy.deepcopy(payload)
    if case=='reference':bad['criteria'][0]['evidence'][0]['photo_position']=5
    if case=='schema':bad.pop('summary')
    body=response_body(bad)
    body.update(id='resp_failed001',model='gpt-4.1-mini',usage={'input_tokens':100,'output_tokens':20,'total_tokens':120})
    if case=='incomplete':body['status']='incomplete'
    runner=OpenAIRunner(settings(),httpx.MockTransport(lambda request:httpx.Response(200,json=body,headers={'x-request-id':'req_failed001'})))
    with pytest.raises(ContractError):
        await runner.analyze(AnalysisInput.model_validate(context),[b'private-photo'],[b'private-reference'])
    lines=capsys.readouterr().out.splitlines()
    assert len(lines)==2
    usage,failure=map(json.loads,lines)
    assert usage['event']=='openai_response_usage' and usage['total_tokens']==120
    assert failure=={'event':'openai_response_validation_failed','job_id':context['job_id'],'stage':stage,'code':'INVALID_RESULT'}
    for private in ['invalid-test-only','private-photo','private-reference',context['question']]:
        assert private not in '\n'.join(lines)
