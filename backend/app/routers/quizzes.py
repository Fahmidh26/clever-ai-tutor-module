"""
Phase 2 adaptive quiz API.
Additive endpoints for generating and submitting adaptive quiz questions.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.adaptive_quiz import (
    evaluate_quiz_answer,
    generate_adaptive_quiz_question,
    recommend_difficulty_from_recent_scores,
)
from app.services.rate_limiter import enforce_user_rate_limit

router = APIRouter(prefix="/api/tutor/quiz", tags=["adaptive-quiz"])


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


@router.post("/generate")
async def generate_quiz_question(request: Request):
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

    session_id = body.get("session_id")
    subject = (body.get("subject") or "").strip() or None
    topic = (body.get("topic") or "").strip() or None
    prompt_context = (body.get("prompt_context") or "").strip() or None
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

            recent_rows = await conn.fetch(
                """
                SELECT is_correct
                FROM adaptive_quiz_attempts
                WHERE user_id = $1
                  AND ($2::VARCHAR IS NULL OR subject = $2)
                  AND ($3::VARCHAR IS NULL OR topic = $3)
                  AND is_correct IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 5
                """,
                tutor_user_id,
                subject,
                topic,
            )
            recent = [bool(row["is_correct"]) for row in recent_rows]
            recommended_difficulty = recommend_difficulty_from_recent_scores(recent)

            question = await generate_adaptive_quiz_question(
                subject=subject,
                topic=topic,
                grade_level=grade_level,
                prompt_context=prompt_context,
                recommended_difficulty=recommended_difficulty,
            )

            row = await conn.fetchrow(
                """
                INSERT INTO adaptive_quiz_attempts (
                    user_id, session_id, subject, topic, prompt_context, difficulty,
                    question_text, options_json, correct_answer, explanation, status, model_used
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8::JSONB, $9, $10, 'pending', $11)
                RETURNING id, difficulty, question_text, options_json, created_at
                """,
                tutor_user_id,
                session_id,
                subject,
                topic,
                prompt_context,
                question.difficulty,
                question.question_text,
                json.dumps(question.options),
                question.correct_answer,
                question.explanation,
                question.model_used,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to generate quiz question", "details": str(e)})

    return {
        "quiz": {
            "id": row["id"],
            "difficulty": row["difficulty"],
            "question": row["question_text"],
            "options": row["options_json"] if isinstance(row["options_json"], list) else [],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        },
        "execution_attempts": question.execution_attempts,
    }


@router.post("/{quiz_id:int}/submit")
async def submit_quiz_answer(request: Request, quiz_id: int):
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
    selected_answer = (body.get("answer") or "").strip()
    if not selected_answer:
        return JSONResponse(status_code=400, content={"error": "answer is required"})

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT id, user_id, session_id, subject, topic, difficulty, question_text, options_json,
                       correct_answer, explanation, status
                FROM adaptive_quiz_attempts
                WHERE id = $1 AND user_id = $2
                """,
                quiz_id,
                tutor_user_id,
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Quiz attempt not found"})
            if row["status"] != "pending":
                return JSONResponse(status_code=400, content={"error": "Quiz attempt already submitted"})

            is_correct, feedback = evaluate_quiz_answer(
                selected_answer=selected_answer,
                correct_answer=str(row["correct_answer"] or ""),
                explanation=str(row["explanation"] or ""),
            )

            await conn.execute(
                """
                UPDATE adaptive_quiz_attempts
                SET selected_answer = $2,
                    is_correct = $3,
                    feedback = $4,
                    status = 'submitted',
                    submitted_at = NOW()
                WHERE id = $1 AND user_id = $5
                """,
                quiz_id,
                selected_answer,
                is_correct,
                feedback,
                tutor_user_id,
            )

            recent_rows = await conn.fetch(
                """
                SELECT is_correct
                FROM adaptive_quiz_attempts
                WHERE user_id = $1
                  AND ($2::VARCHAR IS NULL OR subject = $2)
                  AND ($3::VARCHAR IS NULL OR topic = $3)
                  AND is_correct IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 5
                """,
                tutor_user_id,
                row["subject"],
                row["topic"],
            )
            recent = [bool(item["is_correct"]) for item in recent_rows]
            next_difficulty = recommend_difficulty_from_recent_scores(recent)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to submit quiz answer", "details": str(e)})

    return {
        "result": {
            "quiz_id": quiz_id,
            "is_correct": is_correct,
            "selected_answer": selected_answer,
            "correct_answer": row["correct_answer"],
            "feedback": feedback,
            "explanation": row["explanation"],
            "difficulty": row["difficulty"],
            "next_recommended_difficulty": next_difficulty,
        }
    }


@router.get("/history")
async def quiz_history(request: Request, limit: int = 20):
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
    limit = max(1, min(100, limit))

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, subject, topic, difficulty, question_text, selected_answer, is_correct, status, created_at, submitted_at
                FROM adaptive_quiz_attempts
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
                """,
                tutor_user_id,
                limit,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch quiz history", "details": str(e)})

    history: list[dict[str, object]] = []
    for row in rows:
        history.append(
            {
                "id": row["id"],
                "subject": row["subject"],
                "topic": row["topic"],
                "difficulty": row["difficulty"],
                "question": row["question_text"],
                "selected_answer": row["selected_answer"],
                "is_correct": row["is_correct"],
                "status": row["status"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "submitted_at": row["submitted_at"].isoformat() if row["submitted_at"] else None,
            }
        )
    return {"history": history}
