"""공통 업무 API를 조립한다. AI 모델 호출은 독립 작업자에서만 실행한다."""
from importlib import import_module
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.core.config import get_settings
from server.core.errors import install_error_handlers

app = FastAPI(title='StoreLoop API', version='1.0.0', docs_url=None, redoc_url=None, openapi_url=None)
install_error_handlers(app)
app.add_middleware(CORSMiddleware, allow_origins=get_settings().allowed_origins, allow_credentials=True,
                   allow_methods=['GET','POST','PATCH','PUT','OPTIONS'],
                   allow_headers=['Content-Type','X-CSRF-Token','Idempotency-Key','X-StoreLoop-Role'], expose_headers=['X-Request-ID','Idempotency-Replayed'])
for domain in ('accounts','stores','operations','guidelines','submissions','issues','notifications','dashboard','analytics'):
    app.include_router(import_module('server.' + domain + '.router').router)

@app.get('/health')
def health():
    return {'service': 'storeloop-business', 'status': 'up'}
