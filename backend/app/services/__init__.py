from __future__ import annotations

from app.config import settings
from app.services.root_site_client import RootSiteClient

root_site_client = RootSiteClient(settings=settings)

