from __future__ import annotations

from app.config import settings
from app.services.ai_providers.openai_provider import OpenAIProvider
from app.services.ai_providers.registry import ProviderRegistry
from app.services.root_site_client import RootSiteClient
from app.services.token_service import TokenService
from app.services.tutor_user_sync import TutorUserSyncError, sync_tutor_user_on_login

root_site_client = RootSiteClient(settings=settings)
ai_execution_mode = settings.ai_execution_mode
provider_registry = ProviderRegistry()
if settings.openai_api_key:
    provider_registry.register(
        OpenAIProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    )
token_service = TokenService(
    root_site_client=root_site_client,
    chars_per_token=settings.token_estimate_chars_per_token,
    reserve_buffer_ratio=settings.token_reserve_buffer_ratio,
    default_output_tokens=settings.token_default_output_tokens,
)

