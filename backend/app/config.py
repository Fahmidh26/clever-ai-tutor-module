from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Clever AI Tutor Backend"
    app_env: str = "development"

    session_secret_key: str

    aisite_oauth_base_url: str
    aisite_oauth_internal_url: str
    aisite_oauth_client_id: str
    aisite_oauth_client_secret: str
    aisite_oauth_redirect_uri: str = "http://localhost:8003/oauth/callback"

    frontend_url: str = "http://localhost:5174"
    frontend_post_login_path: str = "/auth/callback"
    allow_origins: str = "http://localhost:5174"

    @field_validator(
        "aisite_oauth_base_url",
        "aisite_oauth_internal_url",
        "frontend_url",
        mode="before",
    )
    @classmethod
    def strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")

    @property
    def allow_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allow_origins.split(",") if origin.strip()]

    @property
    def normalized_post_login_path(self) -> str:
        if self.frontend_post_login_path.startswith("/"):
            return self.frontend_post_login_path
        return f"/{self.frontend_post_login_path}"


settings = Settings()
