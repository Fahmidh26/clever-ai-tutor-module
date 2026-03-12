from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.services import provider_registry
from app.services.ai_providers.base import ChatMessage
from app.services.chat_execution import collect_chat_with_strategy
from app.services.safety_guardrails import sanitize_assistant_output


@dataclass
class ExplainMyAnswerResult:
    response: str
    model_used: str
    execution_attempts: list[dict[str, object]]


def _fallback_explanation(
    *,
    question_text: str,
    selected_answer: str,
    correct_answer: str,
    base_explanation: str,
    student_reasoning: str,
) -> str:
    correctness = "correct" if selected_answer.strip().upper() == correct_answer.strip().upper() else "not correct"
    return (
        f"Your answer ({selected_answer}) is {correctness}. "
        f"Question focus: {question_text}\n"
        f"What you wrote: {student_reasoning}\n"
        f"Key correction: {base_explanation}\n"
        "Next step: restate the rule in one sentence, then solve a similar problem using that rule."
    )


async def explain_student_answer(
    *,
    question_text: str,
    selected_answer: str,
    correct_answer: str,
    base_explanation: str,
    student_reasoning: str,
    subject: str | None = None,
    topic: str | None = None,
    grade_level: int | None = None,
) -> ExplainMyAnswerResult:
    if not provider_registry.registered_provider_names():
        return ExplainMyAnswerResult(
            response=_fallback_explanation(
                question_text=question_text,
                selected_answer=selected_answer,
                correct_answer=correct_answer,
                base_explanation=base_explanation,
                student_reasoning=student_reasoning,
            ),
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
        "You are a tutor running an 'Explain My Answer' workflow.\n"
        "Your job: diagnose student reasoning, identify misconception, and give an actionable fix.\n"
        "Keep response concise and structured:\n"
        "1) What was right\n"
        "2) Where reasoning broke\n"
        "3) Correct principle\n"
        "4) One short retry step\n"
        "Do not shame the student."
    )
    user_prompt = (
        f"{chr(10).join(context) if context else 'No extra context.'}\n"
        f"Question: {question_text}\n"
        f"Student selected: {selected_answer}\n"
        f"Correct answer: {correct_answer}\n"
        f"Base explanation: {base_explanation}\n"
        f"Student reasoning: {student_reasoning}\n"
        "Generate personalized feedback."
    )

    attempts: list[dict[str, object]] = []
    response_text = ""
    selected_model = settings.openai_default_model
    try:
        response_text, selected_model, attempts = await collect_chat_with_strategy(
            provider_registry=provider_registry,
            provider_name="openai",
            messages=[
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ],
            primary_model=settings.openai_default_model,
            fallback_models=settings.llm_fallback_models_list,
            temperature=0.2,
            max_tokens=320,
            timeout_seconds=settings.llm_request_timeout_seconds,
            retry_attempts=settings.llm_retry_attempts,
            retry_backoff_seconds=settings.llm_retry_backoff_seconds,
        )
    except Exception:
        return ExplainMyAnswerResult(
            response=_fallback_explanation(
                question_text=question_text,
                selected_answer=selected_answer,
                correct_answer=correct_answer,
                base_explanation=base_explanation,
                student_reasoning=student_reasoning,
            ),
            model_used="fallback_heuristic",
            execution_attempts=attempts,
        )

    return ExplainMyAnswerResult(
        response=sanitize_assistant_output(response_text),
        model_used=selected_model,
        execution_attempts=attempts,
    )
