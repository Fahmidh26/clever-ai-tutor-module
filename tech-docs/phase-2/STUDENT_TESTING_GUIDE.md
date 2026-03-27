# Student Testing Guide

> Date: 2026-03-27
> Scope: Student-only validation for the tutor app shell

---

## 1. What Was Added

Student flows now cover:

- self-scoped role landing inside the same app shell
- class context and class self-join by invite code
- session create/list/resume behavior
- tutor chat and streaming persistence
- hints, quizzes, explain-my-answer, and flashcards
- mastery, misconceptions, and student dashboard review

---

## 2. Data Source

Student test data comes from these files:

- schema: `backend/db/init.sql`
- seed data: `backend/db/seed.sql`
- local-dev auth accounts: `backend/app/config.py`

The local auth config inserts deterministic login accounts:

- student account: `student@local.dev`
- password: `devpass123`
- teacher account for cross-role checks: `teacher@local.dev`
- admin account for cross-role checks: `admin@local.dev`

Seeded class data used by current teacher/student flows includes:

- class: `Grade 8 Physics A`
- class invite code: `PHY8A`
- KB: `Newton Laws Unit`

Expected student seeded behavior:

- `Student Demo` is enrolled in `Grade 8 Physics A`
- the student can see class-assigned materials
- the student has at least one prior physics session and related progress data in the seeded teacher validation scenario

---

## 3. Startup

### Option A: Docker Compose

From repo root:

```powershell
docker compose up --build
```

This starts:

- frontend: `http://localhost:5174`
- backend: `http://localhost:8003`
- postgres: `localhost:5433`

### Option B: Local Processes

Backend `.env` must include:

```env
AUTH_MODE=local_dev
FRONTEND_URL=http://localhost:5174
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/clever_ai_tutor
REDIS_URL=redis://localhost:6379/0
SESSION_SECRET_KEY=any-long-random-string
```

Then run:

```powershell
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

And in another terminal:

```powershell
cd frontend
cmd /c npm run dev
```

---

## 4. Load Or Refresh Seed Data

If you use Docker from a clean volume, `init.sql` and `seed.sql` run automatically.

If you need to re-apply manually:

```powershell
docker compose exec tutor-db psql -U postgres -d clever_ai_tutor -f /docker-entrypoint-initdb.d/01-init.sql
docker compose exec tutor-db psql -U postgres -d clever_ai_tutor -f /docker-entrypoint-initdb.d/02-seed.sql
```

If you are using a local Postgres instance instead:

```powershell
psql postgresql://postgres:postgres@localhost:5433/clever_ai_tutor -f backend/db/init.sql
psql postgresql://postgres:postgres@localhost:5433/clever_ai_tutor -f backend/db/seed.sql
```

---

## 5. Student Login

1. Open `http://localhost:5174`
2. Click `Login with Local Dev Account`
3. Use:

```text
email: student@local.dev
password: devpass123
```

If local auth is not enabled, set `AUTH_MODE=local_dev` in `backend/.env`.

---

## 6. Student Test Sequence

### A. Student Home / Role Boundary

Confirm:

- student lands in the same app shell
- student sees student tutoring workspace
- teacher/admin controls are not the primary workspace

### B. My Class Context

Expected seeded data:

- class `Grade 8 Physics A`
- assigned KB `Newton Laws Unit`

Actions:

1. open `My Class Context`
2. verify `Grade 8 Physics A` appears
3. verify assigned materials are visible
4. verify class context can be selected

### C. Session Start

Actions:

1. choose a tutor persona
2. create a new session or open an existing one
3. verify session history loads
4. verify class-aware context is retained when selected

### D. Tutor Chat

Actions:

1. send a student message
2. verify tutor response appears
3. if assigned KB context is active, verify citations appear
4. refresh or reopen the session and verify message history persists

### E. Hints, Quiz, And Flashcards

Actions:

1. open hint flow and progress through hint levels
2. open quiz flow and answer a question
3. use `Explain My Answer`
4. generate or review flashcards
5. verify progress records update without leaving student scope

### F. Dashboard And Review

Actions:

1. open student dashboard
2. verify student metrics load
3. verify mastery entries load
4. verify misconceptions load
5. verify the dashboard reflects the recent activity performed above

### G. Student Scope Protection

Actions:

1. try to access a teacher-only route such as `/api/teacher/roster`
2. verify access is blocked
3. verify student cannot browse unrelated student summaries
4. verify student cannot access admin-global tools

---

## 7. Student API Checks

Run these after student login so the browser session cookie is present, or use an API client that carries session cookies.

Student endpoints:

- `GET /api/tutor/classes`
- `POST /api/tutor/classes/join`
- `GET /api/tutor/sessions`
- `POST /api/tutor/sessions`
- `GET /api/tutor/sessions/{id}`
- `PATCH /api/tutor/sessions/{id}/mode`
- `POST /api/expert-chat`
- `POST /api/expert-chat/stream`
- `POST /api/tutor/hints/start`
- `POST /api/tutor/hints/{id}/next`
- `GET /api/tutor/hints/{id}`
- `POST /api/tutor/quiz/generate`
- `POST /api/tutor/quiz/{id}/submit`
- `POST /api/tutor/quiz/{id}/explain-my-answer`
- `GET /api/tutor/quiz/history`
- `GET /api/tutor/flashcards/decks`
- `POST /api/tutor/flashcards/generate`
- `POST /api/tutor/flashcards/review`
- `GET /api/tutor/mastery`
- `GET /api/tutor/misconceptions`
- `GET /api/tutor/progress/student`

Negative scope checks:

- `GET /api/teacher/roster`
- `GET /api/teacher/monitoring`
- `GET /api/teacher/analytics/struggling`

---

## 8. Static Validation

```powershell
cd frontend
cmd /c npm run lint

cd ..
python -m compileall backend/app
```

Current status in this repo:

- `tsc --noEmit` passes
- `python -m compileall backend/app` passes

---

## 9. Browser Automation Status

Student Playwright specs currently exist for tutor workspace coverage, but the broader mocked-browser authenticated-shell issue still affects some role-routing checks in the current setup.

Relevant specs:

- `frontend/e2e/tutor-workspace.spec.ts`
- `frontend/e2e/role-routing-rbac.spec.ts`

Use them as the starting point after the auth-harness issue is fixed, but for now the most reliable student validation path is:

1. static validation
2. seeded local login
3. real browser pass through the student flows above
