# AI Tutor Progress Checklist

> Repos in scope:
> - Tutor app: `D:\USA\clever-ai-tutor`
> - Main site (auth/billing/credits only): `C:\AISITENEW`

> **Architecture**: Main site = auth, billing, credit deduction. Experts, chat, sessions = local tutor APIs. See `ARCHITECTURE.md`.
> Tracking against `AI_TUTOR_MODULE (1).md` roadmap  
> Baseline estimate uses current `WORKLOG.md` state

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

- Foundation setup: **100%**
- Main-site auth/API integration: **100%**
- Core tutoring engine (local per ARCHITECTURE): **~75%** — experts + chat + sessions + streaming + 7 modes
- RAG + teacher knowledge base: **5%**
- UX polish + adaptive UI: **20%**
- Intelligence (mastery/quiz/hints): **0%**
- Gamification/interactive tools/test prep: **0%**

**Estimated overall completion (MVP path): ~22%**

> **Current working state**: Experts, chat, sessions run locally. 7 interaction modes via `mode` param. `GET /api/tutor/modes`, `PATCH /api/tutor/sessions/{id}/mode`.

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
- [ ] KB management UI (upload/status/delete/preview)
- [ ] Teacher class/roster basics

---

## 5) UI & UX Completion (Phase 1.5)

- [x] Basic login/session wiring in frontend
- [x] Basic experts fetch + demo chat wiring
- [ ] Full tutor chat UX (streaming markdown/math/code)
- [ ] Tutor persona selection UX
- [ ] Session history panel
- [ ] Age-adaptive layouts (K-2, 3-5, 6-8, 9-12)
- [ ] Error/loading/offline handling polish
- [ ] End-to-end user journey test coverage

---

## 6) Intelligence Layer (Phase 2 Core)

- [ ] Hint progression engine (3 levels)
- [ ] Adaptive quiz generation
- [ ] Explain-my-answer workflow
- [ ] Flashcards + spaced repetition
- [ ] Mastery tracking per topic
- [ ] Misconception detection
- [ ] Student + teacher progress dashboards

---

## 7) Advanced Phases (3+)

- [ ] Gamification and streak systems
- [ ] Parent dashboard and co-learning
- [ ] Whiteboard, code sandbox, math editor
- [ ] Audio lessons, mind maps, memory score
- [ ] Educational gaming engine
- [ ] Test prep framework (IELTS/SAT/ACT/AP)
- [ ] Compliance, accessibility, i18n

---

## Current Week Focus (Recommended)

- [x] Phase 1.1 complete
- [x] Phase 1.2 complete
- [x] Local experts + chat APIs implemented
- [x] Implement local `/api/tutor/sessions*` (create, list, get, message persistence)
- [x] SSE streaming chat (`POST /api/expert-chat/stream`)
- [x] 7 interaction modes (Teach Me, Quiz Me, Hint, Apply It, Show Thinking, Writing Workshop, Debate/Roleplay)

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

> Update this file daily by checking completed tasks and adjusting percentage estimates.
