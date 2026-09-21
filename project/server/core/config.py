"""실행 환경 설정. 실제 비밀은 코드 기본값에 포함하지 않는다."""
from functools import lru_cache
import json
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / '.local/runtime.env', env_file_encoding='utf-8', extra='ignore')
    database_url: str = 'sqlite:///' + str(PROJECT_ROOT / '.local/storeloop.db')
    media_root: Path = PROJECT_ROOT / '.local/media'
    session_cookie_secure: bool = False
    session_cookie_name: str = 'storeloop_session'
    allowed_origins_value: str = Field(default='http://127.0.0.1:5181', validation_alias='ALLOWED_ORIGINS')
    ai_service_url: str = 'http://127.0.0.1:8201'
    ai_service_token: str = ''
    queue_timeout_seconds: int = 180
    model_timeout_seconds: int = 120
    ai_http_timeout_seconds: int = 130
    lease_timeout_seconds: int = 140
    heartbeat_interval_seconds: int = 10

    @property
    def allowed_origins(self) -> list[str]:
        value = self.allowed_origins_value.strip()
        return json.loads(value) if value.startswith('[') else [v.strip().rstrip('/') for v in value.split(',') if v.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
