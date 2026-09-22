"""Vercel의 공개 업무 API 진입점. 내부 AI 라우트는 공개하지 않는다."""
from server.main import app
from fastapi.staticfiles import StaticFiles
from server.core.config import PROJECT_ROOT

# API 라우트를 먼저 등록한 뒤 빌드된 프론트 파일만 공개한다.
app.mount('/', StaticFiles(directory=PROJECT_ROOT / 'public', html=True, check_dir=False), name='frontend')
