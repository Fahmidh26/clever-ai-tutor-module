from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MasteryUpdateResult:
    mastery_level: int
    reasoning_quality: int


def clamp_mastery(level: int) -> int:
    return max(0, min(5, int(level)))


def estimate_reasoning_quality(*, is_correct: bool, used_explain_my_answer: bool = False) -> int:
    base = 4 if is_correct else 2
    if used_explain_my_answer:
        base += 1
    return max(1, min(5, base))


def next_mastery_level(
    *,
    current_level: int,
    is_correct: bool,
    recent_accuracy: float | None = None,
) -> int:
    level = clamp_mastery(current_level)
    if is_correct:
        level += 1
    else:
        level -= 1

    if recent_accuracy is not None:
        if recent_accuracy >= 0.85:
            level += 1
        elif recent_accuracy <= 0.35:
            level -= 1
    return clamp_mastery(level)
