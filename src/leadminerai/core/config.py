from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = Field(default="LeadMinerAI", alias="APP_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    database_url: str = Field(alias="DATABASE_URL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    tavily_api_key: str = Field(alias="TAVILY_API_KEY")
    tavily_base_url: str = Field(default="https://api.tavily.com", alias="TAVILY_BASE_URL")
    tavily_search_depth: str = Field(default="advanced", alias="TAVILY_SEARCH_DEPTH")
    tavily_max_results: int = Field(default=5, alias="TAVILY_MAX_RESULTS")
    search_concurrency: int = Field(default=5, alias="SEARCH_CONCURRENCY")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_serialize: bool = Field(default=False, alias="LOG_SERIALIZE")
    google_client_id: str | None = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: str | None = Field(default=None, alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(default="http://localhost:8000/api/gmail/oauth2callback", alias="GOOGLE_REDIRECT_URI")
    gmail_encryption_key: str | None = Field(default=None, alias="GMAIL_ENCRYPTION_KEY")



@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
