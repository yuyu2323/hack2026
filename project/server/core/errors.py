"""민감한 입력과 내부 오류를 제외한 공통 HTTP 오류."""
import uuid
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, OperationalError

class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details=None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []


def install_error_handlers(app):
    @app.middleware('http')
    async def request_metadata(request, call_next):
        request.state.request_id = str(uuid.uuid4())
        response = await call_next(request)
        response.headers['X-Request-ID'] = request.state.request_id
        response.headers['Cache-Control'] = 'private, no-store'
        return response

    def payload(request, code, message, details=None):
        return {'error': {'code': code, 'message': message, 'details': details or []},
                'request_id': getattr(request.state,'request_id',str(uuid.uuid4()))}

    @app.exception_handler(ApiError)
    async def api_error(request: Request, error: ApiError):
        return JSONResponse(payload(request,error.code,error.message,error.details),status_code=error.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, error):
        details=[{'field':'.'.join(str(v) for v in item['loc'][1:]), 'message':'입력 형식과 허용 범위를 확인해 주세요.'} for item in error.errors()]
        return JSONResponse(payload(request,'VALIDATION_ERROR','입력값을 확인해 주세요.',details),status_code=422)

    @app.exception_handler(IntegrityError)
    async def integrity_error(request, error):
        return JSONResponse(payload(request,'VERSION_CONFLICT','이미 변경되었거나 중복된 요청입니다.'),status_code=409)

    @app.exception_handler(OperationalError)
    async def unavailable(request, error):
        return JSONResponse(payload(request,'SERVICE_UNAVAILABLE','서비스 연결을 확인하고 있습니다.'),status_code=503)
