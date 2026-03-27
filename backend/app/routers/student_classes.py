from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.rate_limiter import enforce_user_rate_limit
from app.services.rbac import evaluate_access

router = APIRouter(prefix="/api/tutor/classes", tags=["student-classes"])


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
async def list_student_classes(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    decision = evaluate_access(request.session.get("user"), ["student", "teacher", "admin"])
    if not decision.allowed:
        return JSONResponse(status_code=403, content={"error": "Student, teacher, or admin role required", "access": decision.as_dict()})

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            role = decision.user_role or ""
            if role in {"teacher", "admin"}:
                class_rows = await conn.fetch(
                    """
                    SELECT c.id, c.name, c.subject, c.grade_level, c.invite_code,
                           t.display_name AS teacher_name,
                           COUNT(DISTINCT e.id) AS roster_count,
                           COUNT(DISTINCT a.id) AS assigned_kb_count
                    FROM classes c
                    JOIN tutor_users t ON t.id = c.teacher_id
                    LEFT JOIN class_enrollments e ON e.class_id = c.id AND e.status = 'active'
                    LEFT JOIN kb_class_assignments a ON a.class_id = c.id
                    WHERE c.teacher_id = $1
                    GROUP BY c.id, t.display_name
                    ORDER BY c.id DESC
                    """,
                    tutor_user_id,
                )
            else:
                class_rows = await conn.fetch(
                    """
                    SELECT c.id, c.name, c.subject, c.grade_level, c.invite_code,
                           t.display_name AS teacher_name,
                           COUNT(DISTINCT e2.id) AS roster_count,
                           COUNT(DISTINCT a.id) AS assigned_kb_count
                    FROM class_enrollments e
                    JOIN classes c ON c.id = e.class_id
                    JOIN tutor_users t ON t.id = c.teacher_id
                    LEFT JOIN class_enrollments e2 ON e2.class_id = c.id AND e2.status = 'active'
                    LEFT JOIN kb_class_assignments a ON a.class_id = c.id
                    WHERE e.student_id = $1 AND e.status = 'active'
                    GROUP BY c.id, t.display_name
                    ORDER BY c.id DESC
                    """,
                    tutor_user_id,
                )

            class_ids = [int(row["id"]) for row in class_rows]
            kb_rows = await conn.fetch(
                """
                SELECT a.class_id, kb.id, kb.name, kb.subject, kb.description, kb.visibility,
                       COUNT(DISTINCT d.id) AS document_count
                FROM kb_class_assignments a
                JOIN knowledge_bases kb ON kb.id = a.kb_id
                LEFT JOIN kb_documents d ON d.kb_id = kb.id
                WHERE a.class_id = ANY($1::INT[])
                GROUP BY a.class_id, kb.id
                ORDER BY kb.name ASC
                """,
                class_ids or [0],
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch classes", "details": str(exc)})

    kb_map: dict[int, list[dict[str, object]]] = {}
    for row in kb_rows:
        class_id = int(row["class_id"])
        kb_map.setdefault(class_id, []).append(
            {
                "id": row["id"],
                "name": row["name"],
                "subject": row["subject"],
                "description": row["description"],
                "visibility": row["visibility"],
                "document_count": int(row["document_count"] or 0),
            }
        )

    return {
        "classes": [
            {
                "id": row["id"],
                "name": row["name"],
                "subject": row["subject"],
                "grade_level": row["grade_level"],
                "invite_code": row["invite_code"],
                "teacher_name": row["teacher_name"],
                "roster_count": int(row["roster_count"] or 0),
                "assigned_kb_count": int(row["assigned_kb_count"] or 0),
                "assigned_kbs": kb_map.get(int(row["id"]), []),
            }
            for row in class_rows
        ]
    }


@router.post("/join")
async def join_class_with_invite(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    decision = evaluate_access(request.session.get("user"), ["student", "admin"])
    if not decision.allowed:
        return JSONResponse(status_code=403, content={"error": "Student or admin role required", "access": decision.as_dict()})

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    try:
        body = await request.json()
    except Exception:
        body = {}

    invite_code = str(body.get("invite_code") or "").strip().upper()
    if not invite_code:
        return JSONResponse(status_code=400, content={"error": "invite_code is required"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            class_row = await conn.fetchrow(
                """
                SELECT id, teacher_id, name, subject, grade_level, invite_code
                FROM classes
                WHERE invite_code = $1
                """,
                invite_code,
            )
            if not class_row:
                return JSONResponse(status_code=404, content={"error": "Invite code not found"})

            student_row = await conn.fetchrow(
                "SELECT id, role FROM tutor_users WHERE id = $1",
                tutor_user_id,
            )
            if not student_row or str(student_row["role"]).lower() != "student":
                return JSONResponse(status_code=400, content={"error": "Only student users can join classes"})

            enrollment = await conn.fetchrow(
                """
                INSERT INTO class_enrollments (class_id, student_id, status)
                VALUES ($1, $2, 'active')
                ON CONFLICT (class_id, student_id)
                DO UPDATE SET status = 'active'
                RETURNING id, class_id, student_id, enrolled_at, status
                """,
                class_row["id"],
                tutor_user_id,
            )
            await conn.execute(
                """
                INSERT INTO teacher_student_links (teacher_id, student_id, status, source, notes_json)
                VALUES ($1, $2, 'active', 'class-join', '{}'::jsonb)
                ON CONFLICT (teacher_id, student_id)
                DO UPDATE SET status = 'active', source = 'class-join'
                """,
                class_row["teacher_id"],
                tutor_user_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to join class", "details": str(exc)})

    return {
        "class": {
            "id": class_row["id"],
            "name": class_row["name"],
            "subject": class_row["subject"],
            "grade_level": class_row["grade_level"],
            "invite_code": class_row["invite_code"],
        },
        "enrollment": {
            "id": enrollment["id"],
            "class_id": enrollment["class_id"],
            "student_id": enrollment["student_id"],
            "status": enrollment["status"],
            "enrolled_at": enrollment["enrolled_at"].isoformat() if enrollment["enrolled_at"] else None,
        },
    }
