from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.rate_limiter import enforce_user_rate_limit
from app.services.teacher_access import get_tutor_user_id, require_roles, teacher_can_view_student

router = APIRouter(prefix="/api/teacher", tags=["teacher-reports"])


async def _collect_context(conn, teacher_id: int, class_id: int | None, student_id: int | None) -> dict[str, object]:
    context: dict[str, object] = {"class": None, "student": None, "summary": {}}
    if class_id is not None:
        class_row = await conn.fetchrow(
            "SELECT id, name, subject, grade_level FROM classes WHERE id = $1 AND teacher_id = $2",
            class_id,
            teacher_id,
        )
        if not class_row:
            raise ValueError("Class not found")
        context["class"] = {
            "id": class_row["id"],
            "name": class_row["name"],
            "subject": class_row["subject"],
            "grade_level": class_row["grade_level"],
        }

    if student_id is not None:
        if not await teacher_can_view_student(conn, teacher_id, student_id):
            raise ValueError("Student not found in teacher scope")
        student_row = await conn.fetchrow(
            "SELECT id, display_name, grade_level FROM tutor_users WHERE id = $1",
            student_id,
        )
        context["student"] = {
            "id": student_row["id"],
            "display_name": student_row["display_name"],
            "grade_level": student_row["grade_level"],
        }
        summary = await conn.fetchrow(
            """
            SELECT COUNT(*) AS session_count,
                   COALESCE(AVG(mastery_level::FLOAT), 0) AS avg_mastery,
                   (
                       SELECT COUNT(*)
                       FROM misconception_log
                       WHERE student_id = $1 AND resolved_at IS NULL
                   ) AS active_misconceptions
            FROM tutor_sessions s
            LEFT JOIN student_mastery m ON m.student_id = s.user_id
            WHERE s.user_id = $1
            """,
            student_id,
        )
        context["summary"] = {
            "session_count": int(summary["session_count"] or 0),
            "avg_mastery": round(float(summary["avg_mastery"] or 0.0), 2),
            "active_misconceptions": int(summary["active_misconceptions"] or 0),
        }
    elif class_id is not None:
        summary = await conn.fetchrow(
            """
            SELECT COUNT(DISTINCT e.student_id) AS student_count,
                   COUNT(DISTINCT a.kb_id) AS assigned_kb_count
            FROM classes c
            LEFT JOIN class_enrollments e ON e.class_id = c.id AND e.status = 'active'
            LEFT JOIN kb_class_assignments a ON a.class_id = c.id
            WHERE c.id = $1 AND c.teacher_id = $2
            GROUP BY c.id
            """,
            class_id,
            teacher_id,
        )
        context["summary"] = {
            "student_count": int(summary["student_count"] or 0) if summary else 0,
            "assigned_kb_count": int(summary["assigned_kb_count"] or 0) if summary else 0,
        }
    return context


def _suggestions_from_context(context: dict[str, object]) -> list[str]:
    summary = context.get("summary") or {}
    suggestions: list[str] = []
    avg_mastery = float(summary.get("avg_mastery") or 0.0)
    active_misconceptions = int(summary.get("active_misconceptions") or 0)
    if avg_mastery < 2.5:
        suggestions.append("Re-teach the core concept with one worked example and one guided practice problem.")
    if active_misconceptions > 0:
        suggestions.append("Start with the misconception first and ask the student to explain their reasoning out loud.")
    if not suggestions:
        suggestions.append("Escalate difficulty with mixed retrieval practice and one short reflection prompt.")
    if context.get("class"):
        suggestions.append("Tie the next task to the class KB so the student practices with assigned material.")
    return suggestions


@router.post("/copilot/suggest")
async def teacher_copilot_suggest(request: Request):
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

    class_id = body.get("class_id")
    student_id = body.get("student_id")
    try:
        class_id = int(class_id) if class_id is not None else None
        student_id = int(student_id) if student_id is not None else None
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "class_id and student_id must be integers when provided"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            context = await _collect_context(conn, teacher_id, class_id, student_id)
    except ValueError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to generate suggestion", "details": str(exc)})

    return {
        "draft": {
            "kind": "intervention-suggestion",
            "context": context,
            "suggestions": _suggestions_from_context(context),
        }
    }


@router.post("/copilot/worksheet")
async def teacher_copilot_worksheet(request: Request):
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
    topic = str(body.get("topic") or "").strip() or "Current class topic"
    class_id = body.get("class_id")
    student_id = body.get("student_id")
    try:
        class_id = int(class_id) if class_id is not None else None
        student_id = int(student_id) if student_id is not None else None
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "class_id and student_id must be integers when provided"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            context = await _collect_context(conn, teacher_id, class_id, student_id)
    except ValueError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to generate worksheet", "details": str(exc)})

    student_name = ((context.get("student") or {}) if isinstance(context.get("student"), dict) else {}).get("display_name") or "the student"
    return {
        "draft": {
            "kind": "worksheet",
            "topic": topic,
            "context": context,
            "items": [
                f"Warm-up: ask {student_name} to define {topic} in one sentence.",
                f"Guided practice: solve one teacher-worked example on {topic}.",
                f"Independent check: complete one new problem on {topic} without hints.",
                f"Reflection: write one mistake to avoid next time when working on {topic}.",
            ],
        }
    }


@router.get("/reports")
async def list_teacher_reports(request: Request):
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
            rows = await conn.fetch(
                """
                SELECT r.id, r.class_id, r.student_id, r.report_type, r.title, r.status, r.body_json,
                       r.created_at, r.updated_at, c.name AS class_name, u.display_name AS student_name
                FROM teacher_reports r
                LEFT JOIN classes c ON c.id = r.class_id
                LEFT JOIN tutor_users u ON u.id = r.student_id
                WHERE r.teacher_id = $1
                ORDER BY r.updated_at DESC, r.id DESC
                """,
                teacher_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to list reports", "details": str(exc)})

    return {
        "reports": [
            {
                "id": row["id"],
                "class_id": row["class_id"],
                "class_name": row["class_name"],
                "student_id": row["student_id"],
                "student_name": row["student_name"],
                "report_type": row["report_type"],
                "title": row["title"],
                "status": row["status"],
                "body_json": row["body_json"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
            }
            for row in rows
        ]
    }


@router.post("/reports")
async def create_teacher_report(request: Request):
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

    report_type = str(body.get("report_type") or "summary").strip().lower()
    class_id = body.get("class_id")
    student_id = body.get("student_id")
    title = str(body.get("title") or "").strip() or f"{report_type.title()} Draft"
    try:
        class_id = int(class_id) if class_id is not None else None
        student_id = int(student_id) if student_id is not None else None
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "class_id and student_id must be integers when provided"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            context = await _collect_context(conn, teacher_id, class_id, student_id)
            suggestions = _suggestions_from_context(context)
            row = await conn.fetchrow(
                """
                INSERT INTO teacher_reports (teacher_id, class_id, student_id, report_type, title, status, body_json)
                VALUES ($1, $2, $3, $4, $5, 'draft', $6)
                RETURNING id, created_at, updated_at
                """,
                teacher_id,
                class_id,
                student_id,
                report_type,
                title,
                {"context": context, "suggestions": suggestions},
            )
    except ValueError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc)})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to create report", "details": str(exc)})

    return {
        "report": {
            "id": row["id"],
            "class_id": class_id,
            "student_id": student_id,
            "report_type": report_type,
            "title": title,
            "status": "draft",
            "body_json": {"context": context, "suggestions": suggestions},
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
        }
    }


@router.get("/communications")
async def teacher_communications(request: Request):
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
            rows = await conn.fetch(
                """
                SELECT id, class_id, student_id, title, body_json, created_at
                FROM teacher_reports
                WHERE teacher_id = $1
                  AND report_type IN ('parent-summary', 'communication', 'summary')
                ORDER BY created_at DESC, id DESC
                LIMIT 20
                """,
                teacher_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to load communications", "details": str(exc)})

    return {
        "communications": [
            {
                "id": row["id"],
                "class_id": row["class_id"],
                "student_id": row["student_id"],
                "title": row["title"],
                "body_json": row["body_json"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ]
    }
