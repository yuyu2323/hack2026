from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".local" / "runtime.env", extra="ignore")
    ai_service_token: str = Field(default="", repr=False)
    codex_bin: str = "/opt/homebrew/bin/codex"
    codex_model: str = "gpt-6-astra"
    codex_reasoning_effort: str = "low"
    ai_model_timeout_seconds: float = Field(default=120, gt=0, le=120)
    ai_temp_root: Path | None = None
    ai_max_request_bytes: int = 82 * 1024 * 1024


@lru_cache
def get_settings():
    return Settings()
