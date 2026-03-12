"""
Phase 2 misconception detection API.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.rate_limiter import enforce_user_rate_limit

router = APIRouter(prefix="/api/tutor/misconceptions", tags=["misconceptions"])


def _get_tutor_user_id(request: Request) -> int | None:
    user = request.session.get("user")
    if not user:
        return None
    tutor_user = user.get("tutor_user")
    if not isinstance(tutor_user, dict):
        return None
    tid = tutor_user.get("tutor_user_id")
    if tid is None:
        return None
    try:
        return int(tid)
    except (TypeError, ValueError):
        return None


@router.get("")
async def list_misconceptions(request: Request, include_resolved: bool = False, limit: int = 100):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    user_id = _get_tutor_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})
    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})
    limit = max(1, min(500, limit))

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, subject, topic, misconception_type, description, detected_at, resolved_at
                FROM misconception_log
                WHERE student_id = $1
                  AND ($2::BOOLEAN = TRUE OR resolved_at IS NULL)
                ORDER BY detected_at DESC, id DESC
                LIMIT $3
                """,
                user_id,
                include_resolved,
                limit,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to load misconceptions", "details": str(e)})

    return {
        "misconceptions": [
            {
                "id": row["id"],
                "subject": row["subject"],
                "topic": row["topic"],
                "misconception_type": row["misconception_type"],
                "description": row["description"],
                "detected_at": row["detected_at"].isoformat() if row["detected_at"] else None,
                "resolved_at": row["resolved_at"].isoformat() if row["resolved_at"] else None,
            }
            for row in rows
        ]
    }


@router.post("/{misconception_id:int}/resolve")
async def resolve_misconception(request: Request, misconception_id: int):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    user_id = _get_tutor_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})
    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE misconception_log
                SET resolved_at = NOW()
                WHERE id = $1 AND student_id = $2
                RETURNING id, resolved_at
                """,
                misconception_id,
                user_id,
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Misconception not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to resolve misconception", "details": str(e)})

    return {"misconception_id": row["id"], "resolved_at": row["resolved_at"].isoformat() if row["resolved_at"] else None}
