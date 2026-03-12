from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class MisconceptionSignal:
    misconception_type: str
    description: str


def detect_misconception(
    *,
    question_text: str,
    selected_answer: str,
    correct_answer: str,
    explanation: str,
    student_reasoning: str | None = None,
) -> MisconceptionSignal:
    reasoning = (student_reasoning or "").strip().lower()
    question = (question_text or "").strip().lower()
    explanation_norm = (explanation or "").strip().lower()

    if re.search(r"unit|dimension", reasoning) and "unit" in explanation_norm:
        return MisconceptionSignal(
            misconception_type="unit_confusion",
            description="Student reasoning suggests unit/dimension mismatch.",
        )
    if "formula" in reasoning and ("rule" in explanation_norm or "formula" in explanation_norm):
        return MisconceptionSignal(
            misconception_type="formula_misapplication",
            description="Likely used an incorrect formula or applied the right formula in the wrong context.",
        )
    if selected_answer.strip().upper() in {"A", "B", "C", "D"} and correct_answer.strip().upper() in {"A", "B", "C", "D"}:
        return MisconceptionSignal(
            misconception_type="concept_selection_error",
            description=f"Selected option {selected_answer.upper()} instead of {correct_answer.upper()}; concept selection likely incorrect.",
        )
    if "not" in question and "not" not in reasoning:
        return MisconceptionSignal(
            misconception_type="question_misread",
            description="Question likely misread or key constraint was missed.",
        )
    return MisconceptionSignal(
        misconception_type="general_concept_gap",
        description="Incorrect response indicates a concept gap that needs targeted review.",
    )
