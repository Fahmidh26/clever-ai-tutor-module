# AI Tutor Progress Checklist

> Repos in scope:
> - Tutor app: `D:\USA\clever-ai-tutor`
> - Main site (auth/billing/credits only): `C:\AISITENEW`

> **Architecture**: Main site = auth, billing, credit deduction. Experts, chat, sessions = local tutor APIs. See `tech-docs/phase-1/ARCHITECTURE.md`.
> Tracking against `tech-docs/phase-1/AI_TUTOR_MODULE.md` roadmap
> Baseline estimate uses current `tech-docs/phase-1/WORKLOG.md` state
> **Master Rules**: See `AGENTS.md` in project root for all conventions and guidelines.
> **Teacher planning follow-up**: See `tech-docs/phase-2/PHASE_2_TEACHER_SECTION_PLAN.md` and `tech-docs/phase-2/PHASE_2_TEACHER_TRACKER.md`.

---

## Implementation vs Architecture (Audit 2026-03)

| Area | Architecture (target) | Current code | Status |
|------|------------------------|--------------|--------|
| Auth | Main site | Main site OAuth + tutor session | ✅ Aligned |
| Credits | Main site | Main site deduct | ✅ Aligned |
| Experts | Local tutor | Local `/api/experts` from tutor_personas | ✅ Aligned |
| Chat | Local tutor | Local `/api/expert-chat` with OpenAI + credit deduct | ✅ Aligned |
| Sessions | Local tutor | Local `/api/tutor/sessions*` + message persistence | ✅ Aligned |

Frontend calls `/api/experts` and `/api/expert-chat` (local). Proxy blocked for experts/chat paths.

---

## Overall Progress Snapshot (Estimated)

- Foundation setup: **~93%** (pending `1.1.1`)
- Main-site auth/API integration: **100%**
- Core tutoring engine (local per ARCHITECTURE): **~85%** - experts + chat + sessions + streaming + 7 modes; multi-provider local wiring pending
- RAG + teacher knowledge base: **100%**
- UX polish + adaptive UI: **100%**
- Intelligence (mastery/quiz/hints): **100%** (Phase 2 core complete)
- Grand Phase 3 — FP 3.1 Gamification: **0%**
- Grand Phase 3 — FP 3.2 Parent Dashboard: **0%**
- Grand Phase 3 — FP 3.3 Interactive Tools: **0%**
- Grand Phase 3 — FP 3.4 Audio/Mind Maps/Memory: **0%**
- Grand Phase 3 — FP 3.5 Gaming Engine: **0%**
- Grand Phase 3 — FP 3.6 Test Prep: **0%**
- Grand Phase 3 — FP 3.7 Compliance/A11y/i18n: **0%**

**Estimated overall completion (MVP path): ~72%**
**Estimated Phase 3 duration: ~17 weeks**

> **Current working state**: Experts, chat, sessions run locally. 7 interaction modes via `mode` param. `GET /api/tutor/modes`, `PATCH /api/tutor/sessions/{id}/mode`.

---

## Teacher Section Follow-Up

- [x] Teacher ecosystem architecture mapped inside the same RBAC-driven app shell
- [x] Teacher workflow diagrams and student handoff points documented
- [x] Teacher implementation tracker created
- [x] Agent testing workflow updated for teacher/RBAC validation
- [x] Browser smoke coverage added for teacher dashboard and role routing
- [x] Teacher roster handshake and invite-code model implementation
- [x] Teacher class cockpit refinement
- [x] Class-level persona policy
- [x] Session replay and at-risk monitoring
- [x] Parent handoff summary objects
- [x] Teacher testing guide with seeded data and validation flow

---

## 1) Foundation & DevOps (Phase 1.1)

- [ ] `1.1.1` Initialize Python project (`pyproject.toml`, Poetry/uv, Python 3.13)
- [x] `1.1.2` FastAPI app skeleton with router structure
- [x] `1.1.3` Pydantic v2 settings management (`config.py` env validation)
- [x] `1.1.4` Structured logging (structlog + OpenTelemetry baseline)
- [x] `1.1.5` asyncpg connection pool setup with health checks
- [x] `1.1.6` Next.js 16 project with App Router + TypeScript strict mode
- [x] `1.1.7` Tailwind 4 + shadcn/ui 4 setup and theming
- [x] `1.1.8` Zustand 5 store skeleton (auth/session/ui/chat)
- [x] `1.1.9` API client layer with interceptors/retry/error handling
- [x] `1.1.10` Layout shell (sidebar/header/main)
- [x] `1.1.11` Docker Compose with core services
- [x] `1.1.12` PostgreSQL init.sql with full schema + indexes
- [x] `1.1.13` Seed data SQL (personas, subjects, topics, standards)
- [x] `1.1.14` Makefile/scripts (dev, test, migrate, seed, lint, format)
- [x] `1.1.15` CI pipeline skeleton (lint, type-check, test)

---

## 2) Authentication + Root-Site Integration (Phase 1.2)

- [x] `1.2.1` RootSiteClient service (OAuth/JWT/user/credits/catalog/plan checks)
- [x] `1.2.2` Auth middleware (JWT/session extraction and user context)
- [x] `1.2.3` Internal `X-Auth-Hex` header for service-to-service calls
- [x] `1.2.4` Token service (estimate/reserve/reconcile)
- [x] `1.2.5` Frontend OAuth redirect flow + session management
- [x] `1.2.6` Frontend protected routes + auth context provider
- [x] `1.2.7` Frontend login/logout flow (+ root-site redirect path)
- [x] `1.2.8` Tutor user sync on first login
- [x] `1.2.9` Role-based access control (student/teacher/parent/admin)
- [x] `1.2.10` Redis-backed per-user/per-endpoint rate limiting

---

## 3) Core Tutoring Engine (Phase 1.3)

> **Architecture note**: Experts, chat, sessions run locally. Main site only for auth + credit deduction. See `ARCHITECTURE.md`.

- [x] Provider abstraction layer (`1.3.1`)
- [x] At least one production LLM provider wired end-to-end **locally** (OpenAI; main site only for credit deduct)
- [x] Session create/list/get APIs **local** (`/api/tutor/sessions*`)
- [x] Message persistence **local** (tutor DB)
- [x] SSE streaming chat endpoint (`1.3.7`) **local**
- [x] 7 interaction modes (or MVP subset first)
- [x] Safety/guardrail middleware
- [x] Retry/fallback/timeout strategy (`1.3.8`)
- [x] Token usage metering + credit reconciliation (call main site for deduct only)

Phase 1.3 provider subtask status (to implement locally in tutor):
- [x] `1.3.2` OpenAI — tutor backend direct API calls
- [ ] `1.3.3` Anthropic — tutor backend direct API calls
- [ ] `1.3.4` Gemini — tutor backend direct API calls
- [ ] `1.3.5` xAI Grok — tutor backend direct API calls
- [ ] `1.3.6` Provider/model metadata — local catalog or optional sync from main site

---

## 4) RAG + Teacher Dashboard (Phase 1.4)

- [x] Teacher document upload
- [x] Extraction/chunking/embedding pipeline
- [x] Vector retrieval and rerank
- [x] Citation rendering in responses
- [x] KB management UI (upload/status/delete/preview)
- [x] Teacher class/roster basics

---

## 5) UI & UX Completion (Phase 1.5)

- [x] Basic login/session wiring in frontend
- [x] Basic experts fetch + demo chat wiring
- [x] Full tutor chat UX (streaming markdown/math/code)
- [x] Tutor persona selection UX
- [x] Session history panel
- [x] Age-adaptive layouts (K-2, 3-5, 6-8, 9-12)
- [x] Error/loading/offline handling polish
- [x] End-to-end user journey test coverage

---

## 6) Intelligence Layer (Phase 2 Core)

- [x] Hint progression engine (3 levels)
- [x] Adaptive quiz generation
- [x] Explain-my-answer workflow
- [x] Flashcards + spaced repetition
- [x] Mastery tracking per topic
- [x] Misconception detection
- [x] Student + teacher progress dashboards

---

## 7) Grand Phase 3: Advanced Features

> **Phase Terminology**: Grand Phase = top-level milestone; Functional Phase (FP) = sub-phase within a Grand Phase.
> **Full specs**: See `tech-docs/phase-3/PHASE_3_OVERVIEW.md` for summary and links.

### FP 3.1: Gamification & Streak Systems (`tech-docs/phase-3/PHASE_3.1_GAMIFICATION.md`)
- [ ] `3.1.1` XP system (8 action types, multipliers, history)
- [ ] `3.1.2` Level system (age-themed, 5 levels per band)
- [ ] `3.1.3` Daily streaks (freeze tokens, shield, calendar heatmap)
- [ ] `3.1.4` Badge system (achievement, subject, effort, social badges)
- [ ] `3.1.5` Leaderboard (opt-in, class-scoped, weekly reset, anonymous mode)
- [ ] `3.1.6` XP multipliers & bonus events
- [ ] `3.1.7` Celebrations & animations (age-adaptive, reduced-motion)
- [ ] `3.1.8` Gamification dashboard widget + full dashboard page
- [ ] `3.1.9` Challenge modes (daily, weekly class, 1v1 friend)
- [ ] `3.1.10` Reward marketplace (cosmetics, persona unlocks)
- [ ] `3.1.T` Teacher gamification settings + challenge management

### FP 3.2: Parent Dashboard & Co-Learning (`tech-docs/phase-3/PHASE_3.2_PARENT_DASHBOARD.md`)
- [ ] `3.2.1` Child progress overview (mastery radar, time charts, stats)
- [ ] `3.2.2` Activity feed + AI daily summary
- [ ] `3.2.3` Report generation (weekly/monthly PDF, email delivery)
- [ ] `3.2.4` Content controls (subject restrictions, time limits, quiet hours)
- [ ] `3.2.5` COPPA consent flow (under-13, verifiable consent, data deletion)
- [ ] `3.2.6` Multi-child support (per-child drill-down, aggregate family view)
- [ ] `3.2.7` Co-learning mode (observer/participant, WebSocket, dual-audience AI)
- [ ] `3.2.8` Parent guide sidebar (contextual tips, age-appropriate guidance)
- [ ] `3.2.9` Teacher communication (in-app messaging, alerts, broadcast)
- [ ] `3.2.10` Session history, bookmarks, conversation starters

### FP 3.3: Whiteboard, Code Sandbox, Math Editor (`tech-docs/phase-3/PHASE_3.3_INTERACTIVE_TOOLS.md`)
- [ ] `3.3.1` Digital whiteboard (tldraw, drawing tools, AI interpretation, AI drawing, templates)
- [ ] `3.3.2` Code sandbox (Monaco editor, Docker execution, AI review, debugging, challenges)
- [ ] `3.3.3` Math editor (MathLive, MathJSON, step-by-step solving, graphing)
- [ ] `3.3.4` Annotation tools (highlight, underline, sticky notes)
- [ ] `3.3.5` Unified tool panel (tabs, resize, keyboard shortcuts, responsive)

### FP 3.4: Audio Lessons, Mind Maps, Memory Score (`tech-docs/phase-3/PHASE_3.4_AUDIO_MINDMAPS_MEMORY.md`)
- [ ] `3.4.1` Audio lesson generator (AI scripts, TTS, 4 formats, player, teacher management)
- [ ] `3.4.2` Mind map generation (react-flow, mastery colors, click-to-learn, export)
- [ ] `3.4.3` Memory score (forgetting curve, predictions, proactive reminders, SM-2 enhancement)
- [ ] `3.4.4` Roleplay scenarios (character personas, rubric evaluation, subject-specific)

### FP 3.5: Educational Gaming Engine (`tech-docs/phase-3/PHASE_3.5_GAMING_ENGINE.md`)
- [ ] `3.5.1` Game framework (template registry, session management, adaptive difficulty)
- [ ] `3.5.2` K-2 games (Story Adventure, Matching, Virtual Pet, Treasure Hunt)
- [ ] `3.5.3` 3-5 games (RPG Quest, Building, Mystery Detective, Fraction Pizza)
- [ ] `3.5.4` 6-8 games (Escape Room, Civilization Builder, Coding Maze, Speed Challenge)
- [ ] `3.5.5` 9-12 games (Business Sim, Debate Tournament, Case Study, Stock Market)
- [ ] `3.5.6` Multiplayer (class challenge, paired learning, friend challenge, AI opponent)
- [ ] `3.5.7` Teacher game management + analytics dashboard
- [ ] `3.5.8` AI game recommendations + pathway selector

### FP 3.6: Test Prep Framework (`tech-docs/phase-3/PHASE_3.6_TEST_PREP.md`)
- [ ] `3.6.1` Test prep infrastructure (profiles, enrollment, scoring engine)
- [ ] `3.6.2` Mock test generator (full-length, timed, auto-submit)
- [ ] `3.6.3` Score prediction model (trend, confidence interval)
- [ ] `3.6.4` Gap analysis (per-section weakness, heatmap)
- [ ] `3.6.5` Personalized study plan (AI week-by-week roadmap)
- [ ] `3.6.6` IELTS Speaking (AI examiner, Whisper STT, band scoring)
- [ ] `3.6.7` IELTS Writing (Task 1/2, band scoring, paragraph feedback)
- [ ] `3.6.8` IELTS Reading (passages, 6 question types, timed mode)
- [ ] `3.6.9` IELTS Listening (TTS with accents, 4 sections)
- [ ] `3.6.10` SAT module (adaptive, scaled scoring, college benchmarks)
- [ ] `3.6.11` ACT module (4 sections, composite score)
- [ ] `3.6.12` AP module (10 initial subjects, free response, rubric scoring)

### FP 3.7: Compliance, Accessibility, i18n (`tech-docs/phase-3/PHASE_3.7_COMPLIANCE_A11Y_I18N.md`)
- [ ] `3.7.1` COPPA compliance (parental consent, data minimization, deletion)
- [ ] `3.7.2` FERPA compliance (access control, audit logging, data portability)
- [ ] `3.7.3` GDPR compliance (consent management, right to erasure, export)
- [ ] `3.7.4` Audit system (middleware, audit_log table, admin dashboard)
- [ ] `3.7.5` Data retention policies (configurable, automated cleanup)
- [ ] `3.7.6` Keyboard navigation (tab order, arrow keys, shortcuts, focus)
- [ ] `3.7.7` Screen reader compatibility (semantic HTML, ARIA, live regions)
- [ ] `3.7.8` Visual accessibility (contrast, dyslexia font, high contrast, font size, reduced motion)
- [ ] `3.7.9` Automated accessibility testing (axe-core in CI, Lighthouse)
- [ ] `3.7.10` i18n (next-intl, 6 languages, RTL, AI localization)
- [ ] `3.7.11` ESL/ELL bilingual mode
- [ ] `3.7.12` Wellness guardian (session limits, breaks, quiet hours, cooldown)
- [ ] `3.7.13` Micro-tutoring (quick quiz, daily review, bus-stop audio)

---

## Current Week Focus (Recommended)

- [ ] Complete `1.1.1` Python project initialization (`pyproject.toml` + toolchain standardization)
- [ ] Complete local provider expansion: `1.3.3` Anthropic, `1.3.4` Gemini, `1.3.5` xAI Grok
- [ ] Complete `1.3.6` provider/model metadata catalog (local catalog or optional sync)
- [x] Start Phase 2 with Hint progression engine (3 levels)
- [x] Implement Adaptive quiz generation
- [x] Implement Mastery tracking per topic
- [x] Implement Misconception detection baseline

---

## Update Log

- 2026-03-10: Initial checklist created from `WORKLOG.md` + roadmap mapping.
- 2026-03-10: Updated Phase 1.1 and 1.2 to exact roadmap IDs (`1.1.x`, `1.2.x`) from `AI_TUTOR_MODULE (1).md`.
- 2026-03-10: Started Phase 1 implementation in code (backend modularization, validated settings, request logging middleware).
- 2026-03-10: Completed `1.1.5` (asyncpg pool lifecycle + DB healthcheck status in `/health`).
- 2026-03-10: Completed `1.1.6` by migrating frontend to Next.js App Router + TypeScript strict and validating production build.
- 2026-03-10: Completed `1.1.7` with Tailwind 4 + shadcn setup, OKLCH light/dark tokens, and first reusable UI component.
- 2026-03-10: Completed `1.1.8` by adding Zustand stores (`auth`, `session`, `ui`, `chat`) and integrating them into the main page flow.
- 2026-03-10: Completed `1.1.9` with centralized API client (retry/backoff, normalized API errors, unauthorized hook) and migrated page calls to it.
- 2026-03-10: Completed `1.1.10` by implementing application shell layout (sidebar + topbar + main content container).
- 2026-03-10: Completed `1.1.11` by expanding Docker Compose to include API/frontend/DB/Redis/Celery/sandbox services with health checks and dependencies.
- 2026-03-10: Completed `1.1.12` by adding idempotent `backend/db/init.sql` (core+RAG+class+analytics tables with indexes) and wiring it into Postgres container init.
- 2026-03-10: Completed `1.1.13` by adding idempotent `backend/db/seed.sql` for default personas, baseline standards (CCSS/NGSS), and starter subject/topic concept nodes.
- 2026-03-10: Completed `1.1.14` by adding root `Makefile` and PowerShell automation scripts for dev/test/migrate/seed/lint/format flows.
- 2026-03-10: Completed `1.1.15` by adding GitHub Actions CI workflow with lint/type-check and build/test jobs.
- 2026-03-10: Completed `1.2.1` by introducing `RootSiteClient` (OAuth code exchange, JWKS-cached RS256 JWT verification, user profile/credits/catalog/plan APIs) and wiring auth callback to use the service.
- 2026-03-10: Completed `1.2.3` by adding optional internal `X-Auth-Hex` header injection for backend-to-root-site calls (both `RootSiteClient` and main-site proxy) via `ROOT_SITE_X_AUTH_HEX`.
- 2026-03-10: Completed `1.2.4` by adding `TokenService` for token estimation, credit reservation, and reconciliation flows integrated with `RootSiteClient` credit deduction API.
- 2026-03-10: Completed `1.2.6` by introducing frontend `AuthProvider` + auth context hook and wrapping page content with `ProtectedRoute` gating.
- 2026-03-11: Completed `1.2.8` by adding first-login tutor user sync in OAuth callback (DB upsert into `tutor_users` with role/profile fields) and storing `tutor_user` metadata in session payload.
- 2026-03-11: Completed `1.2.9` by adding RBAC utilities (role resolution + access decisions), enforcing role checks for proxied `/api/admin*`, `/api/teacher*`, and `/api/parent*` paths, and exposing resolved role via `/api/me` for frontend guards.
- 2026-03-11: Completed `1.2.10` by adding Redis-backed user/endpoint rate limiter service, initializing it in app lifespan, and enforcing limits on authenticated session/proxy API routes.
- 2026-03-11: Completed `1.3.1` provider abstraction layer by adding `BaseProvider` (`stream_chat`, `count_tokens`) and a provider registry scaffold for model/provider resolution.
- 2026-03-11: Completed `1.3.2` OpenAI provider by adding streaming Chat Completions integration (`gpt-4o`, `gpt-4o-mini`) with direct `httpx` SSE parsing, env-configurable OpenAI settings, and provider auto-registration.
- 2026-03-11: Cross-repo reminder added to handoff/checklist: when shared platform API changes are required, update both `D:\USA\clever-ai-tutor` and `C:\AISITENEW`.
- 2026-03-11: Completed `1.3.3` Anthropic provider by adding streaming Messages API integration (`claude-4-sonnet`, `claude-4-haiku`), env-configurable Anthropic settings, and provider auto-registration.
- 2026-03-11: Completed `1.3.4` Gemini provider by adding streaming GenerateContent SSE integration (`gemini-2.5-pro`, `gemini-2.5-flash`), env-configurable Gemini settings, and provider auto-registration.
- 2026-03-11: Architecture decision: tutor app runs in `main_site_proxy_only` mode (no direct provider keys/calls). All experts/functions/LLM execution are invoked through main-site APIs (`C:\AISITENEW`) via tutor backend proxy.
- 2026-03-11: Main-site tutor API contract added in `C:\AISITENEW` (`/api/experts`, `/api/expert-chat`, `/api/tutor/sessions*`) and aligned as source of truth for tutor execution/data.
- 2026-03-11: Completed `1.3.7` by adding main-site SSE endpoint (`/api/tutor/sessions/{session}/chat`) and implementing tutor proxy streaming pass-through for `text/event-stream` requests.
- 2026-03-11: Completed `1.3.8` by adding main-site retry/fallback/timeout execution strategy in tutor gateway (`runModelCompletion`) with model candidate fallback, transient retry policy, timeout enforcement, and execution-attempt metadata in API responses/stream events.
- 2026-03-11: Completed safety/guardrails by adding `TutorGuardrailMiddleware` on main-site tutor chat routes (input filtering) plus output guardrail sanitization in `TutorGatewayController`.
- 2026-03-11: Completed token usage metering + credit reconciliation by adding estimate/reserve/actual token billing metrics in main-site tutor gateway, persisting billing metadata per message, and charging reconciled actual tokens via `deductUserTokensAndCredits`.
- 2026-03-11: Completed interaction modes by adding 7 mode definitions, mode catalog API (`/api/tutor/modes`), session mode switching (`/api/tutor/sessions/{id}/mode`), and mode-aware prompt layering in both standard and SSE tutor chat paths.
- 2026-03-11: Completed `1.3.5` xAI Grok provider routing in main-site tutor gateway by making retry/fallback provider-aware (`openai` + `grok`), resolving active model/provider candidates from `AISettings`, and executing Grok via `services.xai` API credentials while preserving tutor proxy consumption flow.
- 2026-03-11: Completed `1.3.6` provider/model catalog sync by adding main-site `GET /api/catalog` endpoint returning model metadata (provider, cost, tier, context_window, supports_web_search, modules) from `AISettings` with ETag caching; tutor app consumes via existing `RootSiteClient.get_model_catalog()`.
- 2026-03-12: **Architecture clarification**: Main site only for auth, billing, credit deduction. Experts, chat, sessions run locally in tutor. See `ARCHITECTURE.md`. Phase 1.3 checklist items updated to reflect local implementation; migration from proxy pattern required.
- 2026-03-12: Completed local sessions API (`POST/GET /api/tutor/sessions`, `GET /api/tutor/sessions/{id}`) and message persistence in chat when `session_id` provided.
- 2026-03-12: Completed SSE streaming chat endpoint `POST /api/expert-chat/stream` — streams `stream_start`, `token`, `stream_end` (or `error`) events.
- 2026-03-12: Completed 7 interaction modes — `mode_prompts.py`, `GET /api/tutor/modes`, `PATCH /api/tutor/sessions/{id}/mode`, mode-aware prompt layering in chat.

- 2026-03-12: Completed local safety/guardrail middleware by adding request filtering on /api/expert-chat* (prompt-injection/unsafe-content checks + payload cap) and assistant-output sanitization in chat + streaming handlers.

- 2026-03-12: Completed local retry/fallback/timeout strategy (1.3.8) for /api/expert-chat and /api/expert-chat/stream with model fallback candidates, transient retries with backoff, per-attempt timeout enforcement, and execution-attempt metadata in responses/events.

- 2026-03-12: Completed Phase 1.4 teacher KB upload/list/delete/preview APIs (/api/teacher/kb*) with teacher/admin RBAC, local file persistence, and KB/document metadata storage in knowledge_bases + kb_documents tables.

- 2026-03-12: Completed Phase 1.4 extraction/chunking/embedding pipeline with local document text extraction (txt/md native, optional pdf/docx/pptx via installed libs), configurable chunking, OpenAI embeddings, and kb_chunks persistence via new process endpoints (/api/teacher/kb/{kb_id}/documents/{document_id}/process, /api/teacher/kb/{kb_id}/documents/process-queued).

- 2026-03-12: Completed Phase 1.4 vector retrieval + rerank by adding /api/teacher/kb/{kb_id}/retrieve (query embedding, pgvector nearest-neighbor search on kb_chunks.embedding, lexical overlap rerank, citation labels per chunk).

- 2026-03-12: Completed Phase 1.4 citation rendering in chat responses by injecting retrieved KB context into prompt when kb_id is provided and returning citation metadata in both /api/expert-chat JSON and /api/expert-chat/stream SSE lifecycle events.

- 2026-03-12: Completed Phase 1.4 KB management UI in frontend (frontend/app/page.tsx) with teacher/admin gating and end-to-end wiring for KB create/list, document upload, queued processing trigger, status list, preview, and delete using local /api/teacher/kb* endpoints.

- 2026-03-12: Completed Phase 1.4 teacher class/roster basics with local backend APIs (/api/teacher/classes*) for class create/list/detail, enroll/remove student, and frontend wiring in frontend/app/page.tsx for teacher/admin class + roster management.

- 2026-03-12: Phase 1.5 chat workspace upgrade: added tutor persona selection, mode selection, session creation/loading, session history panel, and SSE streaming chat flow in frontend/app/page.tsx. Kept Full tutor chat UX (streaming markdown/math/code) open for richer markdown/math/code rendering polish.

- 2026-03-12: Completed Phase 1.5 full tutor chat UX rendering by adding streaming chat workspace message rendering for markdown-like formatting, fenced code blocks, and math-friendly inline/block expressions via new frontend/components/chat/message-renderer.tsx and related UI styles.

- 2026-03-12: Completed Phase 1.5 age-adaptive layouts by adding grade-band detection (K-2/3-5/6-8/9-12) from session user data and applying band-specific UX in frontend/app/page.tsx + frontend/app/globals.css (labels, prompt suggestions, copy, and visual scaling).

- 2026-03-12: Completed Phase 1.5 error/loading/offline polish in tutor UI by adding a System Status surface (online/offline state, active background loading indicators, current issue summary, and refresh/reload controls) plus age-band prompt quick-chips and adaptive copy improvements in frontend/app/page.tsx + frontend/app/globals.css.
- 2026-03-12: Completed Phase 1.5 E2E user journey coverage by adding Playwright setup (frontend/playwright.config.ts), auth-gate and tutor-streaming smoke specs (frontend/e2e/*.spec.ts), and npm scripts (e2e, e2e:list) in frontend/package.json with dependency install validation via `npm.cmd run e2e:list`.
- 2026-03-12: Refreshed checklist estimates and Current Week Focus to match implemented Phase 1.4/1.5 work and remaining open items (`1.1.1`, `1.3.3`-`1.3.6`, Phase 2 kickoff).
- 2026-03-12: Started Phase 2 by implementing backend hint progression baseline (`/api/tutor/hints/start`, `/api/tutor/hints/{id}/next`, `/api/tutor/hints/{id}`) with enforced 3-level sequence and persistence in `hint_progressions`.
- 2026-03-12: Wired frontend Hint mode to Phase 2 endpoints in chat workspace (`/api/tutor/hints/start` + `/api/tutor/hints/{id}/next`) with level-aware UI controls and progression state handling.
- 2026-03-12: Implemented adaptive quiz generation baseline with backend APIs (`POST /api/tutor/quiz/generate`, `POST /api/tutor/quiz/{id}/submit`, `GET /api/tutor/quiz/history`), persistence in `adaptive_quiz_attempts`, and frontend `Quiz Me` mode wiring for question generation, option selection, and adaptive feedback.
- 2026-03-12: Implemented explain-my-answer workflow with backend endpoint (`POST /api/tutor/quiz/{id}/explain-my-answer`) and frontend `Quiz Me` integration for student reasoning submission and personalized diagnostic feedback; logs wrong answers to `mistake_journal`.
- 2026-03-12: Implemented flashcards + spaced repetition with backend APIs (`/api/tutor/flashcards/decks*`, `/api/tutor/flashcards/generate`, `/api/tutor/flashcards/review`, `/api/tutor/flashcards/{id}/review`) using SM-2 scheduling and frontend flashcard deck/generation/review UI.
- 2026-03-12: Implemented mastery tracking per topic with backend APIs (`GET /api/tutor/mastery`, `POST /api/tutor/mastery/recompute`), auto-updates from quiz submission, and frontend mastery panel for refresh/recompute and level visibility.
- 2026-03-12: Implemented misconception detection baseline with automatic logging from incorrect quiz submissions, misconception APIs (`GET /api/tutor/misconceptions`, `POST /api/tutor/misconceptions/{id}/resolve`), and frontend misconception review/resolve panel.
- 2026-03-12: Implemented student + teacher progress dashboards with backend APIs (`GET /api/tutor/progress/student`, `GET /api/tutor/progress/teacher?class_id=...`) and frontend dashboard panels for student metrics and teacher class rollups.
- 2026-03-12: Phase 2 core marked complete (hint progression, adaptive quiz, explain-my-answer, flashcards/spaced repetition, mastery tracking, misconception detection, progress dashboards).

> Update this file daily by checking completed tasks and adjusting percentage estimates.

