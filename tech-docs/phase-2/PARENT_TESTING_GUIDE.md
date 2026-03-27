# Parent Testing Guide

> Date: 2026-03-27
> Scope: Parent-only validation for the tutor app shell

---

## 1. What Was Added

Parent documentation now covers:

- parent as a linked-child support role in the same app shell
- linked-child boundary rules
- parent-readable progress and report expectations
- future controls and communication surfaces with explicit implementation gaps

---

## 2. Data Source

Parent test data comes from these files:

- schema: `backend/db/init.sql`
- seed data: `backend/db/seed.sql`
- local-dev auth accounts: `backend/app/config.py`

The local auth config inserts deterministic parent login data:

- parent account: `parent@local.dev`
- password: `devpass123`
- child comparison account: `student@local.dev`
- teacher comparison account: `teacher@local.dev`
- admin comparison account: `admin@local.dev`

Current repo reality:

- parent role exists in auth and RBAC
- deterministic parent-child browser seed flow may still need explicit seed additions or validation queries

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

## 5. Parent Login

1. Open `http://localhost:5174`
2. Click `Login with Local Dev Account`
3. Use:

```text
email: parent@local.dev
password: devpass123
```

If local auth is not enabled, set `AUTH_MODE=local_dev` in `backend/.env`.

---

## 6. Parent Test Sequence

### A. Parent Home / Role Boundary

Confirm:

- parent lands in the same app shell
- role resolves to `parent`
- parent is not treated as teacher or admin

### B. Linked Child Resolution

Current repo reality:

- parent-specific linked-child flows are mostly scaffolded
- deterministic linked-child seed verification may require SQL inspection until parent routes exist

Actions:

1. verify parent login works
2. verify parent shell gating does not expose teacher/admin tools
3. once parent child routes exist, verify linked-child list or empty state

### C. Child Overview And Progress

When parent child routes exist later:

1. select a linked child
2. review child overview
3. review progress summary
4. review mastery or misconception summaries in parent-readable form

### D. Reports And Handoffs

When parent report routes exist later:

1. load parent-facing report or summary
2. verify it is limited to linked-child scope
3. verify it does not expose raw teacher-global analytics

### E. Negative Scope Checks

Actions:

1. try to access teacher-only routes
2. try to access admin-global routes
3. verify parent cannot browse unrelated students
4. verify parent remains read-heavy rather than classroom-owner

---

## 7. Parent API Checks

Run these after parent login so the browser session cookie is present, or use an API client that carries session cookies.

Current checks:

- `GET /api/me`

Planned parent route checks once implemented:

- `GET /api/parent/children`
- `GET /api/parent/children/{id}/overview`
- `GET /api/parent/children/{id}/progress`
- `GET /api/parent/children/{id}/reports`
- `GET /api/parent/controls`
- `GET /api/parent/communications`

Negative scope checks to preserve:

- `GET /api/teacher/roster`
- `GET /api/teacher/monitoring`
- `GET /api/admin/users`
- `GET /api/admin/analytics/global`

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

Parent-specific browser automation is not yet the reliable validation path because parent product surfaces remain scaffolded and the mocked-browser authenticated-shell issue still affects role-routing confidence.

Relevant starting point:

- `frontend/e2e/role-routing-rbac.spec.ts`

For now the most reliable parent validation path is:

1. static validation
2. seeded local parent login
3. real browser role-boundary pass
4. SQL or future API verification for linked-child visibility once implemented
