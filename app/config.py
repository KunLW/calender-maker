from functools import lru_cache
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
