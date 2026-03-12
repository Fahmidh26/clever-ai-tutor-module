# Session Handoff (Resume Template)

Use this file when starting a new chat/session so work continues exactly where it stopped.

## Quick Resume Prompt (Copy/Paste)

Continue this project from `AI_TUTOR_PROGRESS_CHECKLIST.md` and `WORKLOG.md`.
**Architecture**: Read `ARCHITECTURE.md` first — main site = auth/billing/credits only; experts/chat/sessions = local.
Current roadmap source: `AI_TUTOR_MODULE (1).md`.
Main site (auth/billing/credits only): `C:\AISITENEW`.
Run one task at a time in order.
Start from: `<PUT_NEXT_TASK_ID_HERE>` (for example: `1.3.3`).
After each task: implement, validate, and update checklist + worklog.

## Current Status Snapshot

- Completed: Phase 1 Sprint 1.1 and Sprint 1.2 (`1.1.x`, `1.2.x`)
- Current: Architecture clarified — main site only for auth/billing/credits; experts/chat/sessions are local
- Suggested next task: Migrate experts/chat to local tutor APIs (see `ARCHITECTURE.md`)

## Rules For Continuation

- Follow strict order from checklist
- Do not skip validation (build/lint/syntax checks)
- **Architecture**: Main site only for auth, billing, credit deduction. Experts, chat, sessions run locally in tutor. See `ARCHITECTURE.md`.
- Keep main-site integration (`:8000`) for auth and credits only
- If shared APIs/data are needed, update both repos:
  - Tutor app: `D:\USA\clever-ai-tutor`
  - Main site: `C:\AISITENEW`
- Update:
  - `AI_TUTOR_PROGRESS_CHECKLIST.md`
  - `WORKLOG.md`

## Optional Detailed Resume Prompt

Resume implementation for `D:\USA\clever-ai-tutor`.
Use `AI_TUTOR_PROGRESS_CHECKLIST.md` as source of truth.
Main site path for coordinated API changes: `C:\AISITENEW`.
Do exactly one next unchecked roadmap task, in order.
Implement code changes directly, run validations, then update progress docs.
If a command/tool fails, fix and continue automatically.
