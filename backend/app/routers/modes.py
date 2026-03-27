"""
Local tutor modes API — 7 interaction modes catalog.
Per ARCHITECTURE.md, runs on tutor site.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.mode_prompts import MODE_DEFINITIONS
from app.services.rate_limiter import enforce_user_rate_limit

router = APIRouter(prefix="/api/tutor", tags=["modes"])


@router.get("/modes")
async def list_modes(request: Request):
    """List available interaction modes. Local implementation."""
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    return {
        "modes": [
            {
                **mode,
                "label": mode.get("name"),
            }
            for mode in MODE_DEFINITIONS
        ]
    }
