"""
Phase 2 Hint Progression API.
Additive endpoints that enforce 3-level hint sequencing per problem.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.hint_progression import generate_hint
from app.services.rate_limiter import enforce_user_rate_limit

router = APIRouter(prefix="/api/tutor", tags=["hints"])


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


def _serialize_progression(row) -> dict[str, object]:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "session_id": row["session_id"],
        "subject": row["subject"],
        "topic": row["topic"],
        "problem_text": row["problem_text"],
        "current_level": row["current_level"],
        "status": row["status"],
        "last_hint": row["last_hint"],
        "model_used": row["model_used"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
    }


@router.post("/hints/start")
async def start_hint_progression(request: Request):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        body = await request.json() if request.headers.get("content-type", "").lower().startswith("application/json") else {}
    except Exception:
        body = {}

    problem_text = (body.get("problem_text") or body.get("problem") or "").strip()
    if not problem_text:
        return JSONResponse(status_code=400, content={"error": "problem_text is required"})

    session_id = body.get("session_id")
    subject = (body.get("subject") or "").strip() or None
    topic = (body.get("topic") or "").strip() or None
    grade_level = None
    if session_id is not None:
        try:
            session_id = int(session_id)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "session_id must be an integer"})

    try:
        async with db_pool.acquire() as conn:
            if session_id is not None:
                session_row = await conn.fetchrow(
                    """
                    SELECT id, subject, topic, grade_level
                    FROM tutor_sessions
                    WHERE id = $1 AND user_id = $2
                    """,
                    session_id,
                    tutor_user_id,
                )
                if not session_row:
                    return JSONResponse(status_code=404, content={"error": "Session not found"})
                subject = subject or session_row["subject"]
                topic = topic or session_row["topic"]
                grade_level = session_row["grade_level"]

            hint = await generate_hint(
                problem_text=problem_text,
                level=1,
                subject=subject,
                topic=topic,
                grade_level=grade_level,
            )

            row = await conn.fetchrow(
                """
                INSERT INTO hint_progressions (
                    user_id, session_id, subject, topic, problem_text, current_level, status, last_hint, model_used
                )
                VALUES ($1, $2, $3, $4, $5, 1, 'active', $6, $7)
                RETURNING id, user_id, session_id, subject, topic, problem_text, current_level, status,
                          last_hint, model_used, created_at, updated_at
                """,
                tutor_user_id,
                session_id,
                subject,
                topic,
                problem_text,
                hint.hint,
                hint.model_used,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to start hint progression", "details": str(e)})

    return {
        "progression": _serialize_progression(row),
        "hint": hint.hint,
        "execution_attempts": hint.execution_attempts,
        "can_request_next": True,
    }


@router.post("/hints/{progression_id:int}/next")
async def next_hint(request: Request, progression_id: int):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, user_id, session_id, subject, topic, problem_text, current_level, status,
                       last_hint, model_used, created_at, updated_at
                FROM hint_progressions
                WHERE id = $1 AND user_id = $2
                """,
                progression_id,
                tutor_user_id,
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Hint progression not found"})

            current_level = int(row["current_level"] or 1)
            if current_level >= 3:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Hint progression already reached level 3", "current_level": current_level},
                )

            grade_level = None
            if row["session_id"] is not None:
                session_row = await conn.fetchrow(
                    "SELECT grade_level FROM tutor_sessions WHERE id = $1 AND user_id = $2",
                    row["session_id"],
                    tutor_user_id,
                )
                if session_row:
                    grade_level = session_row["grade_level"]

            next_level_value = current_level + 1
            prior_hints = [row["last_hint"]] if row["last_hint"] else []
            hint = await generate_hint(
                problem_text=row["problem_text"],
                level=next_level_value,
                subject=row["subject"],
                topic=row["topic"],
                grade_level=grade_level,
                prior_hints=prior_hints,
            )

            updated = await conn.fetchrow(
                """
                UPDATE hint_progressions
                SET current_level = $2,
                    status = CASE WHEN $2 >= 3 THEN 'completed' ELSE 'active' END,
                    last_hint = $3,
                    model_used = $4,
                    updated_at = NOW()
                WHERE id = $1 AND user_id = $5
                RETURNING id, user_id, session_id, subject, topic, problem_text, current_level, status,
                          last_hint, model_used, created_at, updated_at
                """,
                progression_id,
                next_level_value,
                hint.hint,
                hint.model_used,
                tutor_user_id,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to generate next hint", "details": str(e)})

    return {
        "progression": _serialize_progression(updated),
        "hint": hint.hint,
        "execution_attempts": hint.execution_attempts,
        "can_request_next": int(updated["current_level"]) < 3,
    }


@router.get("/hints/{progression_id:int}")
async def get_hint_progression(request: Request, progression_id: int):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, user_id, session_id, subject, topic, problem_text, current_level, status,
                       last_hint, model_used, created_at, updated_at
                FROM hint_progressions
                WHERE id = $1 AND user_id = $2
                """,
                progression_id,
                tutor_user_id,
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Hint progression not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch hint progression", "details": str(e)})

    return {"progression": _serialize_progression(row), "can_request_next": int(row["current_level"]) < 3}
