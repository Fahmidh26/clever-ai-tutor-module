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
    database_url: str | None = None
    db_pool_min_size: int = 1
    db_pool_max_size: int = 10
    redis_url: str = "redis://localhost:6379/0"
    root_site_jwks_url: str | None = None
    root_site_jwks_path: str = "/.well-known/jwks.json"
    root_site_jwt_issuer: str | None = None
    root_site_jwt_audience: str | None = None
    root_site_jwks_cache_ttl_seconds: int = 300
    root_site_x_auth_hex: str | None = None
    token_estimate_chars_per_token: int = 4
    token_reserve_buffer_ratio: float = 1.15
    token_default_output_tokens: int = 512
    rate_limit_requests_per_window: int = 120
    rate_limit_window_seconds: int = 60

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

    @property
    def resolved_root_site_jwks_url(self) -> str:
        if self.root_site_jwks_url:
            return self.root_site_jwks_url
        return f"{self.aisite_oauth_internal_url}{self.root_site_jwks_path}"

    @property
    def resolved_root_site_jwt_issuer(self) -> str:
        if self.root_site_jwt_issuer:
            return self.root_site_jwt_issuer
        return self.aisite_oauth_base_url


settings = Settings()
