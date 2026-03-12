"""
Local experts API — per ARCHITECTURE.md, experts run on tutor site, not main site.
Serves tutor personas from tutor_personas table.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.rate_limiter import enforce_user_rate_limit

router = APIRouter(prefix="/api", tags=["experts"])


@router.get("/experts")
async def list_experts(request: Request, domain: str = "expert-chat"):
    """List available tutor personas (experts). Local implementation from tutor_personas."""
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(
            status_code=503,
            content={"error": "Database not configured", "experts": []},
        )

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, slug, name, tagline, avatar_url, personality, teaching_style,
                       subject_expertise, is_custom, sort_order
                FROM tutor_personas
                WHERE is_active = TRUE
                ORDER BY sort_order ASC, name ASC
                """
            )
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to fetch experts", "experts": []},
        )

    experts = []
    for row in rows:
        subject_expertise = row["subject_expertise"]
        if subject_expertise is None:
            subject_expertise = []
        elif isinstance(subject_expertise, str):
            try:
                subject_expertise = json.loads(subject_expertise) if subject_expertise else []
            except Exception:
                subject_expertise = []
        elif not isinstance(subject_expertise, list):
            subject_expertise = list(subject_expertise) if subject_expertise else []
        experts.append({
            "id": row["id"],
            "slug": row["slug"],
            "name": row["name"],
            "tagline": row["tagline"],
            "avatar_url": row["avatar_url"],
            "personality": row["personality"],
            "teaching_style": row["teaching_style"],
            "subject_expertise": subject_expertise or [],
            "is_custom": row["is_custom"],
        })

    return {"experts": experts, "domain": domain}
