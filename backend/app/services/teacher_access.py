from __future__ import annotations

from typing import Iterable

from fastapi import Request
from fastapi.responses import JSONResponse

from app.services.rbac import AccessDecision, evaluate_access


def get_tutor_user_id(request: Request) -> int | None:
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


def require_authenticated(request: Request) -> JSONResponse | None:
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    return None


def require_roles(request: Request, roles: Iterable[str]) -> tuple[AccessDecision | None, JSONResponse | None]:
    auth_response = require_authenticated(request)
    if auth_response is not None:
        return None, auth_response

    decision = evaluate_access(request.session.get("user"), list(roles))
    if not decision.allowed:
        allowed = ", ".join(roles)
        return decision, JSONResponse(
            status_code=403,
            content={"error": f"{allowed} role required", "access": decision.as_dict()},
        )
    return decision, None


async def teacher_can_view_student(conn, teacher_id: int, student_id: int) -> bool:
    row = await conn.fetchrow(
        """
        SELECT 1
        FROM teacher_student_links
        WHERE teacher_id = $1
          AND student_id = $2
          AND status = 'active'
        """,
        teacher_id,
        student_id,
    )
    if row:
        return True

    row = await conn.fetchrow(
        """
        SELECT 1
        FROM classes c
        JOIN class_enrollments e ON e.class_id = c.id
        WHERE c.teacher_id = $1
          AND e.student_id = $2
          AND e.status = 'active'
        """,
        teacher_id,
        student_id,
    )
    return bool(row)
