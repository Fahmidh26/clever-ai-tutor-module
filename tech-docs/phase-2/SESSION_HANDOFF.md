# Session Handoff (Resume Template)

Use this file when starting a new chat/session so work continues exactly where it stopped.

## Quick Resume Prompt (Copy/Paste)

Continue this project from `tech-docs/phase-2/AI_TUTOR_PROGRESS_CHECKLIST.md` and `tech-docs/phase-1/WORKLOG.md`.
**Master rules**: Read `AGENTS.md` in project root first — it contains all conventions, guidelines, and architecture rules.
**Architecture**: Read `tech-docs/phase-1/ARCHITECTURE.md` — main site = auth/billing/credits only; experts/chat/sessions = local.
Current roadmap source: `tech-docs/phase-1/AI_TUTOR_MODULE.md`.
Phase 3 functional phase specs: `tech-docs/phase-3/PHASE_3_OVERVIEW.md`.
Main site (auth/billing/credits only): `C:\AISITENEW`.
Run one task at a time in order.
Start from: `<PUT_NEXT_TASK_ID_HERE>` (for example: `3.1.1`).
After each task: implement, validate, and update checklist + worklog.

## Current Status Snapshot

- Completed: Phase 1 (Foundation, Auth, Core Engine, RAG, UI/UX) — ~93%
- Completed: Phase 2 (Intelligence Layer — hints, quiz, flashcards, mastery, misconceptions, dashboards) — 100%
- Current: Grand Phase 3 — Advanced Features — 0% (7 functional phases)
- Pending from Phase 1: `1.1.1` Python project init (pyproject.toml)
- Suggested next: Start FP 3.1 (Gamification) at task `3.1.1` (XP system)

## Phase 3 Functional Phases (in recommended order)

1. **FP 3.1** Gamification & Streak Systems — `tech-docs/phase-3/PHASE_3.1_GAMIFICATION.md`
2. **FP 3.2** Parent Dashboard & Co-Learning — `tech-docs/phase-3/PHASE_3.2_PARENT_DASHBOARD.md`
3. **FP 3.3** Whiteboard, Code Sandbox, Math Editor — `tech-docs/phase-3/PHASE_3.3_INTERACTIVE_TOOLS.md`
4. **FP 3.4** Audio Lessons, Mind Maps, Memory Score — `tech-docs/phase-3/PHASE_3.4_AUDIO_MINDMAPS_MEMORY.md`
5. **FP 3.5** Educational Gaming Engine — `tech-docs/phase-3/PHASE_3.5_GAMING_ENGINE.md`
6. **FP 3.6** Test Prep Framework — `tech-docs/phase-3/PHASE_3.6_TEST_PREP.md`
7. **FP 3.7** Compliance, Accessibility, i18n — `tech-docs/phase-3/PHASE_3.7_COMPLIANCE_A11Y_I18N.md`

## Rules For Continuation

- Follow strict order from checklist
- Do not skip validation (build/lint/syntax checks)
- **Architecture**: Main site only for auth, billing, credit deduction. Experts, chat, sessions run locally in tutor. See `tech-docs/phase-1/ARCHITECTURE.md`.
- **Code conventions**: Tailwind utility classes only (no hardcoded CSS), shadcn/ui components, asyncpg raw SQL (no ORM). See `AGENTS.md`.
- Keep main-site integration (`:8000`) for auth and credits only
- If shared APIs/data are needed, update both repos:
  - Tutor app: `D:\USA\clever-ai-tutor`
  - Main site: `C:\AISITENEW`
- Update after each task:
  - `tech-docs/phase-2/AI_TUTOR_PROGRESS_CHECKLIST.md`
  - `tech-docs/phase-1/WORKLOG.md`

## Documentation Map

```
AGENTS.md                                    ← Master rules (root)
tech-docs/phase-1/ARCHITECTURE.md            ← Core architecture
tech-docs/phase-1/AI_TUTOR_MODULE.md         ← Master specification
tech-docs/phase-1/AI_TUTOR_PLAN.md           ← Original roadmap
tech-docs/phase-1/AI_TUTOR_TESTING_GUIDE.md  ← Testing reference
tech-docs/phase-1/WORKLOG.md                 ← Development history
tech-docs/phase-2/AI_TUTOR_PROGRESS_CHECKLIST.md ← Progress tracker
tech-docs/phase-2/USER_FLOWS_DIAGRAMS.md     ← UX flow reference
tech-docs/phase-3/PHASE_3_OVERVIEW.md        ← Phase 3 summary
tech-docs/phase-3/PHASE_3.X_*.md             ← Functional phase specs
```

## Optional Detailed Resume Prompt

Resume implementation for `D:\USA\clever-ai-tutor`.
Read `AGENTS.md` for all rules and conventions.
Use `tech-docs/phase-2/AI_TUTOR_PROGRESS_CHECKLIST.md` as source of truth.
Main site path for coordinated API changes: `C:\AISITENEW`.
Do exactly one next unchecked roadmap task, in order.
Implement code changes directly, run validations, then update progress docs.
If a command/tool fails, fix and continue automatically.
