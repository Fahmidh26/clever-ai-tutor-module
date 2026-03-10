# AI Tutor Progress Checklist

> Tracking against `AI_TUTOR_MODULE (1).md` roadmap  
> Baseline estimate uses current `WORKLOG.md` state

---

## Overall Progress Snapshot (Estimated)

- Foundation setup: **72%**
- Main-site auth/API integration: **75%**
- Core tutoring engine: **20%**
- RAG + teacher knowledge base: **5%**
- UX polish + adaptive UI: **20%**
- Intelligence (mastery/quiz/hints): **0%**
- Gamification/interactive tools/test prep: **0%**

**Estimated overall completion (MVP path): 22%**

---

## 1) Foundation & DevOps (Phase 1.1)

- [ ] `1.1.1` Initialize Python project (`pyproject.toml`, Poetry/uv, Python 3.13)
- [x] `1.1.2` FastAPI app skeleton with router structure
- [x] `1.1.3` Pydantic v2 settings management (`config.py` env validation)
- [x] `1.1.4` Structured logging (structlog + OpenTelemetry baseline)
- [ ] `1.1.5` asyncpg connection pool setup with health checks
- [ ] `1.1.6` Next.js 16 project with App Router + TypeScript strict mode
- [ ] `1.1.7` Tailwind 4 + shadcn/ui 4 setup and theming
- [ ] `1.1.8` Zustand 5 store skeleton (auth/session/ui/chat)
- [ ] `1.1.9` API client layer with interceptors/retry/error handling
- [ ] `1.1.10` Layout shell (sidebar/header/main)
- [x] `1.1.11` Docker Compose with core services
- [ ] `1.1.12` PostgreSQL init.sql with full schema + indexes
- [ ] `1.1.13` Seed data SQL (personas, subjects, topics, standards)
- [ ] `1.1.14` Makefile/scripts (dev, test, migrate, seed, lint, format)
- [ ] `1.1.15` CI pipeline skeleton (lint, type-check, test)

---

## 2) Authentication + Root-Site Integration (Phase 1.2)

- [ ] `1.2.1` RootSiteClient service (OAuth/JWT/user/credits/catalog/plan checks)
- [x] `1.2.2` Auth middleware (JWT/session extraction and user context)
- [ ] `1.2.3` Internal `X-Auth-Hex` header for service-to-service calls
- [ ] `1.2.4` Token service (estimate/reserve/reconcile)
- [x] `1.2.5` Frontend OAuth redirect flow + session management
- [ ] `1.2.6` Frontend protected routes + auth context provider
- [x] `1.2.7` Frontend login/logout flow (+ root-site redirect path)
- [ ] `1.2.8` Tutor user sync on first login
- [ ] `1.2.9` Role-based access control (student/teacher/parent/admin)
- [ ] `1.2.10` Redis-backed per-user/per-endpoint rate limiting

---

## 3) Core Tutoring Engine (Phase 1.3)

- [ ] Provider abstraction layer
- [ ] At least one production LLM provider wired end-to-end
- [ ] Session create/list/get APIs
- [ ] Message persistence
- [ ] SSE streaming chat endpoint
- [ ] 7 interaction modes (or MVP subset first)
- [ ] Safety/guardrail middleware
- [ ] Retry/fallback/timeout strategy
- [ ] Token usage metering + credit reconciliation

---

## 4) RAG + Teacher Dashboard (Phase 1.4)

- [ ] Teacher document upload
- [ ] Extraction/chunking/embedding pipeline
- [ ] Vector retrieval and rerank
- [ ] Citation rendering in responses
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

- [ ] Finalize Phase 1.1 hardening tasks
- [ ] Complete remaining Phase 1.2 security/testing tasks
- [ ] Start Phase 1.3 session + streaming backend

---

## Update Log

- 2026-03-10: Initial checklist created from `WORKLOG.md` + roadmap mapping.
- 2026-03-10: Updated Phase 1.1 and 1.2 to exact roadmap IDs (`1.1.x`, `1.2.x`) from `AI_TUTOR_MODULE (1).md`.
- 2026-03-10: Started Phase 1 implementation in code (backend modularization, validated settings, request logging middleware).

> Update this file daily by checking completed tasks and adjusting percentage estimates.
