"""실행 환경 설정. 실제 비밀은 코드 기본값에 포함하지 않는다."""
from functools import lru_cache
import json
import os
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / '.local/runtime.env', env_file_encoding='utf-8', extra='ignore')
    database_url: str = 'sqlite:///' + str(PROJECT_ROOT / '.local/storeloop.db')
    media_root: Path = PROJECT_ROOT / '.local/media'
    media_storage: str = 'filesystem'
    media_database_max_bytes: int = 200 * 1024 * 1024
    session_cookie_secure: bool = False
    session_cookie_name: str = 'storeloop_session'
    demo_multi_role_enabled: bool = False
    demo_public_access_enabled: bool = False
    allowed_origins_value: str = Field(
        default_factory=lambda: ('https://' + os.environ['VERCEL_PROJECT_PRODUCTION_URL'])
        if os.environ.get('VERCEL_PROJECT_PRODUCTION_URL') else 'http://127.0.0.1:5182',
        validation_alias='ALLOWED_ORIGINS')
    ai_service_url: str = 'http://127.0.0.1:8202'
    ai_service_token: str = ''
    queue_timeout_seconds: int = 180
    model_timeout_seconds: int = 120
    ai_http_timeout_seconds: int = 130
    lease_timeout_seconds: int = 140
    heartbeat_interval_seconds: int = 10

    @field_validator('database_url')
    @classmethod
    def normalize_postgres_url(cls, value):
        # 관리형 DB의 URL을 설치된 psycopg 3 드라이버로 연결한다.
        if value.startswith(('postgres://', 'postgresql://')):
            return 'postgresql+psycopg://' + value.split('://', 1)[1]
        return value

    @property
    def allowed_origins(self) -> list[str]:
        value = self.allowed_origins_value.strip()
        return json.loads(value) if value.startswith('[') else [v.strip().rstrip('/') for v in value.split(',') if v.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
