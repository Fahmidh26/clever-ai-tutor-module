from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.config import settings
from app.services import provider_registry
from app.services.ai_providers.base import ChatMessage
from app.services.chat_execution import collect_chat_with_strategy
from app.services.safety_guardrails import sanitize_assistant_output


@dataclass
class GeneratedFlashcard:
    front: str
    back: str


@dataclass
class GeneratedFlashcardsResult:
    cards: list[GeneratedFlashcard]
    model_used: str
    execution_attempts: list[dict[str, object]]


def _extract_json_array(raw: str) -> list[dict[str, object]] | None:
    match = re.search(r"\[[\s\S]*\]", raw)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except Exception:
        return None
    if not isinstance(parsed, list):
        return None
    rows: list[dict[str, object]] = []
    for item in parsed:
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _fallback_cards(*, topic: str | None, count: int) -> list[GeneratedFlashcard]:
    label = topic or "this topic"
    return [
        GeneratedFlashcard(
            front=f"What is one key idea in {label}?",
            back=f"A core idea in {label} is understanding definitions, patterns, and application steps.",
        )
        for _ in range(max(1, min(10, count)))
    ]


async def generate_flashcards(
    *,
    prompt: str,
    subject: str | None = None,
    topic: str | None = None,
    grade_level: int | None = None,
    count: int = 5,
) -> GeneratedFlashcardsResult:
    count = max(1, min(10, int(count)))
    if not provider_registry.registered_provider_names():
        return GeneratedFlashcardsResult(
            cards=_fallback_cards(topic=topic, count=count),
            model_used="fallback_heuristic",
            execution_attempts=[],
        )

    context = []
    if subject:
        context.append(f"Subject: {subject}")
    if topic:
        context.append(f"Topic: {topic}")
    if grade_level is not None:
        context.append(f"Grade level: {grade_level}")

    system_prompt = (
        "You generate study flashcards.\n"
        "Return ONLY a JSON array of objects with keys: front, back.\n"
        "Keep each front/back concise and factual."
    )
    user_prompt = (
        f"Generate {count} flashcards.\n"
        f"{chr(10).join(context) if context else 'No extra context.'}\n"
        f"Source prompt:\n{prompt}"
    )

    attempts: list[dict[str, object]] = []
    selected_model = settings.openai_default_model
    raw_text = ""
    try:
        raw_text, selected_model, attempts = await collect_chat_with_strategy(
            provider_registry=provider_registry,
            provider_name="openai",
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            primary_model=settings.openai_default_model,
            fallback_models=settings.llm_fallback_models_list,
            temperature=0.2,
            max_tokens=700,
            timeout_seconds=settings.llm_request_timeout_seconds,
            retry_attempts=settings.llm_retry_attempts,
            retry_backoff_seconds=settings.llm_retry_backoff_seconds,
        )
    except Exception:
        return GeneratedFlashcardsResult(
            cards=_fallback_cards(topic=topic, count=count),
            model_used="fallback_heuristic",
            execution_attempts=attempts,
        )

    parsed = _extract_json_array(sanitize_assistant_output(raw_text))
    if not parsed:
        return GeneratedFlashcardsResult(
            cards=_fallback_cards(topic=topic, count=count),
            model_used=selected_model,
            execution_attempts=attempts,
        )

    cards: list[GeneratedFlashcard] = []
    for item in parsed:
        front = str(item.get("front", "")).strip()
        back = str(item.get("back", "")).strip()
        if front and back:
            cards.append(GeneratedFlashcard(front=front, back=back))
    if not cards:
        cards = _fallback_cards(topic=topic, count=count)
    return GeneratedFlashcardsResult(cards=cards[:count], model_used=selected_model, execution_attempts=attempts)


def apply_sm2_review(
    *,
    ease_factor: float,
    interval_days: int,
    review_count: int,
    quality: int,
    now_utc: datetime | None = None,
) -> tuple[float, int, int, datetime]:
    quality = max(0, min(5, int(quality)))
    ef = float(ease_factor or 2.5)
    interval = int(interval_days or 1)
    count = int(review_count or 0)
    now = now_utc or datetime.now(UTC)

    if quality < 3:
        count = 0
        interval = 1
    else:
        if count == 0:
            interval = 1
        elif count == 1:
            interval = 6
        else:
            interval = max(1, int(round(interval * ef)))
        count += 1

    ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    ef = max(1.3, min(3.0, ef))
    next_review_at = now + timedelta(days=interval)
    return ef, interval, count, next_review_at
