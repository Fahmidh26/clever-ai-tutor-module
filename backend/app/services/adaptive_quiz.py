from __future__ import annotations

import json
import re
from dataclasses import dataclass

from app.config import settings
from app.services import provider_registry
from app.services.ai_providers.base import ChatMessage
from app.services.chat_execution import collect_chat_with_strategy
from app.services.safety_guardrails import sanitize_assistant_output


@dataclass
class QuizQuestion:
    question_text: str
    options: list[str]
    correct_answer: str
    explanation: str
    difficulty: int
    model_used: str
    execution_attempts: list[dict[str, object]]


def recommend_difficulty_from_recent_scores(recent_results: list[bool]) -> int:
    if not recent_results:
        return 2
    accuracy = sum(1 for v in recent_results if v) / max(1, len(recent_results))
    if accuracy >= 0.8:
        return 3
    if accuracy <= 0.4:
        return 1
    return 2


def _fallback_quiz(*, subject: str | None, topic: str | None, difficulty: int) -> QuizQuestion:
    scope = ", ".join([v for v in [subject, topic] if v]).strip()
    scoped_label = f" in {scope}" if scope else ""
    prompt = f"What is the best first step to solve a problem{scoped_label}?"
    options = [
        "Read the question carefully and identify given information.",
        "Skip planning and guess quickly.",
        "Memorize an unrelated formula.",
        "Ignore units and constraints.",
    ]
    return QuizQuestion(
        question_text=prompt,
        options=options,
        correct_answer="A",
        explanation="Start by understanding what is asked and what information is given.",
        difficulty=max(1, min(3, difficulty)),
        model_used="fallback_heuristic",
        execution_attempts=[],
    )


def _extract_json_block(text: str) -> str | None:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    return match.group(0)


def _parse_quiz_payload(raw: str, default_difficulty: int) -> tuple[str, list[str], str, str, int] | None:
    block = _extract_json_block(raw) or raw
    try:
        data = json.loads(block)
    except Exception:
        return None

    question = str(data.get("question", "")).strip()
    options_raw = data.get("options")
    if isinstance(options_raw, list):
        options = [str(item).strip() for item in options_raw if str(item).strip()]
    else:
        options = []
    answer = str(data.get("answer", "")).strip().upper()
    explanation = str(data.get("explanation", "")).strip()
    difficulty = int(data.get("difficulty", default_difficulty) or default_difficulty)
    difficulty = max(1, min(3, difficulty))

    if not question or len(options) < 2:
        return None
    if answer not in {"A", "B", "C", "D"}:
        return None
    if len(options) > 4:
        options = options[:4]
    while len(options) < 4:
        options.append(f"Option {chr(ord('A') + len(options))}")

    return question, options, answer, explanation or "Review the core concept and retry.", difficulty


async def generate_adaptive_quiz_question(
    *,
    subject: str | None = None,
    topic: str | None = None,
    grade_level: int | None = None,
    prompt_context: str | None = None,
    recommended_difficulty: int = 2,
) -> QuizQuestion:
    recommended_difficulty = max(1, min(3, int(recommended_difficulty)))

    if not provider_registry.registered_provider_names():
        return _fallback_quiz(subject=subject, topic=topic, difficulty=recommended_difficulty)

    system_prompt = (
        "You are an adaptive quiz generator.\n"
        "Return ONLY valid JSON with keys: question, options, answer, explanation, difficulty.\n"
        "Rules:\n"
        "- options must be an array of exactly 4 strings.\n"
        "- answer must be one of A, B, C, D.\n"
        "- Keep question concise and age-appropriate.\n"
        "- Do not include markdown or extra text outside JSON."
    )
    context_lines = []
    if subject:
        context_lines.append(f"Subject: {subject}")
    if topic:
        context_lines.append(f"Topic: {topic}")
    if grade_level is not None:
        context_lines.append(f"Grade level: {grade_level}")
    if prompt_context:
        context_lines.append(f"Student context: {prompt_context}")

    user_prompt = (
        f"Generate one multiple-choice question at difficulty {recommended_difficulty} (1 easy, 2 medium, 3 hard).\n"
        f"{chr(10).join(context_lines) if context_lines else 'No extra context.'}"
    )

    attempts: list[dict[str, object]] = []
    raw = ""
    selected_model = settings.openai_default_model
    try:
        raw, selected_model, attempts = await collect_chat_with_strategy(
            provider_registry=provider_registry,
            provider_name="openai",
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            primary_model=settings.openai_default_model,
            fallback_models=settings.llm_fallback_models_list,
            temperature=0.2,
            max_tokens=300,
            timeout_seconds=settings.llm_request_timeout_seconds,
            retry_attempts=settings.llm_retry_attempts,
            retry_backoff_seconds=settings.llm_retry_backoff_seconds,
        )
    except Exception:
        return _fallback_quiz(subject=subject, topic=topic, difficulty=recommended_difficulty)

    parsed = _parse_quiz_payload(sanitize_assistant_output(raw), recommended_difficulty)
    if not parsed:
        fallback = _fallback_quiz(subject=subject, topic=topic, difficulty=recommended_difficulty)
        fallback.execution_attempts = attempts
        return fallback

    question, options, answer, explanation, difficulty = parsed
    return QuizQuestion(
        question_text=question,
        options=options,
        correct_answer=answer,
        explanation=explanation,
        difficulty=difficulty,
        model_used=selected_model,
        execution_attempts=attempts,
    )


def evaluate_quiz_answer(*, selected_answer: str, correct_answer: str, explanation: str) -> tuple[bool, str]:
    normalized = (selected_answer or "").strip().upper()
    if normalized in {"A", "B", "C", "D"}:
        is_correct = normalized == correct_answer.strip().upper()
    else:
        is_correct = normalized == correct_answer.strip()
    if is_correct:
        return True, "Correct. Great work."
    return False, f"Not quite. Correct answer: {correct_answer}. {explanation}".strip()
