# AGENTS.md — Clever AI Tutor Master Rules & Guidelines

> **Purpose**: Single source of truth for all AI agents (Claude Code, Cursor, Copilot) and developers working on this codebase.
> **Last Updated**: 2026-03-18

---

## 1. Project Identity

| Field | Value |
|-------|-------|
| **Name** | Clever AI Tutor |
| **Domain** | tutor.clevercreator.ai |
| **Repo** | `D:\USA\clever-ai-tutor` |
| **Main Site (auth/billing only)** | `C:\AISITENEW` |
| **Branch Strategy** | `main` → `phase-2` → `phase-3` (feature branches off current phase) |

---

## 2. Architecture Rules (CRITICAL — Read First)

| Responsibility | Where It Runs | Notes |
|----------------|---------------|-------|
| Authentication | Main site | OAuth login, token exchange, user profile |
| Billing | Main site | Subscriptions, Stripe |
| Credit / token deduction | Main site | Reserve, deduct, reconcile |
| Experts | Tutor site (LOCAL) | Expert catalog, personas |
| Chat | Tutor site (LOCAL) | AI responses, streaming |
| Sessions | Tutor site (LOCAL) | Session CRUD, message persistence |
| RAG / Knowledge base | Tutor site (LOCAL) | Document upload, retrieval |
| All education logic | Tutor site (LOCAL) | Hints, mastery, quiz, flashcards, games, etc. |

**Rules**:
- NEVER proxy experts, chat, or sessions to the main site
- Main site is called ONLY for: auth, billing, credit deduction
- Read `tech-docs/phase-1/ARCHITECTURE.md` before any architectural change
- All education-specific logic lives in the tutor backend

---

## 3. Tech Stack (Pinned — Do Not Upgrade Without Explicit Approval)

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 16.1.6 | App Router framework |
| React | 19.2.0 | UI library |
| TypeScript | 5.9.3 | Type safety (strict mode) |
| Tailwind CSS | 4.2.1 | Utility-first styling |
| shadcn/ui | new-york style | Component library |
| Zustand | 5.0.11 | State management |
| Lucide React | 0.577.0 | Icons |
| class-variance-authority | 0.7.1 | Component variants |
| Playwright | 1.56.0 | E2E testing |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ | Runtime |
| FastAPI | latest | API framework |
| Uvicorn | standard | ASGI server |
| asyncpg | latest | Async PostgreSQL driver |
| PostgreSQL | 17 | Primary database |
| pgvector | 0.8 | Vector embeddings |
| Redis | 8 | Caching, rate limiting |
| Celery | latest | Async task queue (Redis broker) |
| structlog | latest | Structured logging |
| Pydantic | v2 | Settings & validation |
| httpx | latest | Async HTTP client |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker Compose | Local orchestration |
| GitHub Actions | CI/CD pipeline |
| S3-compatible storage | File/audio/image storage (future) |

---

## 4. Documentation Map

All documentation lives under `/tech-docs/` organized by phase:

```
tech-docs/
├── phase-1/                           (Foundation — completed)
│   ├── AI_TUTOR_MODULE.md             Master specification (181 KB)
│   ├── AI_TUTOR_PLAN.md               Original implementation roadmap
│   ├── AI_TUTOR_NEXT_STEPS_GUIDE.md   Phase 1 guidance
│   ├── AI_TUTOR_TESTING_GUIDE.md      Testing reference
│   ├── ARCHITECTURE.md                Core architecture (READ FIRST)
│   └── WORKLOG.md                     Development history
│
├── phase-2/                           (Intelligence Layer — completed)
│   ├── AI_TUTOR_PROGRESS_CHECKLIST.md Master progress tracker
│   ├── SESSION_HANDOFF.md             Session resume template
│   └── USER_FLOWS_DIAGRAMS.md         UX flow reference
│
├── phase-3/                           (Advanced Features — current)
│   ├── PHASE_3_OVERVIEW.md            Summary of all 7 functional phases
│   ├── PHASE_3.1_GAMIFICATION.md      Gamification & streak systems
│   ├── PHASE_3.2_PARENT_DASHBOARD.md  Parent dashboard & co-learning
│   ├── PHASE_3.3_INTERACTIVE_TOOLS.md Whiteboard, code sandbox, math editor
│   ├── PHASE_3.4_AUDIO_MINDMAPS_MEMORY.md  Audio lessons, mind maps, memory score
│   ├── PHASE_3.5_GAMING_ENGINE.md     Educational gaming engine
│   ├── PHASE_3.6_TEST_PREP.md         Test prep (IELTS/SAT/ACT/AP)
│   └── PHASE_3.7_COMPLIANCE_A11Y_I18N.md  Compliance, accessibility, i18n
│
└── diagrams and workflows/            (Visual references — JPEGs)
```

---

## 5. Phase Terminology

| Term | Meaning | Example |
|------|---------|---------|
| **Grand Phase** | Top-level phase (1, 2, 3) | Grand Phase 3: Advanced Features |
| **Functional Phase** | Sub-phase within a Grand Phase | Functional Phase 3.1: Gamification |
| **Sprint** | Implementation unit within a Functional Phase | Sprint 3.1.1: XP System |

---

## 6. Code Conventions

### 6.1 Backend (Python / FastAPI)

- **Database**: asyncpg + raw SQL — NO ORM (SQLAlchemy, Tortoise, etc.)
- **Validation**: Pydantic v2 for all request/response models
- **Logging**: structlog (structured JSON logging)
- **File Organization**:
  - Routers: `backend/app/routers/{domain}.py` (one router per domain)
  - Services: `backend/app/services/{domain}.py` (business logic)
  - Config: `backend/app/config.py` (Pydantic settings)
- **Auth**: All endpoints require auth middleware; RBAC enforced at router level
- **Roles**: student, teacher, parent, admin
- **Async**: All DB and HTTP operations must be async
- **Error Handling**: FastAPI HTTPException with structured error responses

### 6.2 Frontend (Next.js / React / TypeScript)

- **Router**: App Router (NOT Pages Router)
- **TypeScript**: Strict mode — no `any` types
- **Styling**: Tailwind 4 utility classes ONLY
  - NO hardcoded CSS (`style={{}}`, inline styles)
  - NO CSS modules or separate CSS files for components
  - Use `cn()` helper (clsx + tailwind-merge) for conditional classes
  - OKLCH color system defined in `globals.css`
  - Dark mode via Tailwind `dark:` variant
- **Components**: shadcn/ui (new-york style) as base — extend, don't replace
- **State**: Zustand (one store per domain)
  - `auth-store.ts`, `chat-store.ts`, `session-store.ts`, `ui-store.ts`
  - New stores: `gamification-store.ts`, `parent-store.ts`, etc.
- **API Calls**: Always through `lib/api-client.ts` (retry, error handling, auth)
- **File Organization**:
  - Pages: `frontend/app/{route}/page.tsx`
  - Components: `frontend/components/{domain}/`
  - Stores: `frontend/stores/{domain}-store.ts`
  - Utilities: `frontend/lib/`
- **Animations**: framer-motion or CSS transitions (MUST respect `prefers-reduced-motion`)

### 6.3 Database

- PostgreSQL 17 + pgvector 0.8
- **Schema baseline**: `backend/db/init.sql`
- **Migrations**: `backend/db/migrations/YYYY-MM-DD_description.sql`
- **Seed data**: `backend/db/seed.sql`
- All new tables MUST have:
  - `id SERIAL PRIMARY KEY`
  - `created_at TIMESTAMPTZ DEFAULT NOW()`
  - Indexes on all foreign keys
  - JSONB for flexible/nested data
  - TIMESTAMPTZ for ALL timestamp columns (never TIMESTAMP)

### 6.4 Docker

- All services defined in `docker-compose.yml`
- Health checks required for every service
- Services: tutor-db, tutor-redis, tutor-api, tutor-celery, tutor-sandbox, tutor-frontend
- Ports: Frontend 5174, API 8003, DB 5433, Redis 6379, Sandbox 2375

---

## 7. UI/UX Design Rules

### 7.1 Responsive Breakpoints
| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 640px | Single column, stacked cards, bottom navigation |
| Tablet | 640–1024px | 2-column where appropriate, collapsible sidebars |
| Desktop | > 1024px | Full multi-column layouts, persistent sidebars |

### 7.2 Age-Adaptive Design
| Grade Band | Ages | UI Characteristics |
|------------|------|-------------------|
| K-2 | 5-7 | Large buttons, bright colors, simple language, emoji/icons, minimal text |
| 3-5 | 8-10 | Moderate complexity, guided interactions, encouraging tone |
| 6-8 | 11-13 | Standard UI, more text, self-directed navigation |
| 9-12 | 14-18 | Full-featured, professional, advanced options visible |

### 7.3 Design Principles
- **Modern & Minimal**: Clean layouts with progressive disclosure
- **User-Friendly**: Intuitive navigation, clear CTAs, consistent patterns
- **Feature-Rich but Clean**: Many features accessible without overwhelming the UI
- **Consistent Theme**: shadcn/ui + Tailwind everywhere — no one-off styling
- **Accessible**: WCAG 2.1 AA compliance target (see Phase 3.7)
- **Dark Mode**: All components must support light/dark via Tailwind `dark:` variant

---

## 8. Testing Strategy

### Backend
- **Framework**: pytest with async fixtures
- **Coverage**: All API endpoints, service methods, edge cases
- **Integration**: Tests hit real database (no mocks for DB)

### Frontend
- **E2E**: Playwright (`frontend/e2e/*.spec.ts`)
- **Unit**: Vitest (when added)
- **Config**: `frontend/playwright.config.ts`
- **Scripts**: `npm run e2e`, `npm run e2e:list`

---

## 9. Security & Compliance Rules

### Authentication & Authorization
- OAuth 2.0 with main site for login
- JWT tokens for session management
- RBAC enforced at router level (student/teacher/parent/admin)
- Redis-backed per-user/per-endpoint rate limiting

### Data Protection
- **COPPA**: Parental consent required for users under 13
- **FERPA**: Educational records are protected — authorized access only
- **GDPR**: Right to erasure, data portability, consent management
- **No PII in logs** or error reports — ever
- **Audit logging**: All data modifications logged with actor + timestamp
- **Encryption**: At rest (AES-256) and in transit (TLS 1.3)

### Content Safety
- `TutorGuardrailMiddleware` for input filtering
- Output sanitization in chat handlers
- Age-appropriate content enforcement

---

## 10. Workflow Rules

### Development Process
1. One task at a time, in checklist order
2. Backend first → Frontend wiring → Tests
3. After each task: implement → validate (build/lint) → update checklist + worklog
4. Cross-repo changes: update BOTH `D:\USA\clever-ai-tutor` AND `C:\AISITENEW`

### Branch Strategy
- `main` — stable release
- `phase-2` — current working branch (Phase 2 complete)
- `phase-3` — create for Phase 3 work
- Feature branches: `phase-3/{functional-phase}/{feature}` (e.g., `phase-3/gamification/xp-system`)

### Documentation Updates
- Update `tech-docs/phase-2/AI_TUTOR_PROGRESS_CHECKLIST.md` after each completed task
- Update `tech-docs/phase-1/WORKLOG.md` with implementation notes
- Update `tech-docs/phase-2/SESSION_HANDOFF.md` for handoff readiness

---

## 11. Current Status

| Grand Phase | Status | Completion |
|-------------|--------|------------|
| Phase 1: Foundation & DevOps | Complete | ~93% (pending 1.1.1) |
| Phase 1: Auth Integration | Complete | 100% |
| Phase 1: Core Tutoring Engine | Complete | ~85% (multi-provider pending) |
| Phase 1: RAG + Teacher Dashboard | Complete | 100% |
| Phase 1: UI & UX | Complete | 100% |
| Phase 2: Intelligence Layer | Complete | 100% |
| Phase 3: Advanced Features | Not Started | 0% |

**Estimated overall MVP completion: ~72%**

### Phase 3 Functional Phases (upcoming):
1. Gamification & Streak Systems
2. Parent Dashboard & Co-Learning
3. Whiteboard, Code Sandbox, Math Editor
4. Audio Lessons, Mind Maps, Memory Score
5. Educational Gaming Engine
6. Test Prep Framework (IELTS/SAT/ACT/AP)
7. Compliance, Accessibility, i18n

---

## 12. Existing Database Tables (Reference)

### Core Tables
`tutor_users`, `tutor_personas`, `tutor_sessions`, `tutor_messages`

### Education Tables
`classes`, `class_enrollments`, `parent_student_links`, `content_restrictions`

### Knowledge Base Tables
`knowledge_bases`, `kb_documents`, `kb_chunks`, `kb_class_assignments`

### Intelligence Tables
`hint_progressions`, `adaptive_quiz_attempts`, `mistake_journal`, `flashcard_decks`, `flashcard_cards`, `flashcard_reviews`, `topic_mastery`, `misconceptions`

### Analytics Tables
`student_xp`, `xp_transactions`, `badges`, `student_badges`, `concept_nodes`, `concept_edges`

### Progress Tables
`student_progress_snapshots`

> See `backend/db/init.sql` for full schema definitions.
