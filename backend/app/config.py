from __future__ import annotations

import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Clever AI Tutor Backend"
    app_env: str = "development"
    auth_mode: str = "external_oauth"

    session_secret_key: str

    aisite_oauth_base_url: str = "http://localhost:3000"
    aisite_oauth_internal_url: str = "http://localhost:3000"
    aisite_oauth_client_id: str = ""
    aisite_oauth_client_secret: str = ""
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
    ai_execution_mode: str = "main_site_proxy_only"
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_default_model: str = "gpt-4o-mini"
    llm_request_timeout_seconds: float = 60.0
    llm_retry_attempts: int = 1
    llm_retry_backoff_seconds: float = 0.6
    llm_fallback_models: str = "gpt-4o,gpt-4"
    kb_upload_dir: str = "backend/storage/kb_uploads"
    kb_upload_max_bytes: int = 26214400
    kb_chunk_size_chars: int = 1200
    kb_chunk_overlap_chars: int = 180
    kb_max_chunks_per_document: int = 300
    embedding_model: str = "text-embedding-3-small"
    embedding_timeout_seconds: float = 60.0
    local_dev_login_path: str = "/auth/local-login"
    local_dev_password: str = "devpass123"
    local_dev_accounts_json: str = (
        '[{"root_user_id":101,"email":"student@local.dev","display_name":"Student Demo","role":"student","grade_level":8},'
        '{"root_user_id":102,"email":"teacher@local.dev","display_name":"Teacher Demo","role":"teacher"},'
        '{"root_user_id":103,"email":"parent@local.dev","display_name":"Parent Demo","role":"parent"},'
        '{"root_user_id":104,"email":"admin@local.dev","display_name":"Admin Demo","role":"admin"}]'
    )

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
    def normalized_local_dev_login_path(self) -> str:
        if self.local_dev_login_path.startswith("/"):
            return self.local_dev_login_path
        return f"/{self.local_dev_login_path}"

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

    @property
    def llm_fallback_models_list(self) -> list[str]:
        return [m.strip() for m in self.llm_fallback_models.split(",") if m.strip()]

    @property
    def local_dev_accounts(self) -> list[dict[str, object]]:
        try:
            payload = json.loads(self.local_dev_accounts_json)
        except json.JSONDecodeError:
            return []
        if not isinstance(payload, list):
            return []
        accounts: list[dict[str, object]] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            accounts.append(item)
        return accounts


settings = Settings()
