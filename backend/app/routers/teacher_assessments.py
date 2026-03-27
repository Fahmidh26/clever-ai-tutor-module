from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.rate_limiter import enforce_user_rate_limit
from app.services.teacher_access import get_tutor_user_id, require_roles

router = APIRouter(prefix="/api/teacher/assessments", tags=["teacher-assessments"])


@router.get("")
async def list_teacher_assessments(request: Request):
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
                SELECT a.id, a.title, a.type, a.subject, a.grade_level, a.time_limit_minutes, a.created_at,
                       COUNT(q.id) AS question_count
                FROM assessments a
                LEFT JOIN assessment_questions q ON q.assessment_id = a.id
                WHERE a.teacher_id = $1
                GROUP BY a.id
                ORDER BY a.created_at DESC, a.id DESC
                """,
                teacher_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to list assessments", "details": str(exc)})

    return {
        "assessments": [
            {
                "id": row["id"],
                "title": row["title"],
                "type": row["type"],
                "subject": row["subject"],
                "grade_level": row["grade_level"],
                "time_limit_minutes": row["time_limit_minutes"],
                "question_count": int(row["question_count"] or 0),
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ]
    }


@router.post("")
async def create_teacher_assessment(request: Request):
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

    title = str(body.get("title") or "").strip()
    if not title:
        return JSONResponse(status_code=400, content={"error": "title is required"})
    assessment_type = str(body.get("type") or "quiz").strip() or "quiz"
    subject = str(body.get("subject") or "").strip() or None
    time_limit_minutes_raw = body.get("time_limit_minutes")
    time_limit_minutes = None
    if time_limit_minutes_raw not in (None, ""):
        try:
            time_limit_minutes = int(time_limit_minutes_raw)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "time_limit_minutes must be an integer"})

    grade_level_raw = body.get("grade_level")
    grade_level = None
    if grade_level_raw not in (None, ""):
        try:
            grade_level = int(grade_level_raw)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "grade_level must be an integer"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO assessments (teacher_id, title, type, subject, grade_level, standards_json, time_limit_minutes)
                VALUES ($1, $2, $3, $4, $5, '[]'::jsonb, $6)
                RETURNING id, title, type, subject, grade_level, time_limit_minutes, created_at
                """,
                teacher_id,
                title,
                assessment_type,
                subject,
                grade_level,
                time_limit_minutes,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to create assessment", "details": str(exc)})

    return {
        "assessment": {
            "id": row["id"],
            "title": row["title"],
            "type": row["type"],
            "subject": row["subject"],
            "grade_level": row["grade_level"],
            "time_limit_minutes": row["time_limit_minutes"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        }
    }


@router.get("/{assessment_id:int}")
async def get_teacher_assessment(request: Request, assessment_id: int):
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
            assessment = await conn.fetchrow(
                """
                SELECT id, title, type, subject, grade_level, time_limit_minutes, created_at
                FROM assessments
                WHERE id = $1 AND teacher_id = $2
                """,
                assessment_id,
                teacher_id,
            )
            if not assessment:
                return JSONResponse(status_code=404, content={"error": "Assessment not found"})
            questions = await conn.fetch(
                """
                SELECT id, question_type, content, options_json, correct_answer, explanation, sort_order
                FROM assessment_questions
                WHERE assessment_id = $1
                ORDER BY sort_order ASC, id ASC
                """,
                assessment_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to load assessment", "details": str(exc)})

    return {
        "assessment": {
            "id": assessment["id"],
            "title": assessment["title"],
            "type": assessment["type"],
            "subject": assessment["subject"],
            "grade_level": assessment["grade_level"],
            "time_limit_minutes": assessment["time_limit_minutes"],
            "created_at": assessment["created_at"].isoformat() if assessment["created_at"] else None,
        },
        "questions": [
            {
                "id": row["id"],
                "question_type": row["question_type"],
                "content": row["content"],
                "options_json": row["options_json"],
                "correct_answer": row["correct_answer"],
                "explanation": row["explanation"],
                "sort_order": row["sort_order"],
            }
            for row in questions
        ],
    }


@router.post("/{assessment_id:int}/questions")
async def add_assessment_question(request: Request, assessment_id: int):
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

    content = str(body.get("content") or "").strip()
    if not content:
        return JSONResponse(status_code=400, content={"error": "content is required"})
    question_type = str(body.get("question_type") or "short-answer").strip() or "short-answer"
    options_json = body.get("options_json")
    correct_answer = str(body.get("correct_answer") or "").strip() or None
    explanation = str(body.get("explanation") or "").strip() or None
    sort_order_raw = body.get("sort_order", 0)
    try:
        sort_order = int(sort_order_raw)
    except (TypeError, ValueError):
        sort_order = 0

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            assessment = await conn.fetchrow(
                "SELECT id FROM assessments WHERE id = $1 AND teacher_id = $2",
                assessment_id,
                teacher_id,
            )
            if not assessment:
                return JSONResponse(status_code=404, content={"error": "Assessment not found"})
            row = await conn.fetchrow(
                """
                INSERT INTO assessment_questions (
                    assessment_id, question_type, content, options_json, correct_answer, explanation, misconceptions_tested_json, sort_order
                )
                VALUES ($1, $2, $3, $4, $5, $6, '[]'::jsonb, $7)
                RETURNING id, question_type, content, options_json, correct_answer, explanation, sort_order
                """,
                assessment_id,
                question_type,
                content,
                options_json,
                correct_answer,
                explanation,
                sort_order,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to add assessment question", "details": str(exc)})

    return {
        "question": {
            "id": row["id"],
            "question_type": row["question_type"],
            "content": row["content"],
            "options_json": row["options_json"],
            "correct_answer": row["correct_answer"],
            "explanation": row["explanation"],
            "sort_order": row["sort_order"],
        }
    }
