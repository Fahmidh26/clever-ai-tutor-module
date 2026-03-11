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

## 2026-03-10 - Next task completed (`1.1.15`)

- Added CI workflow: `.github/workflows/ci.yml`
  - Job 1: `lint-typecheck`
    - install backend/frontend dependencies
    - backend syntax check (`python -m compileall backend/app`)
    - frontend type-check (`npm run lint` -> `tsc --noEmit`)
  - Job 2: `test-build`
    - backend sanity check
    - frontend production build
    - docker compose config validation
- Locally validated CI-equivalent command sequence:
  - backend compile
  - frontend lint/type-check
  - frontend build
  - compose config validation

## 2026-03-10 - Next task completed (`1.2.1`)

- Added root site integration service layer:
  - `backend/app/services/root_site_client.py`
  - `backend/app/services/__init__.py`
- Implemented `RootSiteClient` capabilities:
  - OAuth authorization-code token exchange (`POST /api/oauth/token`)
  - JWT verification for RS256 tokens with JWKS endpoint caching
  - User profile fetch with compatibility fallback (`/api/user/details` -> `/api/user`)
  - Credits APIs (`GET /api/user/credits`, `POST /api/user/credits/deduct`)
  - Model catalog fetch with ETag caching (`GET /api/catalog`)
  - Plan/subscription access check helper
- Refactored auth callback to use `RootSiteClient` for token exchange and profile fetch.
- Added root-site JWT/JWKS config fields:
  - `ROOT_SITE_JWKS_URL`
  - `ROOT_SITE_JWKS_PATH`
  - `ROOT_SITE_JWT_ISSUER`
  - `ROOT_SITE_JWT_AUDIENCE`
  - `ROOT_SITE_JWKS_CACHE_TTL_SECONDS`
- Added backend dependency: `PyJWT[crypto]`
- Validation run:
  - `python -m compileall backend/app`
  - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-10 - Next task completed (`1.2.3`)

- Implemented internal service-to-service auth header support (`X-Auth-Hex`) for root-site calls.
- Added backend config/env key:
  - `ROOT_SITE_X_AUTH_HEX`
- Wired header injection into:
  - `RootSiteClient` outbound requests in `backend/app/services/root_site_client.py`
  - Main-site proxy outbound requests in `backend/app/routers/proxy.py`
- Behavior:
  - If `ROOT_SITE_X_AUTH_HEX` is set, backend includes `X-Auth-Hex: <value>` for root-site calls.
  - If unset, behavior remains backward-compatible (no header added).
- Validation run:
  - `python -m compileall backend/app`
  - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-10 - Next task completed (`1.2.4`)

- Added token metering service:
  - `backend/app/services/token_service.py`
- Implemented token service flows:
  - Estimate tokens before model execution (`estimate_tokens`)
  - Reserve credits via root site (`reserve_credits`, action=`reserve`)
  - Reconcile actual usage after model execution (`reconcile_credits`, action=`reconcile`)
  - Convenience flow to estimate + reserve in one step (`estimate_and_reserve`)
- Added typed result structures for estimates/reservations (`TokenEstimate`, `CreditReservation`)
- Wired token service singleton in `backend/app/services/__init__.py` using configured defaults
- Added tunable token settings in backend config/env:
  - `TOKEN_ESTIMATE_CHARS_PER_TOKEN`
  - `TOKEN_RESERVE_BUFFER_RATIO`
  - `TOKEN_DEFAULT_OUTPUT_TOKENS`
- Validation run:
  - `python -m compileall backend/app`
  - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-10 - Next task completed (`1.2.6`)

- Added frontend auth context provider:
  - `frontend/components/auth/auth-context.tsx`
  - Centralized session refresh (`/api/me`), login start, logout, and auth state hydration
- Added protected route wrapper:
  - `frontend/components/auth/protected-route.tsx`
  - Blocks page content when unauthenticated and shows login CTA
- Wired provider at app root:
  - `frontend/app/layout.tsx` now wraps app with `AuthProvider`
- Refactored main page to consume auth context and rely on `ProtectedRoute`:
  - Removed duplicated per-page session bootstrapping logic
  - Preserved existing experts fetch and demo chat behavior for authenticated users
- Validation run:
  - `npm run lint` (frontend)
  - `npm run build` (frontend)

## 2026-03-11 - Next task completed (`1.2.8`)

- Added tutor user sync service:
  - `backend/app/services/tutor_user_sync.py`
  - Extracts root user identity from provider payload and upserts into `tutor_users`
  - Persists baseline tutor profile fields on login (`role`, `display_name`, `grade_level`, `preferred_language`, `interests_json`)
  - Marks first login via insert-vs-update detection and returns typed sync result
- Wired first-login sync into OAuth callback:
  - `backend/app/routers/auth.py` now calls sync immediately after provider profile fetch
  - Login flow now fails with explicit API error if tutor sync cannot complete (DB missing/invalid payload)
  - Session `user` payload now includes `tutor_user` metadata (`tutor_user_id`, `root_user_id`, `role`, `grade_level`, `preferred_language`, `first_login`)
- Exported sync utilities in `backend/app/services/__init__.py` for router usage.
- Validation run:
  - `python -m compileall backend/app`
  - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-11 - Next task completed (`1.2.9`)

- Added RBAC service:
  - `backend/app/services/rbac.py`
  - Resolves canonical role from session user (`tutor_user.role` fallback to `user.role`)
  - Defines role rules for proxied routes and returns typed access decisions
- Enforced backend role checks in proxy router:
  - `backend/app/routers/proxy.py`
  - Added RBAC checks before forwarding requests to main site
  - Role restrictions:
    - `/api/admin*` -> `admin`
    - `/api/teacher*` -> `teacher`, `admin`
    - `/api/parent*` -> `parent`, `admin`
  - Unauthorized role requests now return `403` with required role metadata
- Extended session endpoint for frontend guards:
  - `backend/app/routers/auth.py` `/api/me` now includes resolved `role`
- Added frontend role-aware protected route support:
  - `frontend/components/auth/auth-context.tsx` now stores/exposes `role`
  - `frontend/components/auth/protected-route.tsx` now supports optional `allowedRoles` prop
  - Existing usage remains backward-compatible for auth-only pages
- Validation run:
  - `python -m compileall backend/app`
  - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-11 - Next task completed (`1.2.10`)

- Added Redis-backed rate limiter service:
  - `backend/app/services/rate_limiter.py`
  - Per-user + per-endpoint counters using Redis `INCR` + `EXPIRE` in time windows
  - Endpoint key normalization and structured 429 response payload (`limit`, `remaining`, `reset_after_seconds`)
  - Fail-open behavior if user identity is missing or Redis client is unavailable
- Wired rate limiter lifecycle into FastAPI app startup/shutdown:
  - `backend/app/main.py` now initializes and closes Redis rate-limiter client in lifespan
- Enforced rate limits on authenticated API routes:
  - `backend/app/routers/auth.py` for `/api/me` and `/api/logout`
  - `backend/app/routers/proxy.py` for `/api/main-site/{path:path}`
- Added tunable settings:
  - `backend/app/config.py`:
    - `rate_limit_requests_per_window` (default `120`)
    - `rate_limit_window_seconds` (default `60`)
  - `backend/.env.example`:
    - `RATE_LIMIT_REQUESTS_PER_WINDOW=120`
    - `RATE_LIMIT_WINDOW_SECONDS=60`
- Validation run:
  - `python -m compileall backend/app`
  - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-11 - Next task completed (`1.3.1`)

- Added provider abstraction layer under `backend/app/services/ai_providers/`:
  - `base.py`:
    - `BaseProvider` abstract class with unified interface:
      - `stream_chat(messages, model_config)` -> `AsyncGenerator[str, None]`
      - `count_tokens(text)` -> `int`
    - Shared typed payloads (`ChatMessage`, `ModelConfig`) and `ProviderError`
  - `registry.py`:
    - `ProviderRegistry` for provider registration + lookup
    - Model/provider resolution guard (`resolve`) with support validation
  - `__init__.py` exports for clean imports by upcoming provider implementations
- Wired global registry singleton:
  - `backend/app/services/__init__.py` now initializes `provider_registry = ProviderRegistry()`
- This creates the stable interface needed for upcoming provider tasks (`1.3.2+`) without locking to a specific vendor implementation yet.
- Validation run:
  - `python -m compileall backend/app`
  - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-11 - Next task completed (`1.3.2`)

- Added OpenAI provider implementation:
  - `backend/app/services/ai_providers/openai_provider.py`
  - Direct `httpx` integration with OpenAI Chat Completions streaming endpoint (`/v1/chat/completions`)
  - SSE chunk parsing (`data: ...`) with incremental token-yield support for future streaming endpoints
  - Supported models: `gpt-4o`, `gpt-4o-mini`
  - Token estimation method (`count_tokens`) aligned with existing heuristic
- Wired provider registration:
  - `backend/app/services/__init__.py` now auto-registers `OpenAIProvider` when `OPENAI_API_KEY` is configured
  - `backend/app/services/ai_providers/__init__.py` exports `OpenAIProvider`
- Added OpenAI settings:
  - `backend/app/config.py`:
    - `openai_api_key`
    - `openai_base_url`
    - `openai_timeout_seconds`
  - `backend/.env.example`:
    - `OPENAI_API_KEY`
    - `OPENAI_BASE_URL`
    - `OPENAI_TIMEOUT_SECONDS`
- Exposed provider readiness in health output:
  - `backend/app/routers/health.py` now returns registered provider names
- Validation run:
  - `python -m compileall backend/app`
  - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-11 - Cross-repo coordination note

- Session handoff/checklist now explicitly track both repos:
  - Tutor app: `D:\USA\clever-ai-tutor`
  - Main site: `C:\AISITENEW`
- Rule going forward: when roadmap work needs shared APIs or data contracts, implement coordinated updates in both repos to keep integration in sync.

## 2026-03-11 - Next task completed (`1.3.3`)

- Added Anthropic provider implementation:
  - `backend/app/services/ai_providers/anthropic_provider.py`
  - Direct `httpx` integration with Anthropic Messages streaming endpoint (`/v1/messages`)
  - SSE chunk parsing for `content_block_delta` token output
  - Supported models: `claude-4-sonnet`, `claude-4-haiku`
  - Token estimation method (`count_tokens`) aligned with existing heuristic
- Wired provider registration:
  - `backend/app/services/__init__.py` now auto-registers `AnthropicProvider` when `ANTHROPIC_API_KEY` is configured
  - `backend/app/services/ai_providers/__init__.py` exports `AnthropicProvider`
- Added Anthropic settings:
  - `backend/app/config.py`:
    - `anthropic_api_key`
    - `anthropic_base_url`
    - `anthropic_api_version`
    - `anthropic_timeout_seconds`
  - `backend/.env.example`:
    - `ANTHROPIC_API_KEY`
    - `ANTHROPIC_BASE_URL`
    - `ANTHROPIC_API_VERSION`
    - `ANTHROPIC_TIMEOUT_SECONDS`
- Validation run:
  - `python -m compileall backend/app`
  - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-11 - Next task completed (`1.3.4`)

- Added Gemini provider implementation:
  - `backend/app/services/ai_providers/gemini_provider.py`
  - Direct `httpx` integration with Gemini streaming endpoint (`:streamGenerateContent?alt=sse`)
  - SSE chunk parsing for streamed candidate text tokens
  - Supported models: `gemini-2.5-pro`, `gemini-2.5-flash`
  - Token estimation method (`count_tokens`) aligned with existing heuristic
- Wired provider registration:
  - `backend/app/services/__init__.py` now auto-registers `GeminiProvider` when `GEMINI_API_KEY` is configured
  - `backend/app/services/ai_providers/__init__.py` exports `GeminiProvider`
- Added Gemini settings:
  - `backend/app/config.py`:
    - `gemini_api_key`
    - `gemini_base_url`
    - `gemini_timeout_seconds`
  - `backend/.env.example`:
    - `GEMINI_API_KEY`
    - `GEMINI_BASE_URL`
    - `GEMINI_TIMEOUT_SECONDS`
- Validation run:
  - `python -m compileall backend/app`
  - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-11 - Architecture pivot: main-site-only function execution

- Confirmed architecture rule from product direction:
  - Tutor app must not require direct provider API keys
  - All AI/expert/function execution is delegated to main-site APIs (`C:\AISITENEW`)
  - Tutor backend acts as authenticated proxy/orchestrator only
- Backend changes in tutor repo:
  - `backend/app/config.py`:
    - Removed direct provider key/base-url settings
    - Added `ai_execution_mode` with default `main_site_proxy_only`
  - `backend/.env.example`:
    - Removed provider key variables (`OPENAI_*`, `ANTHROPIC_*`, `GEMINI_*`)
    - Added `AI_EXECUTION_MODE=main_site_proxy_only`
  - `backend/app/services/__init__.py`:
    - Removed concrete provider registrations
    - Exposes `ai_execution_mode` for runtime visibility
  - `backend/app/routers/health.py`:
    - Replaced provider list output with `ai_execution_mode`
  - Removed direct provider implementations:
    - `backend/app/services/ai_providers/openai_provider.py`
    - `backend/app/services/ai_providers/anthropic_provider.py`
    - `backend/app/services/ai_providers/gemini_provider.py`
    - Updated `backend/app/services/ai_providers/__init__.py` exports accordingly
- Frontend clarification:
  - `frontend/app/page.tsx` text now explicitly states proxy-only AI function calls via main site
- Docs/handoff updated:
  - `AI_TUTOR_PROGRESS_CHECKLIST.md` and `SESSION_HANDOFF.md` now enforce main-site-proxy execution rule
- Validation run:
  - `python -m compileall backend/app`
  - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-11 - Main-site tutor API contract implemented (`C:\AISITENEW`)

- Added new authenticated tutor endpoints in main site (`routes/api.php`):
  - `GET /api/experts`
  - `POST /api/expert-chat`
  - `GET /api/tutor/sessions`
  - `POST /api/tutor/sessions`
  - `GET /api/tutor/sessions/{session}`
- Added controller:
  - `C:\AISITENEW\app\Http\Controllers\Api\TutorGatewayController.php`
  - Provides tutor expert catalog, executes chat on main site, persists sessions/messages, returns session payloads.
- Persistence path now centralized in main site:
  - Uses `ai_chats` and `ai_chat_messages` for tutor session/message storage.
  - Credits/token deduction remains on main-site side.
- Tutor repo alignment:
  - Added `RootSiteClient` helper methods for new main-site tutor endpoints:
    - `fetch_tutor_experts`
    - `tutor_expert_chat`
    - `list_tutor_sessions`
    - `create_tutor_session`
    - `get_tutor_session`
- Main-site validation run:
  - `php -l app/Http/Controllers/Api/TutorGatewayController.php`
  - `php -l routes/api.php`
  - `php artisan route:list --path=api` (verified new routes are registered)

## 2026-03-11 - Next task completed (`1.3.7`)

- Added SSE streaming chat endpoint on main site:
  - `POST /api/tutor/sessions/{session}/chat` in `C:\AISITENEW\routes\api.php`
  - Implemented in `C:\AISITENEW\app\Http\Controllers\Api\TutorGatewayController.php::streamSessionChat`
  - Behavior:
    - validates ownership of session
    - executes tutor model call on main site
    - persists prompt/response into `ai_chat_messages`
    - updates `ai_chats.total_words`
    - deducts tokens/credits on main-site side
    - streams SSE events (`stream_start`, `token`, `stream_end`)
- Added tutor proxy streaming pass-through:
  - `backend/app/routers/proxy.py` now detects `Accept: text/event-stream`
  - Uses upstream streamed request and returns `StreamingResponse` without buffering
  - Preserves existing JSON behavior for non-stream requests
- Validation run:
  - Tutor repo:
    - `python -m compileall backend/app`
    - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`
  - Main site:
    - `php -l app/Http/Controllers/Api/TutorGatewayController.php`
    - `php -l routes/api.php`
    - `php artisan route:list --path=api` (verified `api/tutor/sessions/{session}/chat`)

## 2026-03-11 - Next task completed (`1.3.8`)

- Hardened main-site tutor execution strategy in `C:\AISITENEW\app\Http\Controllers\Api\TutorGatewayController.php`:
  - Added retry/fallback/timeout handling inside `runModelCompletion(...)`
  - Candidate model selection now uses:
    - site default model
    - active OpenAI models from `AISettings`
    - safe final fallbacks (`gpt-4o-mini`, `gpt-4o`)
  - Retries transient failures (`408`, `429`, `5xx`) with short backoff
  - Enforces per-request timeout via Laravel HTTP client
  - Emits structured attempt metadata for observability
- Response/stream metadata improvements:
  - `expertChat` JSON now includes `execution` details (`strategy`, `fallback_used`, `attempts`)
  - SSE stream start/end events now include fallback/attempt context
- Validation run:
  - Main site:
    - `php -l app/Http/Controllers/Api/TutorGatewayController.php`
    - `php -l routes/api.php`
    - `php artisan route:list --path=api` (stream route still present)
  - Tutor repo:
    - `python -m compileall backend/app`
    - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-11 - Next task completed (Safety / guardrail middleware)

- Added request safety middleware on main-site tutor endpoints:
  - `C:\AISITENEW\app\Http\Middleware\TutorGuardrailMiddleware.php`
  - Applied to:
    - `POST /api/expert-chat`
    - `POST /api/tutor/sessions/{session}/chat`
  - Behavior:
    - scans `message` and conversation content
    - blocks clearly unsafe request patterns with `422` (`unsafe_input_detected`)
- Added output safety sanitization in tutor gateway:
  - `C:\AISITENEW\app\Http\Controllers\Api\TutorGatewayController.php`
  - unsafe generated output is replaced with safe refusal text before persisting/returning/streaming
- Registered middleware alias:
  - `C:\AISITENEW\app\Http\Kernel.php` -> `tutor.guardrail`
- Validation run:
  - Main site:
    - `php -l app/Http/Middleware/TutorGuardrailMiddleware.php`
    - `php -l app/Http/Controllers/Api/TutorGatewayController.php`
    - `php -l app/Http/Kernel.php`
    - `php -l routes/api.php`
    - `php artisan route:list --path=api` (tutor routes still present)
  - Tutor repo:
    - `python -m compileall backend/app`
    - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-11 - Next task completed (Token usage metering + credit reconciliation)

- Hardened billing metering in main-site tutor gateway:
  - `C:\AISITENEW\app\Http\Controllers\Api\TutorGatewayController.php`
  - Added billing metric assembly per completion:
    - estimated input/output/total tokens
    - reserved tokens (buffered estimate)
    - actual tokens (provider usage fallback to estimate)
    - reconcile delta (`actual - reserved`)
  - Added billing metadata to:
    - `/api/expert-chat` JSON responses
    - SSE stream events (`stream_start`, `stream_end`)
    - persisted `ai_chat_messages.result` payload
- Credit/token deduction now reconciles against computed actual token usage:
  - Uses `deductUserTokensAndCredits(actual_tokens, 0, model, user_id)`
  - Keeps all token/credit authority in main site.
- Validation run:
  - Main site:
    - `php -l app/Http/Controllers/Api/TutorGatewayController.php`
    - `php -l routes/api.php`
    - `php artisan route:list --path=api`
  - Tutor repo:
    - `python -m compileall backend/app`
    - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-11 - Next task completed (7 interaction modes)

- Added mode-capable tutor APIs on main site:
  - `C:\AISITENEW\app\Http\Controllers\Api\TutorGatewayController.php`
  - New mode catalog endpoint: `GET /api/tutor/modes`
  - New session mode switch endpoint: `POST /api/tutor/sessions/{session}/mode`
  - Added 7 defined modes:
    - `teach_me`, `quiz_me`, `practice`, `explore`, `show_thinking`, `writing_workshop`, `debate_roleplay`
- Wired mode-aware prompt behavior:
  - Chat message construction now appends mode-specific instructions to the system prompt layer
  - Applied to both:
    - standard completion path (`/api/expert-chat`)
    - SSE streaming path (`/api/tutor/sessions/{session}/chat`)
- Added per-session mode persistence (cache-backed):
  - Session mode is resolved from explicit request mode, otherwise from cached session mode, with fallback to `teach_me`
  - `createSession` and `getSession` now return current mode context
- Included mode metadata in outputs:
  - `/api/expert-chat` response includes `mode`
  - SSE `stream_start` and `stream_end` include `mode`
  - Persisted `ai_chat_messages.result` includes `mode`
- Updated tutor proxy client surface:
  - `D:\USA\clever-ai-tutor\backend\app\services\root_site_client.py`
  - `tutor_expert_chat(...)` accepts optional `mode`
  - Added `list_tutor_modes(...)` and `set_tutor_session_mode(...)`
- Route registration updates:
  - `C:\AISITENEW\routes\api.php` includes tutor mode routes
- Validation run:
  - Main site:
    - `php -l app/Http/Controllers/Api/TutorGatewayController.php`
    - `php -l routes/api.php`
    - `php artisan route:list --path=api` (verified `/api/tutor/modes` and `/api/tutor/sessions/{session}/mode`)
  - Tutor repo:
    - `python -m compileall backend/app`
    - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`

## 2026-03-11 - Next task completed (`1.3.5` xAI Grok provider via main-site proxy)

- Added provider-aware model execution in main-site tutor gateway:
  - `C:\AISITENEW\app\Http\Controllers\Api\TutorGatewayController.php`
  - Reworked retry/fallback from model-only to provider+model target routing
  - Supports OpenAI + xAI Grok using provider-specific credentials/base URLs
- Implemented Grok request path as OpenAI-compatible chat completions:
  - Provider `grok` resolves credentials from `config('services.xai.*')`
  - Requests sent to `https://api.x.ai/v1/chat/completions`
  - OpenAI path continues to use `https://api.openai.com/v1/chat/completions`
- Candidate model/provider selection now uses active `AISettings` rows:
  - Reads both `openai` and `grok` provider entries
  - Preserves default-model priority from `siteSettings.default_model`
  - Skips providers that have missing API keys (fail-open to other configured providers)
- Response/stream execution metadata now carries provider context:
  - JSON usage includes `provider` + `model`
  - SSE start/end metadata includes provider details
  - Execution attempt entries include provider for fallback observability
- Tutor app remains proxy-only and unchanged in architecture:
  - `D:\USA\clever-ai-tutor` still consumes main-site tutor APIs only
  - No direct provider keys/calls added in tutor repo
- Validation run:
  - Main site:
    - `php -l app/Http/Controllers/Api/TutorGatewayController.php`
    - `php artisan route:list --path=api/tutor`
  - Tutor repo:
    - `python -m compileall backend/app`
    - `powershell -ExecutionPolicy Bypass -File scripts/lint.ps1`
