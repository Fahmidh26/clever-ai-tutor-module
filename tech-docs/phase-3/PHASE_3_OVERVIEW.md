# Grand Phase 3: Advanced Features — Overview

> **Status**: Not Started
> **Branch**: `phase-3` (to be created from `phase-2`)
> **Dependencies**: Grand Phases 1–2 complete
> **Target Users**: Students (K-12), Parents, Teachers, Educators, Administrators

---

## Phase Terminology

| Term | Meaning | Example |
|------|---------|---------|
| **Grand Phase** | Top-level milestone (1, 2, 3) | Grand Phase 3: Advanced Features |
| **Functional Phase** | Self-contained feature set within a Grand Phase | FP 3.1: Gamification |
| **Sprint Task** | Individual implementation task | 3.1.1: XP System |

---

## Functional Phase Summary

| # | Functional Phase | Document | Est. Duration | Dependencies | Priority |
|---|-----------------|----------|---------------|--------------|----------|
| 3.1 | Gamification & Streak Systems | [PHASE_3.1_GAMIFICATION.md](PHASE_3.1_GAMIFICATION.md) | 2 weeks | Phase 2 (mastery, quiz, flashcards) | P0 — High |
| 3.2 | Parent Dashboard & Co-Learning | [PHASE_3.2_PARENT_DASHBOARD.md](PHASE_3.2_PARENT_DASHBOARD.md) | 2 weeks | Phase 2, parent_student_links, RBAC | P0 — High |
| 3.3 | Whiteboard, Code Sandbox, Math Editor | [PHASE_3.3_INTERACTIVE_TOOLS.md](PHASE_3.3_INTERACTIVE_TOOLS.md) | 2 weeks | Phase 1.5 (chat UI), Docker sandbox | P1 — Medium |
| 3.4 | Audio Lessons, Mind Maps, Memory Score | [PHASE_3.4_AUDIO_MINDMAPS_MEMORY.md](PHASE_3.4_AUDIO_MINDMAPS_MEMORY.md) | 2 weeks | Phase 2 (flashcards, mastery), TTS API | P1 — Medium |
| 3.5 | Educational Gaming Engine | [PHASE_3.5_GAMING_ENGINE.md](PHASE_3.5_GAMING_ENGINE.md) | 3 weeks | FP 3.1 (gamification/XP), mastery | P1 — Medium |
| 3.6 | Test Prep Framework (IELTS/SAT/ACT/AP) | [PHASE_3.6_TEST_PREP.md](PHASE_3.6_TEST_PREP.md) | 3 weeks | Quiz engine, mastery, flashcards | P1 — Medium |
| 3.7 | Compliance, Accessibility, i18n | [PHASE_3.7_COMPLIANCE_A11Y_I18N.md](PHASE_3.7_COMPLIANCE_A11Y_I18N.md) | 3 weeks | All prior phases (audit & harden) | P0 — High |

**Total estimated duration**: ~17 weeks (with parallelization opportunities)

---

## Recommended Execution Order

```
Week 1-2:   FP 3.1 Gamification (foundation for XP/rewards across all features)
Week 2-4:   FP 3.2 Parent Dashboard (parallel with tail of 3.1)
Week 4-6:   FP 3.3 Interactive Tools (whiteboard/code/math)
Week 6-8:   FP 3.4 Audio/Mind Maps/Memory Score
Week 8-11:  FP 3.5 Gaming Engine (depends on 3.1 XP system)
Week 11-14: FP 3.6 Test Prep Framework
Week 14-17: FP 3.7 Compliance/A11y/i18n (hardening pass over everything)
```

FP 3.7 (Compliance) should also have incremental checks during each prior phase — don't wait until the end for accessibility and compliance considerations.

---

## Cross-Cutting Concerns (Apply to ALL Functional Phases)

### UI/UX Consistency
- All pages use Tailwind 4 utility classes + shadcn/ui components (new-york style)
- NO hardcoded CSS, NO inline styles, NO CSS modules
- OKLCH color system (light/dark) from `globals.css`
- Responsive: mobile (<640px), tablet (640-1024px), desktop (>1024px)
- Age-adaptive: K-2 / 3-5 / 6-8 / 9-12 grade bands

### Architecture Pattern
- Backend: FastAPI router + service + asyncpg (raw SQL)
- Frontend: Next.js App Router + Zustand store + api-client.ts
- Real-time: SSE for streaming, WebSocket for collaborative features
- Background: Celery tasks for heavy/scheduled processing

### Security & Compliance
- RBAC at every endpoint (student/teacher/parent/admin)
- COPPA, FERPA, GDPR awareness in every feature
- Audit logging for data modifications
- No PII in logs or error reports

### Testing
- Backend: pytest async tests for every new endpoint
- Frontend: Playwright E2E specs for critical user journeys
- Accessibility: axe-core automated audits (Phase 3.7 formalizes)

---

## New Database Tables Summary (Across All FPs)

| Functional Phase | New Tables |
|-----------------|------------|
| 3.1 Gamification | `challenges`, `challenge_attempts`, `reward_items`, `student_rewards` |
| 3.2 Parent Dashboard | `parent_alerts`, `parent_teacher_messages`, `co_learning_sessions` |
| 3.3 Interactive Tools | `whiteboard_states`, `code_executions`, `code_challenges` |
| 3.4 Audio/Mind Maps | `audio_lessons`, `mind_maps`, `memory_scores`, `roleplay_sessions` |
| 3.5 Gaming Engine | `game_templates`, `game_sessions`, `game_assignments`, `game_leaderboard` |
| 3.6 Test Prep | `test_profiles`, `student_test_prep`, `mock_test_attempts`, `speaking_attempts`, `writing_attempts` |
| 3.7 Compliance | `audit_log`, `consent_records`, `data_retention_policies`, `user_preferences` |

**Note**: Some tables already exist in `init.sql` (e.g., `student_xp`, `badges`, `parent_student_links`, `content_restrictions`, `concept_nodes`). Always check existing schema before creating new tables.

---

## New Frontend Packages (Across All FPs)

| Package | Version | Functional Phase | Purpose |
|---------|---------|-----------------|---------|
| `tldraw` | 4.3.x | 3.3 | Digital whiteboard |
| `@monaco-editor/react` | latest | 3.3 | Code editor |
| `mathlive` | 0.108.x | 3.3 | Math input |
| `react-flow` | latest | 3.4 | Mind map rendering |
| `next-intl` | latest | 3.7 | Internationalization |

---

## New Zustand Stores (Across All FPs)

| Store | Functional Phase | Key State |
|-------|-----------------|-----------|
| `gamification-store.ts` | 3.1 | xp, level, streak, badges, leaderboard |
| `parent-store.ts` | 3.2 | children, activeChild, alerts, controls |
| `tools-store.ts` | 3.3 | activePanel, whiteboardState, codeState |
| `study-tools-store.ts` | 3.4 | audioLessons, mindMaps, memoryScores |
| `games-store.ts` | 3.5 | gameSession, templates, leaderboard |
| `test-prep-store.ts` | 3.6 | enrollment, mockTest, studyPlan |
| `preferences-store.ts` | 3.7 | language, accessibility, wellness |
