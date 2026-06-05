from functools import lru_cache
import os
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    qwen_api_key: str | None = Field(default=None, alias="QWEN_API_KEY")
    qwen_model: str = Field(default="qwen-plus", alias="QWEN_MODEL")
    qwen_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        alias="QWEN_BASE_URL",
    )
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")
    app_timezone: str = Field(default="Asia/Shanghai", alias="APP_TIMEZONE")
    database_path: str = Field(default="data/calendar.db", alias="DATABASE_PATH")
    app_token: str | None = Field(default=None, alias="APP_TOKEN")
    calendar_token: str = Field(default="change-me", alias="CALENDAR_TOKEN")
    calendar_name: str = Field(default="AI Calendar", alias="CALENDAR_NAME")

    @property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo(self.app_timezone)

    @property
    def effective_qwen_api_key(self) -> str | None:
        return clean_env_value(os.environ.get("QWEN_API_KEY") or self.qwen_api_key)

    @property
    def effective_openai_api_key(self) -> str | None:
        return clean_env_value(os.environ.get("OPENAI_API_KEY") or self.openai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def clean_env_value(value: str | None) -> str | None:
    if value is None:
        return None
    expanded = os.path.expandvars(value.strip()).strip()
    if not expanded or expanded.startswith("$"):
        return None
    return expanded
