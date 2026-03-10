# Session Handoff (Resume Template)

Use this file when starting a new chat/session so work continues exactly where it stopped.

## Quick Resume Prompt (Copy/Paste)

Continue this project from `AI_TUTOR_PROGRESS_CHECKLIST.md` and `WORKLOG.md`.
Current roadmap source: `AI_TUTOR_MODULE (1).md`.
Run one task at a time in order.
Start from: `<PUT_NEXT_TASK_ID_HERE>` (for example: `1.2.1`).
After each task: implement, validate, and update checklist + worklog.

## Current Status Snapshot

- Completed: Phase 1, Sprint 1.1 (`1.1.1` to `1.1.15`)
- Next: Sprint 1.2
- Suggested next task: `1.2.1` (RootSiteClient service)

## Rules For Continuation

- Follow strict order from checklist
- Do not skip validation (build/lint/syntax checks)
- Keep main-site integration (`:8000`) working
- Update:
  - `AI_TUTOR_PROGRESS_CHECKLIST.md`
  - `WORKLOG.md`

## Optional Detailed Resume Prompt

Resume implementation for `D:\USA\clever-ai-tutor`.
Use `AI_TUTOR_PROGRESS_CHECKLIST.md` as source of truth.
Do exactly one next unchecked roadmap task, in order.
Implement code changes directly, run validations, then update progress docs.
If a command/tool fails, fix and continue automatically.
