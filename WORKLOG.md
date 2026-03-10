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
