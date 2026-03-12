"""
Phase 2 flashcards + spaced repetition API.
"""
from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.flashcards import apply_sm2_review, generate_flashcards
from app.services.rate_limiter import enforce_user_rate_limit

router = APIRouter(prefix="/api/tutor/flashcards", tags=["flashcards"])


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


@router.post("/decks")
async def create_deck(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    user_id = _get_tutor_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})
    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        body = await request.json()
    except Exception:
        body = {}
    title = (body.get("title") or "").strip()
    if not title:
        return JSONResponse(status_code=400, content={"error": "title is required"})
    subject = (body.get("subject") or "").strip() or None
    topic = (body.get("topic") or "").strip() or None

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO flashcard_decks (student_id, title, subject, topic)
                VALUES ($1, $2, $3, $4)
                RETURNING id, student_id, title, subject, topic, created_at
                """,
                user_id,
                title,
                subject,
                topic,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to create deck", "details": str(e)})

    return {
        "deck": {
            "id": row["id"],
            "student_id": row["student_id"],
            "title": row["title"],
            "subject": row["subject"],
            "topic": row["topic"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        }
    }


@router.get("/decks")
async def list_decks(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    user_id = _get_tutor_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})
    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT d.id, d.title, d.subject, d.topic, d.created_at, COUNT(f.id) AS card_count
                FROM flashcard_decks d
                LEFT JOIN flashcards f ON f.deck_id = d.id
                WHERE d.student_id = $1
                GROUP BY d.id
                ORDER BY d.created_at DESC, d.id DESC
                """,
                user_id,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to list decks", "details": str(e)})

    return {
        "decks": [
            {
                "id": row["id"],
                "title": row["title"],
                "subject": row["subject"],
                "topic": row["topic"],
                "card_count": int(row["card_count"] or 0),
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ]
    }


@router.get("/decks/{deck_id:int}")
async def get_deck_cards(request: Request, deck_id: int):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    user_id = _get_tutor_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})
    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            deck = await conn.fetchrow(
                "SELECT id, title, subject, topic, created_at FROM flashcard_decks WHERE id = $1 AND student_id = $2",
                deck_id,
                user_id,
            )
            if not deck:
                return JSONResponse(status_code=404, content={"error": "Deck not found"})
            rows = await conn.fetch(
                """
                SELECT id, front, back, next_review_at, ease_factor, interval, review_count, created_at
                FROM flashcards
                WHERE deck_id = $1
                ORDER BY id DESC
                """,
                deck_id,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch deck", "details": str(e)})

    return {
        "deck": {
            "id": deck["id"],
            "title": deck["title"],
            "subject": deck["subject"],
            "topic": deck["topic"],
            "created_at": deck["created_at"].isoformat() if deck["created_at"] else None,
        },
        "cards": [
            {
                "id": row["id"],
                "front": row["front"],
                "back": row["back"],
                "next_review_at": row["next_review_at"].isoformat() if row["next_review_at"] else None,
                "ease_factor": float(row["ease_factor"] or 2.5),
                "interval_days": int(row["interval"] or 1),
                "review_count": int(row["review_count"] or 0),
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ],
    }


@router.post("/generate")
async def generate_cards(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    user_id = _get_tutor_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})
    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        body = await request.json()
    except Exception:
        body = {}
    deck_id = body.get("deck_id")
    prompt = (body.get("prompt") or "").strip()
    if not prompt:
        return JSONResponse(status_code=400, content={"error": "prompt is required"})
    count = body.get("count", 5)
    try:
        count = max(1, min(10, int(count)))
    except (TypeError, ValueError):
        count = 5

    subject = (body.get("subject") or "").strip() or None
    topic = (body.get("topic") or "").strip() or None
    grade_level = None

    try:
        async with db_pool.acquire() as conn:
            if deck_id is not None:
                try:
                    deck_id = int(deck_id)
                except (TypeError, ValueError):
                    return JSONResponse(status_code=400, content={"error": "deck_id must be an integer"})
                deck = await conn.fetchrow(
                    """
                    SELECT d.id, d.title, d.subject, d.topic, s.grade_level
                    FROM flashcard_decks d
                    LEFT JOIN tutor_sessions s ON s.id = $3
                    WHERE d.id = $1 AND d.student_id = $2
                    """,
                    deck_id,
                    user_id,
                    body.get("session_id"),
                )
                if not deck:
                    return JSONResponse(status_code=404, content={"error": "Deck not found"})
                subject = subject or deck["subject"]
                topic = topic or deck["topic"]
                grade_level = deck["grade_level"]
            else:
                row = await conn.fetchrow(
                    """
                    INSERT INTO flashcard_decks (student_id, title, subject, topic)
                    VALUES ($1, $2, $3, $4)
                    RETURNING id
                    """,
                    user_id,
                    (body.get("title") or "Generated Deck").strip() or "Generated Deck",
                    subject,
                    topic,
                )
                deck_id = row["id"]

            generated = await generate_flashcards(
                prompt=prompt,
                subject=subject,
                topic=topic,
                grade_level=grade_level,
                count=count,
            )

            inserted = []
            for card in generated.cards:
                row = await conn.fetchrow(
                    """
                    INSERT INTO flashcards (deck_id, front, back, source_session_id, next_review_at, ease_factor, interval, review_count)
                    VALUES ($1, $2, $3, $4, NOW(), 2.5, 1, 0)
                    RETURNING id, front, back, next_review_at, ease_factor, interval, review_count, created_at
                    """,
                    deck_id,
                    card.front,
                    card.back,
                    body.get("session_id"),
                )
                inserted.append(row)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to generate flashcards", "details": str(e)})

    return {
        "deck_id": deck_id,
        "cards": [
            {
                "id": row["id"],
                "front": row["front"],
                "back": row["back"],
                "next_review_at": row["next_review_at"].isoformat() if row["next_review_at"] else None,
                "ease_factor": float(row["ease_factor"] or 2.5),
                "interval_days": int(row["interval"] or 1),
                "review_count": int(row["review_count"] or 0),
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in inserted
        ],
        "execution_attempts": generated.execution_attempts,
    }


@router.get("/review")
async def due_cards(request: Request, limit: int = 20):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    user_id = _get_tutor_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})
    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})
    limit = max(1, min(100, limit))
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT f.id, f.deck_id, f.front, f.back, f.next_review_at, f.ease_factor, f.interval, f.review_count,
                       d.title AS deck_title, d.subject, d.topic
                FROM flashcards f
                JOIN flashcard_decks d ON d.id = f.deck_id
                WHERE d.student_id = $1
                  AND (f.next_review_at IS NULL OR f.next_review_at <= NOW())
                ORDER BY f.next_review_at ASC NULLS FIRST, f.id ASC
                LIMIT $2
                """,
                user_id,
                limit,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch due cards", "details": str(e)})

    return {
        "cards": [
            {
                "id": row["id"],
                "deck_id": row["deck_id"],
                "deck_title": row["deck_title"],
                "subject": row["subject"],
                "topic": row["topic"],
                "front": row["front"],
                "back": row["back"],
                "next_review_at": row["next_review_at"].isoformat() if row["next_review_at"] else None,
                "ease_factor": float(row["ease_factor"] or 2.5),
                "interval_days": int(row["interval"] or 1),
                "review_count": int(row["review_count"] or 0),
            }
            for row in rows
        ]
    }


@router.post("/{card_id:int}/review")
async def review_card(request: Request, card_id: int):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response
    if not request.session.get("access_token"):
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    user_id = _get_tutor_user_id(request)
    if user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})
    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        body = await request.json()
    except Exception:
        body = {}
    quality_raw = body.get("quality")
    if quality_raw is None:
        return JSONResponse(status_code=400, content={"error": "quality is required (0-5)"})
    try:
        quality = max(0, min(5, int(quality_raw)))
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "quality must be an integer (0-5)"})

    now = datetime.now(UTC)
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT f.id, f.ease_factor, f.interval, f.review_count
                FROM flashcards f
                JOIN flashcard_decks d ON d.id = f.deck_id
                WHERE f.id = $1 AND d.student_id = $2
                """,
                card_id,
                user_id,
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Card not found"})

            ef, interval, count, next_review_at = apply_sm2_review(
                ease_factor=float(row["ease_factor"] or 2.5),
                interval_days=int(row["interval"] or 1),
                review_count=int(row["review_count"] or 0),
                quality=quality,
                now_utc=now,
            )

            updated = await conn.fetchrow(
                """
                UPDATE flashcards
                SET ease_factor = $2, interval = $3, review_count = $4, next_review_at = $5
                WHERE id = $1
                RETURNING id, ease_factor, interval, review_count, next_review_at
                """,
                card_id,
                ef,
                interval,
                count,
                next_review_at,
            )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to review card", "details": str(e)})

    return {
        "card": {
            "id": updated["id"],
            "ease_factor": float(updated["ease_factor"] or 2.5),
            "interval_days": int(updated["interval"] or 1),
            "review_count": int(updated["review_count"] or 0),
            "next_review_at": updated["next_review_at"].isoformat() if updated["next_review_at"] else None,
            "quality": quality,
        }
    }
