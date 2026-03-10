# Clever AI Tutor - Work Log

## What I created

- New project at `D:/USA/clever-ai-tutor`
- React frontend scaffolded with Vite in `frontend/`
- FastAPI backend scaffolded in `backend/`
- OAuth/session authentication pattern reused from `fastapi-ai-tutor`
- Backend proxy endpoint added so this app can call APIs from main site at port `8000`

## Authentication reused

- OAuth login endpoint: `GET /oauth/login`
- OAuth callback endpoint: `GET /oauth/callback`
- Session endpoint: `GET /api/me`
- Logout endpoint: `POST /api/logout`

These are implemented to match the working auth approach from the current project.

## Main-site API proxy

- Endpoint: `/api/main-site/{path:path}`
- Methods: `GET, POST, PUT, PATCH, DELETE`
- Uses the logged-in session `access_token`
- Forwards requests to `AISITE_OAUTH_INTERNAL_URL` (default: `http://localhost:8000/`)

Example:

- `GET /api/main-site/api/experts?domain=expert-chat`
- `POST /api/main-site/api/expert-chat`

## Environment setup done

- Added backend env files:
  - `backend/.env.example`
  - `backend/.env` (copied working credentials and adjusted redirect/frontend URLs for this new app)
- Added frontend env files:
  - `frontend/.env.example`
  - `frontend/.env`

## Run instructions

### Docker (single command)

From project root:

1. `cd D:/USA/clever-ai-tutor`
2. `docker compose up --build`

App URLs:

- Frontend: `http://localhost:5174`
- Backend: `http://localhost:8003`

Notes:

- Backend still authenticates against your main site at `http://localhost:8000`
- In Docker, backend uses `host.docker.internal:8000` internally to reach host machine APIs
- Keep your main site running on port `8000` before logging in

### Backend

1. `cd D:/USA/clever-ai-tutor/backend`
2. `python -m venv .venv`
3. `.venv/Scripts/activate`
4. `pip install -r requirements.txt`
5. `uvicorn app.main:app --reload --port 8003`

### Frontend

1. `cd D:/USA/clever-ai-tutor/frontend`
2. `npm install`
3. `npm run dev -- --port 5174`

## Current status

- Project scaffolding completed
- Auth flow wiring completed
- Main-site proxy wiring completed
- Frontend wired to login, session check, experts fetch, and demo expert chat
- Dockerized with one-command startup via `docker compose up --build`

## 2026-03-10 - Phase 1 execution started

- Backend refactored from single-file app into modular structure:
  - `app/config.py` for validated settings
  - `app/logging_config.py` for structured logging setup
  - `app/middleware/request_logging.py` for request ID + latency logs
  - `app/routers/auth.py`, `app/routers/proxy.py`, `app/routers/health.py`
- Existing auth and main-site proxy behavior preserved through routers
- Added new backend dependencies:
  - `pydantic-settings`
  - `structlog`
- Backend syntax validation passed (`python -m compileall app`)

## 2026-03-10 - Next task completed (`1.1.5`)

- Added DB pool lifecycle management using `asyncpg`:
  - Startup initializes pool when `DATABASE_URL` is configured
  - Shutdown closes pool cleanly
- Added DB health check integration:
  - `/health` and `/api/health` now return DB status (`ok`, `error`, or `not_configured`)
- Added DB env settings to `backend/.env.example`:
  - `DATABASE_URL`
  - `DB_POOL_MIN_SIZE`
  - `DB_POOL_MAX_SIZE`
- Added `asyncpg` to backend requirements
- Re-validated backend syntax after changes

## 2026-03-10 - Next task completed (`1.1.6`)

- Migrated frontend from Vite SPA to Next.js 16 (App Router) with TypeScript strict mode
- Added core Next.js files:
  - `app/layout.tsx`
  - `app/page.tsx` (ported existing login/session/experts/demo-chat behavior)
  - `app/globals.css`
  - `next.config.ts`
  - `tsconfig.json`
  - `next-env.d.ts`
  - `.eslintrc.json` (Next.js config)
- Updated frontend env key:
  - `VITE_API_BASE_URL` -> `NEXT_PUBLIC_API_BASE_URL`
- Updated Docker setup for Next.js runtime:
  - `frontend/Dockerfile` now builds and serves Next.js app
  - `docker-compose.yml` build arg updated to `NEXT_PUBLIC_API_BASE_URL`
- Verified build success with `npm run build`

## 2026-03-10 - Next task completed (`1.1.7`)

- Added Tailwind CSS v4 setup for Next.js:
  - Installed `tailwindcss`, `@tailwindcss/postcss`, `postcss`
  - Added `postcss.config.mjs`
  - Enabled Tailwind import in `app/globals.css`
- Added shadcn-compatible foundation:
  - `components.json`
  - `lib/utils.ts` (`cn()` helper)
  - `components/ui/button.tsx` reusable button component
- Added light/dark OKLCH theme tokens in `app/globals.css`
- Updated `app/page.tsx` to use the reusable shadcn-style `Button`
- Verified production build still passes after UI stack changes

## 2026-03-10 - Next task completed (`1.1.8`)

- Added Zustand state skeleton with separate stores:
  - `stores/auth-store.ts`
  - `stores/session-store.ts`
  - `stores/ui-store.ts`
  - `stores/chat-store.ts`
- Installed Zustand dependency
- Integrated stores into `app/page.tsx`:
  - session/auth state updates on login/session load/logout
  - chat prompt/result/error/loading state via store
  - UI theme mode store with dark/light toggle
- Verified frontend build after store integration

## 2026-03-10 - Next task completed (`1.1.9`)

- Added centralized API client module: `lib/api-client.ts`
  - Standardized GET/POST/PUT/PATCH/DELETE methods
  - Retry with exponential backoff for transient failures (408/429/5xx)
  - Normalized error handling via `ApiError` (status + payload)
  - Unauthorized hook support for auth/session clearing
- Refactored `app/page.tsx` to use API client for:
  - `/api/me`
  - `/api/main-site/api/experts`
  - `/api/logout`
  - `/api/main-site/api/expert-chat`
- Verified frontend production build and lint diagnostics after refactor

## 2026-03-10 - Next task completed (`1.1.10`)

- Implemented layout shell structure in frontend UI:
  - Left sidebar navigation panel
  - Top header bar for global actions
  - Main content container for module pages/cards
- Updated `app/globals.css` with shell layout and responsive behavior
- Updated `app/page.tsx` to render existing session/expert/chat cards inside the new shell
- Verified frontend production build and lint diagnostics after layout changes

## 2026-03-10 - Next task completed (`1.1.11`)

- Expanded `docker-compose.yml` to include full Sprint 1.1 service set:
  - `tutor-api` (FastAPI)
  - `tutor-frontend` (Next.js)
  - `tutor-db` (PostgreSQL + pgvector image)
  - `tutor-redis` (Redis 8)
  - `tutor-celery` (Celery worker)
  - `tutor-sandbox` (Docker-in-Docker sandbox)
- Added service health checks and startup dependencies (`depends_on` with health conditions)
- Added named volumes for DB/Redis/sandbox persistence
- Added minimal Celery bootstrap in backend:
  - `app/tasks/celery_app.py`
  - `app/tasks/__init__.py`
- Added `celery[redis]` dependency and `REDIS_URL` config support
- Validated compose file with `docker compose config`
- Re-validated backend syntax after Celery/config changes

## 2026-03-10 - Next task completed (`1.1.12`)

- Added `backend/db/init.sql` with idempotent PostgreSQL schema setup:
  - Core tutoring tables (`tutor_users`, `tutor_sessions`, `tutor_messages`, personas)
  - RAG tables (`knowledge_bases`, `kb_documents`, `kb_chunks`, assignments)
  - Class/enrollment/parent link tables
  - Learning intelligence, assessments, gamification, flashcards, standards
  - Portfolio/analytics/notifications/restrictions/learning-path tables
  - pgvector extension + HNSW vector index for chunk embeddings
  - Supporting indexes for high-frequency foreign key and query paths
- Wired schema init into Docker DB startup:
  - Mounted `./backend/db/init.sql` -> `/docker-entrypoint-initdb.d/01-init.sql`
- Validated compose configuration after SQL init wiring

## 2026-03-10 - Next task completed (`1.1.13`)

- Added `backend/db/seed.sql` with idempotent seed data for:
  - 6 default tutor personas (Sofia, Marcus, Aiko, Reza, Dr. Chen, Alex)
  - standards frameworks (Common Core + NGSS)
  - starter standards records (Math, ELA, Science)
  - starter subject/topic concept nodes (Math, Science, ELA, Coding)
- Wired seed file into Postgres container init:
  - Mounted `./backend/db/seed.sql` -> `/docker-entrypoint-initdb.d/02-seed.sql`
- Validated compose configuration after seed wiring

## 2026-03-10 - Next task completed (`1.1.14`)

- Added root `Makefile` with targets:
  - `dev`, `test`, `migrate`, `seed`, `lint`, `format`
- Added Windows-friendly automation scripts in `scripts/`:
  - `dev.ps1` (docker compose up --build)
  - `test.ps1` (backend compile + frontend production build)
  - `migrate.ps1` (apply `01-init.sql` to running DB)
  - `seed.ps1` (apply `02-seed.sql` to running DB)
  - `lint.ps1` (frontend TypeScript check + backend compile)
  - `format.ps1` (placeholder messaging until formatter stack is added)
- Updated frontend `lint` script in `package.json` to `tsc --noEmit` (compatible with Next.js 16 CLI changes)
- Validated:
  - `scripts/lint.ps1` runs successfully
  - `scripts/test.ps1` runs successfully
