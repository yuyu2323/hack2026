"""최종 독립 검토에서 발견한 내부 상태조회 프록시 경계 재현."""
import httpx

from server.core.config import get_settings
from server.operations import service


def test_internal_health_does_not_route_bearer_token_to_environment_proxy(db, monkeypatch):
    # 실제 연결 없이 HTTPX가 선택한 transport만 관찰한다.
    monkeypatch.setenv('HTTP_PROXY', 'http://proxy.invalid:8888')
    monkeypatch.setenv('HTTPS_PROXY', 'http://proxy.invalid:8888')
    monkeypatch.setenv('ALL_PROXY', 'http://proxy.invalid:8888')
    monkeypatch.delenv('NO_PROXY', raising=False)
    monkeypatch.delenv('no_proxy', raising=False)
    settings=get_settings()
    monkeypatch.setattr(settings, 'ai_service_url', 'http://127.0.0.1:8010')
    monkeypatch.setattr(settings, 'ai_service_token', 'external-invalid-review-token')
    transports=[]

    def inspect_transport(transport, request):
        transports.append(type(transport._pool).__name__)
        return httpx.Response(200, json={'status':'up'}, request=request)

    monkeypatch.setattr(httpx.HTTPTransport, 'handle_request', inspect_transport)
    result=service.service_dashboard(db)
    assert next(row for row in result['services'] if row['name']=='ai')['status']=='up'
    assert transports == ['ConnectionPool']
