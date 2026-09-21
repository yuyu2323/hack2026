"""내부 분석 호출의 multipart·오류·본문 상한을 검증한다. 모델은 호출하지 않는다."""
from uuid import uuid4
import httpx
import pytest
from packages.review_contract.errors import ContractError
from packages.review_contract.models import AnalysisInput
from server.analysis_jobs.worker import PreparedRequest,call_analyzer
from server.core.config import Settings


@pytest.fixture
def request_data():
    context=AnalysisInput.model_validate(dict(schema_version='1.0',job_id=str(uuid4()),attempt_id=str(uuid4()),submission_id=str(uuid4()),question='사진 확인',guidelines=[],photos=[dict(photo_id=str(uuid4()),position=1,mime_type='image/png',sha256='a'*64)],references=[dict(reference_id=str(uuid4()),photo_id=str(uuid4()),position=1,mime_type='image/png',sha256='b'*64,caption='Reference')],previous_review=None))
    return PreparedRequest(context,(b'actual-submission-bytes',),(b'actual-reference-bytes',))


@pytest.mark.asyncio
async def test_internal_request_contains_real_bytes_metadata_and_token(request_data):
    async def handle(request):
        raw=await request.aread()
        assert request.headers['authorization']=='Bearer test-only-token'
        assert b'actual-submission-bytes' in raw and b'actual-reference-bytes' in raw
        assert str(request_data.context.attempt_id).encode() in raw and '사진 확인'.encode() in raw
        assert b'name="photos"' in raw and b'name="references"' in raw
        return httpx.Response(200,json={'result':'test-double'})
    settings=Settings(_env_file=None,ai_service_token='test-only-token')
    async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client:
        assert await call_analyzer(request_data,settings,client=client)=={'result':'test-double'}


@pytest.mark.parametrize('status,body,code',[(409,{'error':{'code':'AI_BUSY','message':'private-body'}},'AI_UNAVAILABLE'),(401,{'error':{'code':'UNAUTHENTICATED','message':'private-body'}},'AI_UNAVAILABLE'),(504,{'error':{'code':'MODEL_TIMEOUT','message':'private-body'}},'MODEL_TIMEOUT'),(502,{'error':{'code':'MODEL_AUTH_FAILED','message':'private-body'}},'MODEL_AUTH_FAILED'),(502,{'error':{'code':'invented','message':'private-body'}},'AI_UNAVAILABLE')])
@pytest.mark.asyncio
async def test_remote_errors_become_safe_known_codes(request_data,status,body,code):
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req:httpx.Response(status,json=body))) as client:
        with pytest.raises(ContractError) as caught:
            await call_analyzer(request_data,Settings(_env_file=None),client=client)
    assert caught.value.code==code and 'private-body' not in str(caught.value)


@pytest.mark.parametrize('raw,code',[(b'{bad','INVALID_JSON'),(b'a'* (600*1024+1),'INVALID_RESULT')])
@pytest.mark.asyncio
async def test_invalid_or_oversized_response_is_rejected(request_data,raw,code):
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req:httpx.Response(200,content=raw))) as client:
        with pytest.raises(ContractError) as caught:
            await call_analyzer(request_data,Settings(_env_file=None),client=client)
    assert caught.value.code==code


@pytest.mark.asyncio
async def test_transport_timeout_is_distinct_from_unavailable(request_data):
    def handler(request): raise httpx.ReadTimeout('private-transport-body',request=request)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(ContractError) as caught:
            await call_analyzer(request_data,Settings(_env_file=None),client=client)
    assert caught.value.code=='MODEL_TIMEOUT' and 'private' not in str(caught.value)
