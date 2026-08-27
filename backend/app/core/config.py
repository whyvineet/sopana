from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="openai/gpt-4o-mini", alias="OPENROUTER_MODEL")
    openrouter_http_referer: str = Field(default="http://localhost:5173", alias="OPENROUTER_HTTP_REFERER")
    openrouter_app_title: str = Field(default="SOPANA", alias="OPENROUTER_APP_TITLE")
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )

    supabase_url: str = Field(default="", alias="SUPABASE_URL")
    supabase_publishable_key: str = Field(default="", alias="SUPABASE_PUBLISHABLE_KEY")
    supabase_secret_key: str = Field(default="", alias="SUPABASE_SECRET_KEY")
    supabase_jwks_url: str = Field(default="", alias="SUPABASE_JWKS_URL")

    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")
    search_timeout_seconds: int = Field(default=10, alias="SEARCH_TIMEOUT_SECONDS")
    search_max_results: int = Field(default=5, alias="SEARCH_MAX_RESULTS")
    research_cache_ttl_hours: int = Field(default=24, alias="RESEARCH_CACHE_TTL_HOURS")
    max_path_repair_iterations: int = Field(default=2, alias="MAX_PATH_REPAIR_ITERATIONS")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_secret_key)

    @property
    def tavily_configured(self) -> bool:
        return bool(self.tavily_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
