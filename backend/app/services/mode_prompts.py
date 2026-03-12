"""
7 interaction modes — mode definitions and prompt builder.
Per AI_TUTOR_MODULE spec: Teach Me, Quiz Me, Hint, Apply It, Show Thinking, Writing Workshop, Debate/Roleplay.
"""
from __future__ import annotations

MODE_DEFINITIONS = [
    {
        "id": "teach_me",
        "name": "Teach Me",
        "description": "Full explanation with examples; uses student interests for analogies",
        "phase": 1,
    },
    {
        "id": "quiz_me",
        "name": "Quiz Me",
        "description": "Asks one question, waits for answer, gives detailed feedback, escalates difficulty",
        "phase": 1,
    },
    {
        "id": "hint",
        "name": "Hint",
        "description": "Progressive hints (3 levels): nudge → direction → approach (no answer)",
        "phase": 1,
    },
    {
        "id": "apply_it",
        "name": "Apply It",
        "description": "Presents a real-world scenario that uses the concept",
        "phase": 1,
    },
    {
        "id": "show_thinking",
        "name": "Show Your Thinking",
        "description": "Student explains reasoning step-by-step; AI evaluates the process, not just the answer",
        "phase": 1,
    },
    {
        "id": "writing_workshop",
        "name": "Writing Workshop",
        "description": "Coach through drafts with rubric-based feedback; never writes for the student",
        "phase": 1,
    },
    {
        "id": "debate_roleplay",
        "name": "Debate/Roleplay",
        "description": "Debate historical events, roleplay as scientists, practice language in real scenarios",
        "phase": 3,
    },
]

MODE_IDS = {m["id"] for m in MODE_DEFINITIONS}
DEFAULT_MODE = "teach_me"

# Legacy DB values (e.g. init.sql default 'teach') -> canonical mode id
_LEGACY_MODE_MAP = {"teach": "teach_me", "quiz": "quiz_me"}


def normalize_mode(raw: str | None) -> str:
    """Convert legacy or raw mode string to canonical mode id."""
    s = (raw or "").strip().lower() or DEFAULT_MODE
    mapped = _LEGACY_MODE_MAP.get(s, s)
    return mapped if mapped in MODE_IDS else DEFAULT_MODE


UNIVERSAL_RULES = """
UNIVERSAL RULES:
1. Use the student's interests for analogies where natural.
2. Never write essays, complete assignments, or do homework for the student.
3. If a student seems frustrated, acknowledge it and adjust approach.
4. Keep responses appropriately concise. Break long explanations into steps.
5. Use LaTeX notation for math (wrapped in $ or $$).
6. Use markdown formatting for structure.
7. Adjust vocabulary complexity to grade level.
8. If the topic is outside your expertise, say so honestly.
9. End responses with a natural next step (question, suggestion, encouragement).
"""


def get_mode_prompt_injection(mode: str, hint_level: int | None = None, grade_level: int | None = None) -> str:
    """Return mode-specific prompt instructions to append to the system prompt."""
    mode = (mode or "").strip().lower() or DEFAULT_MODE
    grade_level = grade_level or 8

    if mode == "quiz_me":
        return f"""
QUIZ MODE ACTIVE. Generate exactly ONE question appropriate for grade level {grade_level}.
Ask the question clearly. Do NOT provide hints or answers yet.
After the student responds, give detailed feedback: correct/incorrect + why + right approach.
"""

    if mode == "hint":
        level = max(1, min(3, hint_level or 1))
        return f"""
HINT MODE ACTIVE. Hint level requested: {level}/3.
DO NOT solve the problem. DO NOT give the answer.
Provide ONLY a Level {level} hint:
  Level 1: A gentle nudge in the right direction (1 sentence)
  Level 2: Point to the relevant concept or rule (2 sentences)
  Level 3: Describe the approach step by step WITHOUT solving it
"""

    if mode == "show_thinking":
        return """
METACOGNITION MODE ACTIVE. The student will explain their reasoning step by step.
Evaluate the PROCESS of their thinking, not just the final answer.
Identify exactly where reasoning breaks down.
Provide feedback on logical structure, assumptions, and justification quality.
"""

    if mode == "writing_workshop":
        return """
WRITING WORKSHOP MODE. The student has submitted a draft for feedback.
NEVER rewrite or write for the student.
Provide specific, actionable feedback using the rubric:
  - Thesis clarity
  - Evidence and support
  - Organization and flow
  - Voice and style
  - Grammar and mechanics
Ask guiding questions: "What evidence supports this claim?"
"""

    if mode == "apply_it":
        return """
APPLY IT MODE ACTIVE. Present a real-world scenario that uses the concept.
Make it concrete and relatable. Show how the concept applies in practice.
"""

    if mode == "debate_roleplay":
        return """
DEBATE/ROLEPLAY MODE ACTIVE. Engage in scenario-based learning.
Debate historical events, roleplay as experts, or practice language in real-world scenarios.
Stay in character and encourage the student to participate actively.
"""

    # teach_me (default) — no special injection, just general tutoring
    return """
TEACH ME MODE. Provide structured explanation with examples.
Use the student's interests for analogies where natural.
Offer to rephrase or give another example if needed.
"""


def build_system_prompt(
    base_prompt: str,
    mode: str = "teach_me",
    hint_level: int | None = None,
    grade_level: int | None = None,
) -> str:
    """Combine base persona prompt with mode-specific instructions and universal rules."""
    mode_injection = get_mode_prompt_injection(mode, hint_level, grade_level)
    return f"{base_prompt}\n\n{mode_injection}\n{UNIVERSAL_RULES}"
