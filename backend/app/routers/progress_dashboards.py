"""
Phase 2 student + teacher progress dashboards.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.rate_limiter import enforce_user_rate_limit
from app.services.rbac import evaluate_access

router = APIRouter(prefix="/api/tutor/progress", tags=["progress"])


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


@router.get("/student")
async def student_dashboard(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    student_id = _get_tutor_user_id(request)
    if student_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})
    try:
        async with db_pool.acquire() as conn:
            sessions = await conn.fetchrow(
                """
                SELECT COUNT(*) AS total_sessions,
                       COALESCE(SUM(tokens_used), 0) AS total_tokens
                FROM tutor_sessions
                WHERE user_id = $1
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
            mastery = await conn.fetchrow(
                """
                SELECT COUNT(*) AS mastery_topics,
                       COALESCE(AVG(mastery_level::FLOAT), 0) AS avg_mastery
                FROM student_mastery
                WHERE student_id = $1
                """,
                student_id,
            )
            misconceptions = await conn.fetchrow(
                """
                SELECT COUNT(*) AS active_misconceptions
                FROM misconception_log
                WHERE student_id = $1 AND resolved_at IS NULL
                """,
                student_id,
            )
            due_cards = await conn.fetchrow(
                """
                SELECT COUNT(*) AS due_flashcards
                FROM flashcards f
                JOIN flashcard_decks d ON d.id = f.deck_id
                WHERE d.student_id = $1
                  AND (f.next_review_at IS NULL OR f.next_review_at <= NOW())
                """,
                student_id,
            )

            recent_mastery = await conn.fetch(
                """
                SELECT subject, topic, mastery_level, reasoning_quality, last_assessed_at
                FROM student_mastery
                WHERE student_id = $1
                ORDER BY last_assessed_at DESC NULLS LAST, id DESC
                LIMIT 8
                """,
                student_id,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to build student dashboard", "details": str(e)})

    total_quiz = int(quiz["total_quiz"] or 0)
    correct_quiz = int(quiz["correct_quiz"] or 0)
    accuracy = (correct_quiz / total_quiz) if total_quiz > 0 else 0.0
    return {
        "summary": {
            "total_sessions": int(sessions["total_sessions"] or 0),
            "total_tokens": int(sessions["total_tokens"] or 0),
            "total_quiz": total_quiz,
            "correct_quiz": correct_quiz,
            "quiz_accuracy": round(accuracy, 4),
            "mastery_topics": int(mastery["mastery_topics"] or 0),
            "avg_mastery": round(float(mastery["avg_mastery"] or 0.0), 2),
            "active_misconceptions": int(misconceptions["active_misconceptions"] or 0),
            "due_flashcards": int(due_cards["due_flashcards"] or 0),
        },
        "recent_mastery": [
            {
                "subject": row["subject"],
                "topic": row["topic"],
                "mastery_level": int(row["mastery_level"] or 0),
                "reasoning_quality": int(row["reasoning_quality"] or 0) if row["reasoning_quality"] is not None else None,
                "last_assessed_at": row["last_assessed_at"].isoformat() if row["last_assessed_at"] else None,
            }
            for row in recent_mastery
        ],
    }


@router.get("/teacher")
async def teacher_dashboard(request: Request, class_id: int):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    decision = evaluate_access(request.session.get("user"), ["teacher", "admin"])
    if not decision.allowed:
        return JSONResponse(status_code=403, content={"error": "Teacher or admin role required", "access": decision.as_dict()})

    teacher_id = _get_tutor_user_id(request)
    if teacher_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})
    try:
        async with db_pool.acquire() as conn:
            class_row = await conn.fetchrow(
                """
                SELECT id, name, subject, grade_level
                FROM classes
                WHERE id = $1 AND teacher_id = $2
                """,
                class_id,
                teacher_id,
            )
            if not class_row:
                return JSONResponse(status_code=404, content={"error": "Class not found"})

            roster = await conn.fetch(
                """
                SELECT e.student_id, u.display_name
                FROM class_enrollments e
                JOIN tutor_users u ON u.id = e.student_id
                WHERE e.class_id = $1 AND e.status = 'active'
                ORDER BY e.id DESC
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
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to build teacher dashboard", "details": str(e)})

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
