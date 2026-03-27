from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.rate_limiter import enforce_user_rate_limit
from app.services.teacher_access import get_tutor_user_id, require_roles, teacher_can_view_student

router = APIRouter(prefix="/api/teacher", tags=["teacher-monitoring"])


async def _class_summary(conn, teacher_id: int, class_id: int) -> dict[str, object] | None:
    class_row = await conn.fetchrow(
        """
        SELECT id, name, subject, grade_level, invite_code, persona_id
        FROM classes
        WHERE id = $1 AND teacher_id = $2
        """,
        class_id,
        teacher_id,
    )
    if not class_row:
        return None

    roster = await conn.fetch(
        """
        SELECT e.student_id, u.display_name, u.grade_level
        FROM class_enrollments e
        JOIN tutor_users u ON u.id = e.student_id
        WHERE e.class_id = $1 AND e.status = 'active'
        ORDER BY u.display_name NULLS LAST, e.id DESC
        """,
        class_id,
    )
    student_ids = [int(r["student_id"]) for r in roster]
    if not student_ids:
        return {
            "class": {
                "id": class_row["id"],
                "name": class_row["name"],
                "subject": class_row["subject"],
                "grade_level": class_row["grade_level"],
                "invite_code": class_row["invite_code"],
                "persona_id": class_row["persona_id"],
            },
            "summary": {
                "student_count": 0,
                "active_students": 0,
                "avg_mastery": 0.0,
                "quiz_accuracy": 0.0,
                "active_misconceptions": 0,
                "total_sessions": 0,
                "total_messages": 0,
                "kb_messages": 0,
                "assigned_kb_count": 0,
            },
            "students": [],
        }

    mastery_rows = await conn.fetch(
        """
        SELECT student_id, COALESCE(AVG(mastery_level::FLOAT), 0) AS avg_mastery
        FROM student_mastery
        WHERE student_id = ANY($1::INT[])
        GROUP BY student_id
        """,
        student_ids,
    )
    quiz_rows = await conn.fetch(
        """
        SELECT user_id AS student_id,
               COUNT(*) AS total_quiz,
               COALESCE(SUM(CASE WHEN is_correct THEN 1 ELSE 0 END), 0) AS correct_quiz
        FROM adaptive_quiz_attempts
        WHERE user_id = ANY($1::INT[])
          AND is_correct IS NOT NULL
        GROUP BY user_id
        """,
        student_ids,
    )
    misconception_rows = await conn.fetch(
        """
        SELECT student_id, COUNT(*) AS active_misconceptions
        FROM misconception_log
        WHERE student_id = ANY($1::INT[])
          AND resolved_at IS NULL
        GROUP BY student_id
        """,
        student_ids,
    )
    session_rows = await conn.fetch(
        """
        SELECT user_id AS student_id,
               COUNT(*) AS total_sessions,
               MAX(COALESCE(ended_at, started_at, created_at)) AS last_activity_at
        FROM tutor_sessions
        WHERE user_id = ANY($1::INT[])
          AND class_id = $2
        GROUP BY user_id
        """,
        student_ids,
        class_id,
    )
    message_rows = await conn.fetch(
        """
        SELECT s.user_id AS student_id,
               COUNT(m.id) AS total_messages,
               COALESCE(SUM(CASE WHEN m.kb_id IS NOT NULL THEN 1 ELSE 0 END), 0) AS kb_messages,
               MAX(m.created_at) AS last_message_at
        FROM tutor_sessions s
        JOIN tutor_messages m ON m.session_id = s.id
        WHERE s.user_id = ANY($1::INT[])
          AND s.class_id = $2
        GROUP BY s.user_id
        """,
        student_ids,
        class_id,
    )
    kb_count_row = await conn.fetchrow(
        "SELECT COUNT(*) AS assigned_kb_count FROM kb_class_assignments WHERE class_id = $1",
        class_id,
    )

    mastery_map = {int(r["student_id"]): float(r["avg_mastery"] or 0.0) for r in mastery_rows}
    quiz_map = {int(r["student_id"]): (int(r["total_quiz"] or 0), int(r["correct_quiz"] or 0)) for r in quiz_rows}
    misconception_map = {int(r["student_id"]): int(r["active_misconceptions"] or 0) for r in misconception_rows}
    session_map = {
        int(r["student_id"]): {
            "total_sessions": int(r["total_sessions"] or 0),
            "last_activity_at": r["last_activity_at"].isoformat() if r["last_activity_at"] else None,
        }
        for r in session_rows
    }
    message_map = {
        int(r["student_id"]): {
            "total_messages": int(r["total_messages"] or 0),
            "kb_messages": int(r["kb_messages"] or 0),
            "last_message_at": r["last_message_at"].isoformat() if r["last_message_at"] else None,
        }
        for r in message_rows
    }

    students_payload: list[dict[str, object]] = []
    total_accuracy_sum = 0.0
    total_mastery_sum = 0.0
    total_misconceptions = 0
    total_sessions = 0
    total_messages = 0
    total_kb_messages = 0
    active_students = 0
    for row in roster:
        sid = int(row["student_id"])
        total_quiz, correct_quiz = quiz_map.get(sid, (0, 0))
        accuracy = (correct_quiz / total_quiz) if total_quiz > 0 else 0.0
        avg_mastery = mastery_map.get(sid, 0.0)
        active_mis = misconception_map.get(sid, 0)
        session_info = session_map.get(sid, {"total_sessions": 0, "last_activity_at": None})
        message_info = message_map.get(sid, {"total_messages": 0, "kb_messages": 0, "last_message_at": None})
        total_accuracy_sum += accuracy
        total_mastery_sum += avg_mastery
        total_misconceptions += active_mis
        total_sessions += int(session_info["total_sessions"])
        total_messages += int(message_info["total_messages"])
        total_kb_messages += int(message_info["kb_messages"])
        if int(session_info["total_sessions"]) > 0 or int(message_info["total_messages"]) > 0:
            active_students += 1
        students_payload.append(
            {
                "student_id": sid,
                "display_name": row["display_name"],
                "grade_level": row["grade_level"],
                "avg_mastery": round(avg_mastery, 2),
                "quiz_accuracy": round(accuracy, 4),
                "active_misconceptions": active_mis,
                "total_sessions": int(session_info["total_sessions"]),
                "total_messages": int(message_info["total_messages"]),
                "kb_messages": int(message_info["kb_messages"]),
                "last_activity_at": message_info["last_message_at"] or session_info["last_activity_at"],
            }
        )

    student_count = len(students_payload)
    return {
        "class": {
            "id": class_row["id"],
            "name": class_row["name"],
            "subject": class_row["subject"],
            "grade_level": class_row["grade_level"],
            "invite_code": class_row["invite_code"],
            "persona_id": class_row["persona_id"],
        },
        "summary": {
            "student_count": student_count,
            "active_students": active_students,
            "avg_mastery": round(total_mastery_sum / student_count, 2) if student_count > 0 else 0.0,
            "quiz_accuracy": round(total_accuracy_sum / student_count, 4) if student_count > 0 else 0.0,
            "active_misconceptions": total_misconceptions,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "kb_messages": total_kb_messages,
            "assigned_kb_count": int(kb_count_row["assigned_kb_count"] or 0) if kb_count_row else 0,
        },
        "students": students_payload,
    }


@router.get("/monitoring")
async def teacher_monitoring_dashboard(request: Request):
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
            class_rows = await conn.fetch(
                "SELECT id FROM classes WHERE teacher_id = $1 ORDER BY id DESC",
                teacher_id,
            )
            payload = []
            for row in class_rows:
                summary = await _class_summary(conn, teacher_id, int(row["id"]))
                if summary:
                    payload.append(summary)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to load teacher monitoring dashboard", "details": str(exc)})

    return {"classes": payload}


@router.get("/analytics/class/{class_id:int}")
async def teacher_class_analytics(request: Request, class_id: int):
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
            payload = await _class_summary(conn, teacher_id, class_id)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to load class analytics", "details": str(exc)})

    if payload is None:
        return JSONResponse(status_code=404, content={"error": "Class not found"})
    return payload


@router.get("/analytics/students/{student_id:int}")
async def teacher_student_analytics(request: Request, student_id: int):
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
            if not await teacher_can_view_student(conn, teacher_id, student_id):
                return JSONResponse(status_code=404, content={"error": "Student not found in teacher scope"})

            student_row = await conn.fetchrow(
                "SELECT id, display_name, grade_level FROM tutor_users WHERE id = $1",
                student_id,
            )
            classes = await conn.fetch(
                """
                SELECT c.id, c.name, c.subject, c.grade_level
                FROM classes c
                JOIN class_enrollments e ON e.class_id = c.id
                WHERE c.teacher_id = $1
                  AND e.student_id = $2
                  AND e.status = 'active'
                ORDER BY c.id DESC
                """,
                teacher_id,
                student_id,
            )
            mastery = await conn.fetch(
                """
                SELECT id, subject, topic, mastery_level, reasoning_quality, last_assessed_at
                FROM student_mastery
                WHERE student_id = $1
                ORDER BY last_assessed_at DESC NULLS LAST, id DESC
                LIMIT 20
                """,
                student_id,
            )
            misconceptions = await conn.fetch(
                """
                SELECT id, subject, topic, misconception_type, description, detected_at, resolved_at
                FROM misconception_log
                WHERE student_id = $1
                ORDER BY detected_at DESC, id DESC
                LIMIT 20
                """,
                student_id,
            )
            sessions = await conn.fetch(
                """
                SELECT s.id, s.class_id, s.subject, s.topic, s.mode, s.created_at,
                       p.name AS persona_name,
                       COUNT(m.id) AS message_count
                FROM tutor_sessions s
                LEFT JOIN tutor_personas p ON p.id = s.persona_id
                LEFT JOIN tutor_messages m ON m.session_id = s.id
                WHERE s.user_id = $1
                GROUP BY s.id, p.name
                ORDER BY s.created_at DESC, s.id DESC
                LIMIT 20
                """,
                student_id,
            )
            quiz = await conn.fetchrow(
                """
                SELECT COUNT(*) AS total_quiz,
                       COALESCE(SUM(CASE WHEN is_correct THEN 1 ELSE 0 END), 0) AS correct_quiz
                FROM adaptive_quiz_attempts
                WHERE user_id = $1
                  AND is_correct IS NOT NULL
                """,
                student_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to load student analytics", "details": str(exc)})

    total_quiz = int(quiz["total_quiz"] or 0) if quiz else 0
    correct_quiz = int(quiz["correct_quiz"] or 0) if quiz else 0
    return {
        "student": {
            "id": student_row["id"],
            "display_name": student_row["display_name"],
            "grade_level": student_row["grade_level"],
        },
        "summary": {
            "class_count": len(classes),
            "mastery_count": len(mastery),
            "active_misconceptions": sum(1 for row in misconceptions if row["resolved_at"] is None),
            "quiz_accuracy": round(correct_quiz / total_quiz, 4) if total_quiz > 0 else 0.0,
            "session_count": len(sessions),
        },
        "classes": [
            {"id": row["id"], "name": row["name"], "subject": row["subject"], "grade_level": row["grade_level"]}
            for row in classes
        ],
        "mastery": [
            {
                "id": row["id"],
                "subject": row["subject"],
                "topic": row["topic"],
                "mastery_level": row["mastery_level"],
                "reasoning_quality": row["reasoning_quality"],
                "last_assessed_at": row["last_assessed_at"].isoformat() if row["last_assessed_at"] else None,
            }
            for row in mastery
        ],
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
            for row in misconceptions
        ],
        "recent_sessions": [
            {
                "id": row["id"],
                "class_id": row["class_id"],
                "subject": row["subject"],
                "topic": row["topic"],
                "mode": row["mode"],
                "persona_name": row["persona_name"],
                "message_count": int(row["message_count"] or 0),
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in sessions
        ],
    }


@router.get("/analytics/struggling")
async def teacher_struggling_students(request: Request):
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
                SELECT DISTINCT u.id AS student_id, u.display_name, c.id AS class_id, c.name AS class_name,
                       COALESCE(m.avg_mastery, 0) AS avg_mastery,
                       COALESCE(mc.active_misconceptions, 0) AS active_misconceptions,
                       COALESCE(q.total_quiz, 0) AS total_quiz,
                       COALESCE(q.correct_quiz, 0) AS correct_quiz,
                       s.last_activity_at
                FROM classes c
                JOIN class_enrollments e ON e.class_id = c.id AND e.status = 'active'
                JOIN tutor_users u ON u.id = e.student_id
                LEFT JOIN (
                    SELECT student_id, AVG(mastery_level::FLOAT) AS avg_mastery
                    FROM student_mastery
                    GROUP BY student_id
                ) m ON m.student_id = u.id
                LEFT JOIN (
                    SELECT student_id, COUNT(*) AS active_misconceptions
                    FROM misconception_log
                    WHERE resolved_at IS NULL
                    GROUP BY student_id
                ) mc ON mc.student_id = u.id
                LEFT JOIN (
                    SELECT user_id, COUNT(*) AS total_quiz,
                           COALESCE(SUM(CASE WHEN is_correct THEN 1 ELSE 0 END), 0) AS correct_quiz
                    FROM adaptive_quiz_attempts
                    WHERE is_correct IS NOT NULL
                    GROUP BY user_id
                ) q ON q.user_id = u.id
                LEFT JOIN (
                    SELECT user_id, MAX(COALESCE(ended_at, started_at, created_at)) AS last_activity_at
                    FROM tutor_sessions
                    GROUP BY user_id
                ) s ON s.user_id = u.id
                WHERE c.teacher_id = $1
                ORDER BY c.id DESC, u.display_name NULLS LAST
                """,
                teacher_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to load struggling students", "details": str(exc)})

    items: list[dict[str, object]] = []
    for row in rows:
        total_quiz = int(row["total_quiz"] or 0)
        correct_quiz = int(row["correct_quiz"] or 0)
        accuracy = (correct_quiz / total_quiz) if total_quiz > 0 else 0.0
        flags: list[str] = []
        if float(row["avg_mastery"] or 0.0) < 2.5:
            flags.append("low_mastery")
        if int(row["active_misconceptions"] or 0) >= 2:
            flags.append("misconceptions")
        if total_quiz > 0 and accuracy < 0.7:
            flags.append("low_quiz_accuracy")
        if row["last_activity_at"] is None:
            flags.append("inactive")
        if not flags:
            continue
        items.append(
            {
                "student_id": row["student_id"],
                "display_name": row["display_name"],
                "class_id": row["class_id"],
                "class_name": row["class_name"],
                "avg_mastery": round(float(row["avg_mastery"] or 0.0), 2),
                "quiz_accuracy": round(accuracy, 4),
                "active_misconceptions": int(row["active_misconceptions"] or 0),
                "last_activity_at": row["last_activity_at"].isoformat() if row["last_activity_at"] else None,
                "flags": flags,
            }
        )

    return {"students": items}


@router.get("/session-replay/{session_id:int}")
async def teacher_session_replay(request: Request, session_id: int):
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
            session_row = await conn.fetchrow(
                """
                SELECT s.id, s.user_id, s.class_id, s.subject, s.topic, s.mode, s.created_at,
                       u.display_name,
                       c.name AS class_name,
                       p.name AS persona_name
                FROM tutor_sessions s
                JOIN tutor_users u ON u.id = s.user_id
                LEFT JOIN classes c ON c.id = s.class_id
                LEFT JOIN tutor_personas p ON p.id = s.persona_id
                WHERE s.id = $1
                """,
                session_id,
            )
            if not session_row:
                return JSONResponse(status_code=404, content={"error": "Session not found"})

            class_owned = False
            if session_row["class_id"] is not None:
                class_check = await conn.fetchrow(
                    "SELECT 1 FROM classes WHERE id = $1 AND teacher_id = $2",
                    session_row["class_id"],
                    teacher_id,
                )
                class_owned = bool(class_check)
            if not class_owned and not await teacher_can_view_student(conn, teacher_id, int(session_row["user_id"])):
                return JSONResponse(status_code=404, content={"error": "Session not found in teacher scope"})

            messages = await conn.fetch(
                """
                SELECT id, role, content, mode, kb_id, created_at
                FROM tutor_messages
                WHERE session_id = $1
                ORDER BY id ASC
                """,
                session_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to load session replay", "details": str(exc)})

    return {
        "session": {
            "id": session_row["id"],
            "student_id": session_row["user_id"],
            "student_name": session_row["display_name"],
            "class_id": session_row["class_id"],
            "class_name": session_row["class_name"],
            "subject": session_row["subject"],
            "topic": session_row["topic"],
            "mode": session_row["mode"],
            "persona_name": session_row["persona_name"],
            "created_at": session_row["created_at"].isoformat() if session_row["created_at"] else None,
        },
        "messages": [
            {
                "id": row["id"],
                "role": row["role"],
                "content": row["content"],
                "mode": row["mode"],
                "kb_id": row["kb_id"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in messages
        ],
    }
