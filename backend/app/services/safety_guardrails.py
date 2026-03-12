from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class GuardrailDecision:
    blocked: bool
    code: str | None = None
    message: str | None = None


_PROMPT_INJECTION_PATTERNS = (
    re.compile(r"\bignore (all )?(previous|prior) instructions\b", re.IGNORECASE),
    re.compile(r"\breveal\b.*\b(system prompt|hidden prompt|developer prompt)\b", re.IGNORECASE),
    re.compile(r"\bjailbreak\b", re.IGNORECASE),
)

_HARMFUL_REQUEST_PATTERNS = (
    re.compile(r"\bhow to (make|build)\b.*\b(bomb|explosive|weapon)\b", re.IGNORECASE),
    re.compile(r"\bhow to (hack|ddos|phish|steal)\b", re.IGNORECASE),
    re.compile(r"\bself[- ]?harm\b|\bsuicide\b|\bkill myself\b", re.IGNORECASE),
)


def check_user_message(text: str) -> GuardrailDecision:
    message = (text or "").strip()
    if not message:
        return GuardrailDecision(blocked=False)

    for pattern in _PROMPT_INJECTION_PATTERNS:
        if pattern.search(message):
            return GuardrailDecision(
                blocked=True,
                code="prompt_injection_blocked",
                message="I can help with learning tasks, but I cannot follow unsafe instruction-bypass requests.",
            )

    for pattern in _HARMFUL_REQUEST_PATTERNS:
        if pattern.search(message):
            return GuardrailDecision(
                blocked=True,
                code="unsafe_content_blocked",
                message="I can help with safe educational content, but I can't assist with harmful requests.",
            )

    return GuardrailDecision(blocked=False)


def sanitize_assistant_output(text: str) -> str:
    response = (text or "").strip()
    if not response:
        return response

    # Block accidental system-prompt disclosure and unsafe direct harm instructions.
    if re.search(r"\b(system prompt|developer prompt|hidden instructions)\b", response, re.IGNORECASE):
        return "I can continue helping with the lesson, but I cannot disclose internal instructions."
    if re.search(r"\b(make|build)\b.*\b(bomb|explosive|weapon)\b", response, re.IGNORECASE):
        return "I can't provide harmful instructions. I can help with safe science learning instead."
    return response

