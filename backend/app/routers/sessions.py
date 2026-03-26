"""
Local tutor sessions API — per ARCHITECTURE.md, sessions run on tutor site.
Create, list, get sessions from tutor_sessions and tutor_messages.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.mode_prompts import MODE_IDS
from app.services.rate_limiter import enforce_user_rate_limit

router = APIRouter(prefix="/api/tutor", tags=["sessions"])


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


@router.post("/sessions")
async def create_session(request: Request):
    """Create a new tutor session. Local implementation."""
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    try:
        body = await request.json() if request.headers.get("content-type", "").lower().startswith("application/json") else {}
    except Exception:
        body = {}
    persona_id = body.get("persona_id")
    if persona_id is None:
        return JSONResponse(status_code=400, content={"error": "persona_id is required"})
    try:
        persona_id = int(persona_id)
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "persona_id must be an integer"})

    subject = body.get("subject")
    topic = body.get("topic")
    class_id = body.get("class_id")
    mode = (body.get("mode") or "teach_me").strip().lower()
    if mode not in MODE_IDS:
        mode = "teach_me"
    if class_id is not None:
        try:
            class_id = int(class_id)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "class_id must be an integer"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            # Verify persona exists and is active
            persona_row = await conn.fetchrow(
                "SELECT id FROM tutor_personas WHERE id = $1 AND is_active = TRUE",
                persona_id,
            )
            if not persona_row:
                return JSONResponse(status_code=404, content={"error": "Persona not found"})

            if class_id is not None:
                class_row = await conn.fetchrow(
                    """
                    SELECT c.id
                    FROM classes c
                    JOIN class_enrollments e ON e.class_id = c.id
                    WHERE c.id = $1 AND e.student_id = $2 AND e.status = 'active'
                    """,
                    class_id,
                    tutor_user_id,
                )
                if not class_row:
                    return JSONResponse(status_code=404, content={"error": "Class not found or not accessible"})

            row = await conn.fetchrow(
                """
                INSERT INTO tutor_sessions (user_id, persona_id, class_id, subject, topic, mode, status)
                VALUES ($1, $2, $3, $4, $5, $6, 'active')
                RETURNING id, user_id, persona_id, class_id, subject, topic, mode, status, started_at, created_at
                """,
                tutor_user_id,
                persona_id,
                class_id,
                subject,
                topic,
                mode,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to create session", "details": str(e)})

    return {
        "session": {
            "id": row["id"],
            "user_id": row["user_id"],
            "persona_id": row["persona_id"],
            "class_id": row["class_id"],
            "subject": row["subject"],
            "topic": row["topic"],
            "mode": row["mode"],
            "status": row["status"],
            "started_at": row["started_at"].isoformat() if row["started_at"] else None,
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        },
    }


@router.get("/sessions")
async def list_sessions(request: Request, limit: int = 50, offset: int = 0):
    """List tutor sessions for the current user. Local implementation."""
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    limit = max(1, min(100, limit))
    offset = max(0, offset)

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT s.id, s.user_id, s.persona_id, s.class_id, s.subject, s.topic, s.mode, s.status,
                       s.tokens_used, s.started_at, s.ended_at, s.created_at,
                       p.name AS persona_name, p.slug AS persona_slug,
                       c.name AS class_name
                FROM tutor_sessions s
                JOIN tutor_personas p ON p.id = s.persona_id
                LEFT JOIN classes c ON c.id = s.class_id
                WHERE s.user_id = $1
                ORDER BY s.started_at DESC NULLS LAST, s.id DESC
                LIMIT $2 OFFSET $3
                """,
                tutor_user_id,
                limit,
                offset,
            )
            count_row = await conn.fetchrow(
                "SELECT COUNT(*) AS total FROM tutor_sessions WHERE user_id = $1",
                tutor_user_id,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to list sessions", "details": str(e)})

    sessions = []
    for row in rows:
        sessions.append({
            "id": row["id"],
            "user_id": row["user_id"],
            "persona_id": row["persona_id"],
            "persona_name": row["persona_name"],
            "persona_slug": row["persona_slug"],
            "class_id": row["class_id"],
            "class_name": row["class_name"],
            "subject": row["subject"],
            "topic": row["topic"],
            "mode": row["mode"],
            "status": row["status"],
            "tokens_used": row["tokens_used"],
            "started_at": row["started_at"].isoformat() if row["started_at"] else None,
            "ended_at": row["ended_at"].isoformat() if row["ended_at"] else None,
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        })

    total = int(count_row["total"]) if count_row else 0
    return {"sessions": sessions, "total": total, "limit": limit, "offset": offset}


@router.get("/sessions/{session_id:int}")
async def get_session(request: Request, session_id: int):
    """Get a single session with messages. Local implementation."""
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            session_row = await conn.fetchrow(
                """
                SELECT s.id, s.user_id, s.persona_id, s.class_id, s.subject, s.topic, s.mode, s.status,
                       s.tokens_used, s.model_used, s.started_at, s.ended_at, s.created_at,
                       p.name AS persona_name, p.slug AS persona_slug, p.system_prompt,
                       c.name AS class_name
                FROM tutor_sessions s
                JOIN tutor_personas p ON p.id = s.persona_id
                LEFT JOIN classes c ON c.id = s.class_id
                WHERE s.id = $1 AND s.user_id = $2
                """,
                session_id,
                tutor_user_id,
            )
            if not session_row:
                return JSONResponse(status_code=404, content={"error": "Session not found"})

            msg_rows = await conn.fetch(
                """
                SELECT id, session_id, role, content, mode, tokens_used, model_used, created_at
                FROM tutor_messages
                WHERE session_id = $1
                ORDER BY id ASC
                """,
                session_id,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to get session", "details": str(e)})

    messages = []
    for m in msg_rows:
        messages.append({
            "id": m["id"],
            "role": m["role"],
            "content": m["content"],
            "mode": m["mode"],
            "tokens_used": m["tokens_used"],
            "created_at": m["created_at"].isoformat() if m["created_at"] else None,
        })

    return {
        "session": {
            "id": session_row["id"],
            "user_id": session_row["user_id"],
            "persona_id": session_row["persona_id"],
            "persona_name": session_row["persona_name"],
            "persona_slug": session_row["persona_slug"],
            "class_id": session_row["class_id"],
            "class_name": session_row["class_name"],
            "subject": session_row["subject"],
            "topic": session_row["topic"],
            "mode": session_row["mode"],
            "status": session_row["status"],
            "tokens_used": session_row["tokens_used"],
            "model_used": session_row["model_used"],
            "started_at": session_row["started_at"].isoformat() if session_row["started_at"] else None,
            "ended_at": session_row["ended_at"].isoformat() if session_row["ended_at"] else None,
            "created_at": session_row["created_at"].isoformat() if session_row["created_at"] else None,
        },
        "messages": messages,
    }


@router.patch("/sessions/{session_id:int}/mode")
async def set_session_mode(request: Request, session_id: int):
    """Switch interaction mode for a session. Local implementation."""
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    try:
        body = await request.json() if request.headers.get("content-type", "").lower().startswith("application/json") else {}
    except Exception:
        body = {}

    mode = (body.get("mode") or "").strip().lower()
    if not mode:
        return JSONResponse(status_code=400, content={"error": "mode is required"})

    if mode not in MODE_IDS:
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid mode. Valid: {sorted(MODE_IDS)}"},
        )

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE tutor_sessions SET mode = $2
                WHERE id = $1 AND user_id = $3
                RETURNING id, mode
                """,
                session_id,
                mode,
                tutor_user_id,
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Session not found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to update mode", "details": str(e)})

    return {"session_id": session_id, "mode": row["mode"]}
