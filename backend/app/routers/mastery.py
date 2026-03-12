"""
Phase 2 mastery tracking API.
"""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.mastery_tracking import clamp_mastery
from app.services.rate_limiter import enforce_user_rate_limit

router = APIRouter(prefix="/api/tutor/mastery", tags=["mastery"])


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
async def list_mastery(request: Request, limit: int = 100):
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
                SELECT id, subject, topic, standard_code, mastery_level, reasoning_quality, last_assessed_at
                FROM student_mastery
                WHERE student_id = $1
                ORDER BY last_assessed_at DESC NULLS LAST, id DESC
                LIMIT $2
                """,
                user_id,
                limit,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to load mastery records", "details": str(e)})

    return {
        "mastery": [
            {
                "id": row["id"],
                "subject": row["subject"],
                "topic": row["topic"],
                "standard_code": row["standard_code"],
                "mastery_level": int(row["mastery_level"] or 0),
                "reasoning_quality": int(row["reasoning_quality"] or 0) if row["reasoning_quality"] is not None else None,
                "last_assessed_at": row["last_assessed_at"].isoformat() if row["last_assessed_at"] else None,
            }
            for row in rows
        ]
    }


@router.post("/recompute")
async def recompute_mastery(request: Request):
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
        body = await request.json() if request.headers.get("content-type", "").lower().startswith("application/json") else {}
    except Exception:
        body = {}
    subject = (body.get("subject") or "").strip() or None
    topic = (body.get("topic") or "").strip() or None
    if not subject or not topic:
        return JSONResponse(status_code=400, content={"error": "subject and topic are required"})

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT COUNT(*) AS total,
                       COALESCE(SUM(CASE WHEN is_correct THEN 1 ELSE 0 END), 0) AS correct
                FROM adaptive_quiz_attempts
                WHERE user_id = $1
                  AND subject = $2
                  AND topic = $3
                  AND is_correct IS NOT NULL
                """,
                user_id,
                subject,
                topic,
            )
            total = int(row["total"] or 0)
            correct = int(row["correct"] or 0)
            accuracy = (correct / total) if total > 0 else 0.0
            # Accuracy-to-level mapping for baseline mastery.
            level = clamp_mastery(round(accuracy * 5))
            reasoning_quality = max(1, min(5, round(accuracy * 5))) if total > 0 else 0
            now = datetime.now(UTC)

            updated = await conn.fetchrow(
                """
                INSERT INTO student_mastery (student_id, subject, topic, mastery_level, reasoning_quality, last_assessed_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (student_id, subject, topic)
                DO UPDATE
                SET mastery_level = EXCLUDED.mastery_level,
                    reasoning_quality = EXCLUDED.reasoning_quality,
                    last_assessed_at = EXCLUDED.last_assessed_at
                RETURNING id, mastery_level, reasoning_quality, last_assessed_at
                """,
                user_id,
                subject,
                topic,
                level,
                reasoning_quality if reasoning_quality > 0 else None,
                now,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to recompute mastery", "details": str(e)})

    return {
        "mastery": {
            "id": updated["id"],
            "subject": subject,
            "topic": topic,
            "mastery_level": int(updated["mastery_level"] or 0),
            "reasoning_quality": int(updated["reasoning_quality"] or 0) if updated["reasoning_quality"] is not None else None,
            "last_assessed_at": updated["last_assessed_at"].isoformat() if updated["last_assessed_at"] else None,
            "quiz_total": total,
            "quiz_correct": correct,
            "accuracy": round(accuracy, 4),
        }
    }
