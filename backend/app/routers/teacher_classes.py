"""
Teacher class + roster basics (Phase 1.4).
"""
from __future__ import annotations

import secrets

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.rate_limiter import enforce_user_rate_limit
from app.services.rbac import evaluate_access

router = APIRouter(prefix="/api/teacher/classes", tags=["teacher-classes"])


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


def _require_teacher_or_admin(request: Request) -> JSONResponse | None:
    user = request.session.get("user")
    decision = evaluate_access(user, ["teacher", "admin"])
    if not decision.allowed:
        return JSONResponse(
            status_code=403,
            content={"error": "Teacher or admin role required", "access": decision.as_dict()},
        )
    return None


def _new_invite_code() -> str:
    return secrets.token_urlsafe(6).replace("-", "").replace("_", "")[:10].upper()


@router.post("")
async def create_class(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    role_response = _require_teacher_or_admin(request)
    if role_response is not None:
        return role_response

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    try:
        body = await request.json()
    except Exception:
        body = {}

    name = (body.get("name") or "").strip()
    if not name:
        return JSONResponse(status_code=400, content={"error": "name is required"})
    subject = (body.get("subject") or "").strip() or None
    grade_level_raw = body.get("grade_level")
    grade_level = None
    if grade_level_raw is not None and str(grade_level_raw).strip() != "":
        try:
            grade_level = int(grade_level_raw)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "grade_level must be an integer"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    invite_code = _new_invite_code()
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO classes (teacher_id, name, subject, grade_level, invite_code)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, teacher_id, name, subject, grade_level, invite_code, created_at
                """,
                tutor_user_id,
                name,
                subject,
                grade_level,
                invite_code,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to create class", "details": str(exc)})

    return {
        "class": {
            "id": row["id"],
            "teacher_id": row["teacher_id"],
            "name": row["name"],
            "subject": row["subject"],
            "grade_level": row["grade_level"],
            "invite_code": row["invite_code"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        }
    }


@router.get("")
async def list_classes(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    role_response = _require_teacher_or_admin(request)
    if role_response is not None:
        return role_response

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT c.id, c.teacher_id, c.name, c.subject, c.grade_level, c.invite_code, c.created_at,
                       COUNT(e.id) AS roster_count
                FROM classes c
                LEFT JOIN class_enrollments e ON e.class_id = c.id
                WHERE c.teacher_id = $1
                GROUP BY c.id
                ORDER BY c.id DESC
                """,
                tutor_user_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to list classes", "details": str(exc)})

    return {
        "classes": [
            {
                "id": row["id"],
                "teacher_id": row["teacher_id"],
                "name": row["name"],
                "subject": row["subject"],
                "grade_level": row["grade_level"],
                "invite_code": row["invite_code"],
                "roster_count": int(row["roster_count"] or 0),
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ]
    }


@router.get("/{class_id:int}")
async def get_class_roster(request: Request, class_id: int):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    role_response = _require_teacher_or_admin(request)
    if role_response is not None:
        return role_response

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            class_row = await conn.fetchrow(
                """
                SELECT id, teacher_id, name, subject, grade_level, invite_code, created_at
                FROM classes
                WHERE id = $1 AND teacher_id = $2
                """,
                class_id,
                tutor_user_id,
            )
            if not class_row:
                return JSONResponse(status_code=404, content={"error": "Class not found"})

            enrollment_rows = await conn.fetch(
                """
                SELECT e.id, e.class_id, e.student_id, e.status, e.enrolled_at,
                       u.display_name, u.grade_level
                FROM class_enrollments e
                JOIN tutor_users u ON u.id = e.student_id
                WHERE e.class_id = $1
                ORDER BY e.id DESC
                """,
                class_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch class", "details": str(exc)})

    return {
        "class": {
            "id": class_row["id"],
            "teacher_id": class_row["teacher_id"],
            "name": class_row["name"],
            "subject": class_row["subject"],
            "grade_level": class_row["grade_level"],
            "invite_code": class_row["invite_code"],
            "created_at": class_row["created_at"].isoformat() if class_row["created_at"] else None,
        },
        "roster": [
            {
                "enrollment_id": row["id"],
                "class_id": row["class_id"],
                "student_id": row["student_id"],
                "status": row["status"],
                "enrolled_at": row["enrolled_at"].isoformat() if row["enrolled_at"] else None,
                "display_name": row["display_name"],
                "grade_level": row["grade_level"],
            }
            for row in enrollment_rows
        ],
    }


@router.post("/{class_id:int}/enroll")
async def enroll_student(request: Request, class_id: int):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    role_response = _require_teacher_or_admin(request)
    if role_response is not None:
        return role_response

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    try:
        body = await request.json()
    except Exception:
        body = {}
    student_id_raw = body.get("student_id")
    if student_id_raw is None:
        return JSONResponse(status_code=400, content={"error": "student_id is required"})
    try:
        student_id = int(student_id_raw)
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "student_id must be an integer"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            class_row = await conn.fetchrow(
                "SELECT id FROM classes WHERE id = $1 AND teacher_id = $2",
                class_id,
                tutor_user_id,
            )
            if not class_row:
                return JSONResponse(status_code=404, content={"error": "Class not found"})

            student_row = await conn.fetchrow(
                "SELECT id, role, display_name, grade_level FROM tutor_users WHERE id = $1",
                student_id,
            )
            if not student_row:
                return JSONResponse(status_code=404, content={"error": "Student user not found"})
            if str(student_row["role"]).lower() != "student":
                return JSONResponse(status_code=400, content={"error": "User is not a student"})

            row = await conn.fetchrow(
                """
                INSERT INTO class_enrollments (class_id, student_id, status)
                VALUES ($1, $2, 'active')
                ON CONFLICT (class_id, student_id)
                DO UPDATE SET status = 'active'
                RETURNING id, class_id, student_id, status, enrolled_at
                """,
                class_id,
                student_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to enroll student", "details": str(exc)})

    return {
        "enrollment": {
            "enrollment_id": row["id"],
            "class_id": row["class_id"],
            "student_id": row["student_id"],
            "status": row["status"],
            "enrolled_at": row["enrolled_at"].isoformat() if row["enrolled_at"] else None,
        }
    }


@router.delete("/{class_id:int}/enrollments/{enrollment_id:int}")
async def remove_enrollment(request: Request, class_id: int, enrollment_id: int):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    role_response = _require_teacher_or_admin(request)
    if role_response is not None:
        return role_response

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            class_row = await conn.fetchrow(
                "SELECT id FROM classes WHERE id = $1 AND teacher_id = $2",
                class_id,
                tutor_user_id,
            )
            if not class_row:
                return JSONResponse(status_code=404, content={"error": "Class not found"})

            result = await conn.execute(
                "DELETE FROM class_enrollments WHERE id = $1 AND class_id = $2",
                enrollment_id,
                class_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to remove enrollment", "details": str(exc)})

    if not result.endswith("1"):
        return JSONResponse(status_code=404, content={"error": "Enrollment not found"})
    return {"ok": True, "class_id": class_id, "enrollment_id": enrollment_id}

