from __future__ import annotations

from app.config import settings
from app.services.root_site_client import RootSiteClient
from app.services.token_service import TokenService
from app.services.tutor_user_sync import TutorUserSyncError, sync_tutor_user_on_login

root_site_client = RootSiteClient(settings=settings)
token_service = TokenService(
    root_site_client=root_site_client,
    chars_per_token=settings.token_estimate_chars_per_token,
    reserve_buffer_ratio=settings.token_reserve_buffer_ratio,
    default_output_tokens=settings.token_default_output_tokens,
)

