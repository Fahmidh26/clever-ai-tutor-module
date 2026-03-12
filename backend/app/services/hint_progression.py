from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.services import provider_registry
from app.services.ai_providers.base import ChatMessage
from app.services.chat_execution import collect_chat_with_strategy
from app.services.safety_guardrails import sanitize_assistant_output


@dataclass
class HintGenerationResult:
    hint: str
    model_used: str
    execution_attempts: list[dict[str, object]]


def _fallback_hint(*, problem_text: str, level: int, subject: str | None, topic: str | None) -> str:
    scope = ""
    if subject or topic:
        parts = [part for part in [subject, topic] if part]
        scope = f" ({' / '.join(parts)})"

    if level == 1:
        return (
            f"Level 1 hint{scope}: Identify what the question is asking for, then list the given information "
            "before doing any calculations."
        )
    if level == 2:
        return (
            f"Level 2 hint{scope}: Choose the key rule or concept that connects the given information to the target. "
            "Write the rule first, then map each value to it."
        )
    return (
        f"Level 3 hint{scope}: Break the solution into small steps, solve each step in order, and check units/signs "
        "after every step. If one step fails, redo only that step."
    )


async def generate_hint(
    *,
    problem_text: str,
    level: int,
    subject: str | None = None,
    topic: str | None = None,
    grade_level: int | None = None,
    prior_hints: list[str] | None = None,
) -> HintGenerationResult:
    level = max(1, min(3, int(level)))
    prior_hints = [h.strip() for h in (prior_hints or []) if h and h.strip()]

    if not provider_registry.registered_provider_names():
        return HintGenerationResult(
            hint=_fallback_hint(problem_text=problem_text, level=level, subject=subject, topic=topic),
            model_used="fallback_heuristic",
            execution_attempts=[],
        )

    context_lines = []
    if subject:
        context_lines.append(f"Subject: {subject}")
    if topic:
        context_lines.append(f"Topic: {topic}")
    if grade_level is not None:
        context_lines.append(f"Grade level: {grade_level}")

    prior_block = "\n".join(f"- {item}" for item in prior_hints)
    prior_section = f"\nPrevious hints already shown:\n{prior_block}\nDo not repeat them." if prior_block else ""

    system_prompt = (
        "You are an educational tutor generating progressive hints only.\n"
        "Never provide the final answer.\n"
        "Hint Levels:\n"
        "Level 1: gentle nudge in one sentence.\n"
        "Level 2: relevant concept/rule in up to two sentences.\n"
        "Level 3: step-by-step approach without solving the final result.\n"
        "Keep tone concise, clear, and age-appropriate."
    )

    user_prompt = (
        f"Generate level {level} hint.\n"
        f"{chr(10).join(context_lines) if context_lines else 'No subject/topic context provided.'}\n"
        f"Problem:\n{problem_text}\n"
        f"{prior_section}"
    )

    attempts: list[dict[str, object]] = []
    hint_text = ""
    selected_model = settings.openai_default_model
    try:
        hint_text, selected_model, attempts = await collect_chat_with_strategy(
            provider_registry=provider_registry,
            provider_name="openai",
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            primary_model=settings.openai_default_model,
            fallback_models=settings.llm_fallback_models_list,
            temperature=0.1,
            max_tokens=220,
            timeout_seconds=settings.llm_request_timeout_seconds,
            retry_attempts=settings.llm_retry_attempts,
            retry_backoff_seconds=settings.llm_retry_backoff_seconds,
        )
    except Exception:
        return HintGenerationResult(
            hint=_fallback_hint(problem_text=problem_text, level=level, subject=subject, topic=topic),
            model_used="fallback_heuristic",
            execution_attempts=attempts,
        )

    return HintGenerationResult(
        hint=sanitize_assistant_output(hint_text),
        model_used=selected_model,
        execution_attempts=attempts,
    )
