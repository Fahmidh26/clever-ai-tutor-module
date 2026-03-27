from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.rate_limiter import enforce_user_rate_limit
from app.services.teacher_access import get_tutor_user_id, require_roles

router = APIRouter(prefix="/api/teacher", tags=["teacher-roster"])


def _new_join_code() -> str:
    return secrets.token_urlsafe(7).replace("-", "").replace("_", "")[:12].upper()


async def _load_roster_payload(conn, teacher_id: int) -> dict[str, object]:
    linked_rows = await conn.fetch(
        """
        SELECT l.id, l.student_id, l.status, l.source, l.created_at,
               u.display_name, u.grade_level,
               COUNT(DISTINCT e.class_id) FILTER (WHERE e.status = 'active') AS class_count
        FROM teacher_student_links l
        JOIN tutor_users u ON u.id = l.student_id
        LEFT JOIN classes c ON c.teacher_id = l.teacher_id
        LEFT JOIN class_enrollments e
          ON e.class_id = c.id
         AND e.student_id = l.student_id
        WHERE l.teacher_id = $1
          AND l.status = 'active'
        GROUP BY l.id, u.display_name, u.grade_level
        ORDER BY u.display_name NULLS LAST, l.id DESC
        """,
        teacher_id,
    )
    request_rows = await conn.fetch(
        """
        SELECT r.id, r.student_id, r.class_id, r.status, r.request_message, r.requested_at,
               u.display_name, u.grade_level, c.name AS class_name, jc.code AS join_code
        FROM teacher_join_requests r
        JOIN tutor_users u ON u.id = r.student_id
        LEFT JOIN classes c ON c.id = r.class_id
        LEFT JOIN teacher_join_codes jc ON jc.id = r.join_code_id
        WHERE r.teacher_id = $1
          AND r.status = 'pending'
        ORDER BY r.requested_at DESC, r.id DESC
        """,
        teacher_id,
    )
    code_rows = await conn.fetch(
        """
        SELECT id, code, status, expires_at, created_at
        FROM teacher_join_codes
        WHERE teacher_id = $1
        ORDER BY created_at DESC, id DESC
        LIMIT 10
        """,
        teacher_id,
    )

    linked_students = []
    unassigned_students = []
    for row in linked_rows:
        item = {
            "link_id": row["id"],
            "student_id": row["student_id"],
            "display_name": row["display_name"],
            "grade_level": row["grade_level"],
            "status": row["status"],
            "source": row["source"],
            "class_count": int(row["class_count"] or 0),
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        }
        linked_students.append(item)
        if int(row["class_count"] or 0) == 0:
            unassigned_students.append(item)

    return {
        "linked_students": linked_students,
        "unassigned_students": unassigned_students,
        "pending_requests": [
            {
                "id": row["id"],
                "student_id": row["student_id"],
                "display_name": row["display_name"],
                "grade_level": row["grade_level"],
                "class_id": row["class_id"],
                "class_name": row["class_name"],
                "status": row["status"],
                "request_message": row["request_message"],
                "join_code": row["join_code"],
                "requested_at": row["requested_at"].isoformat() if row["requested_at"] else None,
            }
            for row in request_rows
        ],
        "join_codes": [
            {
                "id": row["id"],
                "code": row["code"],
                "status": row["status"],
                "expires_at": row["expires_at"].isoformat() if row["expires_at"] else None,
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in code_rows
        ],
    }


@router.get("/roster")
async def get_teacher_roster(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    _, role_response = require_roles(request, ["teacher", "admin"])
    if role_response is not None:
        return role_response

    teacher_id = get_tutor_user_id(request)
    if teacher_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            payload = await _load_roster_payload(conn, teacher_id)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to load teacher roster", "details": str(exc)})

    return payload


@router.post("/roster/link")
async def create_teacher_student_link(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    _, role_response = require_roles(request, ["teacher", "admin"])
    if role_response is not None:
        return role_response

    teacher_id = get_tutor_user_id(request)
    if teacher_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    try:
        body = await request.json()
    except Exception:
        body = {}

    try:
        student_id = int(body.get("student_id"))
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "student_id must be an integer"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            student_row = await conn.fetchrow(
                "SELECT id, role, display_name, grade_level FROM tutor_users WHERE id = $1",
                student_id,
            )
            if not student_row or str(student_row["role"]).lower() != "student":
                return JSONResponse(status_code=404, content={"error": "Student not found"})
            link_row = await conn.fetchrow(
                """
                INSERT INTO teacher_student_links (teacher_id, student_id, status, source, notes_json)
                VALUES ($1, $2, 'active', 'manual', '{}'::jsonb)
                ON CONFLICT (teacher_id, student_id)
                DO UPDATE SET status = 'active', source = 'manual'
                RETURNING id, teacher_id, student_id, status, source, created_at
                """,
                teacher_id,
                student_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to link student", "details": str(exc)})

    return {
        "link": {
            "id": link_row["id"],
            "teacher_id": link_row["teacher_id"],
            "student_id": link_row["student_id"],
            "status": link_row["status"],
            "source": link_row["source"],
            "created_at": link_row["created_at"].isoformat() if link_row["created_at"] else None,
        }
    }


@router.get("/join-codes")
async def list_teacher_join_codes(request: Request):
    payload = await get_teacher_roster(request)
    if isinstance(payload, JSONResponse):
        return payload
    return {"join_codes": payload.get("join_codes", [])}


@router.post("/join-codes")
async def create_teacher_join_code(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    _, role_response = require_roles(request, ["teacher", "admin"])
    if role_response is not None:
        return role_response

    teacher_id = get_tutor_user_id(request)
    if teacher_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    try:
        body = await request.json()
    except Exception:
        body = {}
    expires_in_days = body.get("expires_in_days", 14)
    try:
        expires_in_days = max(1, min(90, int(expires_in_days)))
    except (TypeError, ValueError):
        expires_in_days = 14
    code = _new_join_code()
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO teacher_join_codes (teacher_id, code, status, expires_at, metadata_json)
                VALUES ($1, $2, 'active', $3, '{}'::jsonb)
                RETURNING id, code, status, expires_at, created_at
                """,
                teacher_id,
                code,
                expires_at,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to create join code", "details": str(exc)})

    return {
        "join_code": {
            "id": row["id"],
            "code": row["code"],
            "status": row["status"],
            "expires_at": row["expires_at"].isoformat() if row["expires_at"] else None,
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        }
    }


@router.get("/join-requests")
async def list_teacher_join_requests(request: Request):
    payload = await get_teacher_roster(request)
    if isinstance(payload, JSONResponse):
        return payload
    return {"join_requests": payload.get("pending_requests", [])}


@router.post("/join-requests")
async def create_teacher_join_request(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    decision, role_response = require_roles(request, ["student", "parent", "teacher", "admin"])
    if role_response is not None:
        return role_response

    actor_role = (decision.user_role or "").lower() if decision else ""
    actor_id = get_tutor_user_id(request)
    if actor_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    try:
        body = await request.json()
    except Exception:
        body = {}

    join_code = str(body.get("join_code") or "").strip().upper()
    request_message = str(body.get("request_message") or "").strip() or None
    class_id_raw = body.get("class_id")
    class_id = None
    if class_id_raw not in (None, ""):
        try:
            class_id = int(class_id_raw)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "class_id must be an integer"})

    student_id = actor_id
    if actor_role in {"parent", "teacher", "admin"}:
        try:
            student_id = int(body.get("student_id"))
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "student_id must be provided for non-student actors"})

    if not join_code:
        return JSONResponse(status_code=400, content={"error": "join_code is required"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            code_row = await conn.fetchrow(
                """
                SELECT id, teacher_id, code, status, expires_at
                FROM teacher_join_codes
                WHERE code = $1
                """,
                join_code,
            )
            if not code_row:
                return JSONResponse(status_code=404, content={"error": "Join code not found"})
            if code_row["status"] != "active":
                return JSONResponse(status_code=400, content={"error": "Join code is not active"})
            if code_row["expires_at"] and code_row["expires_at"] < datetime.now(timezone.utc):
                return JSONResponse(status_code=400, content={"error": "Join code has expired"})

            student_row = await conn.fetchrow(
                "SELECT id, role FROM tutor_users WHERE id = $1",
                student_id,
            )
            if not student_row or str(student_row["role"]).lower() != "student":
                return JSONResponse(status_code=404, content={"error": "Student not found"})

            if class_id is not None:
                class_row = await conn.fetchrow(
                    "SELECT id FROM classes WHERE id = $1 AND teacher_id = $2",
                    class_id,
                    code_row["teacher_id"],
                )
                if not class_row:
                    return JSONResponse(status_code=404, content={"error": "Class not found for this teacher"})

            row = await conn.fetchrow(
                """
                INSERT INTO teacher_join_requests (teacher_id, student_id, join_code_id, class_id, status, request_message)
                VALUES ($1, $2, $3, $4, 'pending', $5)
                ON CONFLICT (teacher_id, student_id, class_id)
                DO UPDATE SET status = 'pending', request_message = EXCLUDED.request_message, requested_at = NOW()
                RETURNING id, teacher_id, student_id, class_id, status, requested_at
                """,
                code_row["teacher_id"],
                student_id,
                code_row["id"],
                class_id,
                request_message,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to create join request", "details": str(exc)})

    return {
        "join_request": {
            "id": row["id"],
            "teacher_id": row["teacher_id"],
            "student_id": row["student_id"],
            "class_id": row["class_id"],
            "status": row["status"],
            "requested_at": row["requested_at"].isoformat() if row["requested_at"] else None,
        }
    }


@router.post("/join-requests/{request_id:int}/approve")
async def approve_teacher_join_request(request: Request, request_id: int):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    _, role_response = require_roles(request, ["teacher", "admin"])
    if role_response is not None:
        return role_response

    teacher_id = get_tutor_user_id(request)
    if teacher_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            request_row = await conn.fetchrow(
                """
                SELECT id, teacher_id, student_id, class_id, status
                FROM teacher_join_requests
                WHERE id = $1 AND teacher_id = $2
                """,
                request_id,
                teacher_id,
            )
            if not request_row:
                return JSONResponse(status_code=404, content={"error": "Join request not found"})
            if request_row["status"] != "pending":
                return JSONResponse(status_code=400, content={"error": "Join request is not pending"})

            await conn.execute(
                """
                INSERT INTO teacher_student_links (teacher_id, student_id, status, source, notes_json)
                VALUES ($1, $2, 'active', 'approved-request', '{}'::jsonb)
                ON CONFLICT (teacher_id, student_id)
                DO UPDATE SET status = 'active', source = 'approved-request'
                """,
                teacher_id,
                request_row["student_id"],
            )

            if request_row["class_id"] is not None:
                await conn.execute(
                    """
                    INSERT INTO class_enrollments (class_id, student_id, status)
                    VALUES ($1, $2, 'active')
                    ON CONFLICT (class_id, student_id)
                    DO UPDATE SET status = 'active'
                    """,
                    request_row["class_id"],
                    request_row["student_id"],
                )

            await conn.execute(
                """
                UPDATE teacher_join_requests
                SET status = 'approved', reviewed_by = $2, reviewed_at = NOW()
                WHERE id = $1
                """,
                request_id,
                teacher_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to approve join request", "details": str(exc)})

    return {"ok": True, "request_id": request_id}


@router.post("/join-requests/{request_id:int}/reject")
async def reject_teacher_join_request(request: Request, request_id: int):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    _, role_response = require_roles(request, ["teacher", "admin"])
    if role_response is not None:
        return role_response

    teacher_id = get_tutor_user_id(request)
    if teacher_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE teacher_join_requests
                SET status = 'rejected', reviewed_by = $2, reviewed_at = NOW()
                WHERE id = $1 AND teacher_id = $2 AND status = 'pending'
                """,
                request_id,
                teacher_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to reject join request", "details": str(exc)})

    if not result.endswith("1"):
        return JSONResponse(status_code=404, content={"error": "Pending join request not found"})
    return {"ok": True, "request_id": request_id}
