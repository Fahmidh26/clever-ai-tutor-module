# AI Tutor Implementation Guide

## Purpose

Build the AI Tutor module in `D:\USA\clever-ai-tutor` following `AI_TUTOR_MODULE (1).md` in a practical, execution-first order.

## Architecture (See `ARCHITECTURE.md`)

- **Main site** (port `8000`): Auth, billing, credit deduction only.
- **Tutor site** (local): Experts, chat, sessions, AI execution. All tutor functions run locally.

---

## Current Baseline (Already Done)

Based on `WORKLOG.md`, the following foundation pieces are already in place:

- Project scaffolding (`frontend/` + `backend/`)
- Auth pattern reused from working project
- Main-site API proxy endpoint in backend
- Environment files for frontend/backend
- Docker startup path
- Basic frontend wiring for login/session/experts/demo chat

This means you should **continue from Phase 1.3+ behaviors**, while filling Phase 1.1/1.2 gaps that are still missing (quality, security, DB rigor, observability, tests).

---

## What You Need Before Starting

## 1) Running Services
- Main site up at `http://localhost:8000`
- AI Tutor backend up (current plan: `8003`)
- AI Tutor frontend up (current plan: `5174`)
- Optional: Redis + Postgres containers for production-like flow

## 2) Required Secrets / Config
- OAuth client id/secret for tutor app
- Root API base URL + internal URL
- JWT verification settings
- LLM provider API keys (OpenAI/Anthropic/Gemini/Grok as needed)
- Database + Redis connection strings

## 3) Product Decisions to Lock Early
- Initial user roles enabled on day 1 (`student`, `teacher`; optionally `parent`, `admin`)
- First release interaction modes (recommend all 7 in backend, expose 3-4 in UI initially)
- Which first RAG sources are allowed (`pdf`, `docx`, `pptx`, `url`)

---

## Recommended Build Order (What After What)

## Stage A - Harden Foundation (finish remaining Phase 1.1/1.2)
Goal: Make current scaffold production-safe before adding more features.

1. Add centralized config validation (fail fast on missing env).
2. Add structured logging + request ids.
3. Add DB migration system and baseline schema for users/sessions/messages.
4. Add Redis-backed rate limits on auth/chat routes.
5. Add integration tests for OAuth callback + `/api/main-site/{path}` proxy.
6. Add role guard middleware and route-level authorization.

**Output:** Stable auth + proxy + storage foundation with tests.

## Stage B - Core Tutor Engine (Phase 1.3)
Goal: Deliver real tutoring sessions, not just demo chat.

1. Create provider abstraction and minimum 1 provider implementation.
2. Implement session APIs: create session, append message, stream AI response.
3. Implement mode-aware prompt builder (start with `Teach Me`, `Quiz Me`, `Hint`).
4. Persist conversation history and token usage per turn.
5. Add fallback handling and timeout policy.
6. Enforce content safety and anti-cheating rules server-side.

**Output:** End-to-end tutoring flow with persisted sessions and streaming responses.

## Stage C - Teacher KB + RAG (Phase 1.4)
Goal: Let teacher content improve student answers.

1. Build document upload flow (teacher only).
2. Add extraction/chunking/embedding pipeline.
3. Store vectors in pgvector and add retrieval endpoint.
4. Inject top chunks into prompt with citations in response.
5. Add teacher KB UI: upload, status, delete, preview.

**Output:** Tutor responses grounded in class-specific material.

## Stage D - UX Completion (Phase 1.5)
Goal: Make core product usable for real classrooms.

1. Chat UI improvements (streaming, markdown/math/code, quick actions).
2. Tutor persona cards + subject selection.
3. Age-band UI variants (start with 2 bands, then expand to 4).
4. Error/loading/empty states + mobile responsiveness.
5. Add E2E tests for login -> select tutor -> chat -> cite KB.

**Output:** MVP-ready classroom flow.

## Stage E - Intelligence Layer (Phase 2 priority subset)
Goal: Add measurable learning impact.

1. Mastery model per topic (5 levels).
2. Hint progression engine (3 levels, cannot skip).
3. Quiz generation + explain-my-answer.
4. Flashcards with review scheduling (SM-2 or equivalent).
5. Progress dashboard for student + teacher.

**Output:** Adaptive tutor with learning loop, not only conversation.

---

## Main-Site Integration Pattern (Auth + Credits Only)

1. Frontend never calls main site (`:8000`) directly.
2. Frontend calls Tutor backend for all operations.
3. Auth: Tutor backend uses OAuth with main site for login/callback; session stored locally.
4. Credits: When chat consumes tokens, tutor backend calls main site to deduct credits.
5. Experts, chat, sessions: Implemented locally in tutor backend — do NOT proxy to main site.

See `ARCHITECTURE.md` for the canonical rule.

---

## Minimum API Map to Implement First

## Must Have for MVP
- Auth/session: login, callback, current user, logout
- Tutor sessions: create/list/get/append message/stream response
- Tutors/personas: list available tutors
- RAG: upload doc, index status, retrieve chunks
- Progress: mastery summary per student

## Good Next
- Teacher class management
- Assignments + quiz attempts
- Parent progress view

---

## Suggested 6-Week Tactical Plan (From Current State)

- Week 1: Stage A hardening (config, logging, auth/proxy tests, RBAC)
- Week 2: Stage B session model + streaming + persistence
- Week 3: Stage B prompt modes + safety + fallback
- Week 4: Stage C upload/chunk/embed/retrieve pipeline
- Week 5: Stage D UX polish + persona/age-band pass
- Week 6: Stage E hints/quizzes/mastery baseline

---

## Definition of Done for Initial Release

- User logs in via main site and lands in tutor dashboard
- Student can run a full streamed tutoring session
- At least 3 interaction modes are functional end-to-end
- Teacher uploads material and sees citations in student responses
- Session and usage data are persisted and queryable
- Basic progress metrics visible to student and teacher
- Critical path covered by integration/E2E tests

---

## Risks and Mitigation

- **Auth drift from main site:** add contract tests against live `:8000` endpoints.
- **Proxy instability:** enforce timeout/retry circuit and explicit error taxonomy.
- **LLM cost spikes:** track token usage per session and set per-plan limits.
- **RAG quality variance:** tune chunk size + rerank and show citations always.
- **Scope creep:** lock MVP to Stages A-D + minimal Stage E.

---

## Daily Execution Rhythm

1. Pick 1 sprint block and split into 3-6 concrete tasks.
2. Implement backend first, then frontend wiring, then tests.
3. Demo working flow locally using main site on `8000`.
4. Update `AI_TUTOR_PROGRESS_CHECKLIST.md` at end of day.
5. Keep a short changelog entry in `WORKLOG.md`.
