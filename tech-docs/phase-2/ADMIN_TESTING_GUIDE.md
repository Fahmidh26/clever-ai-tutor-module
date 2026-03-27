# Admin Testing Guide

> Date: 2026-03-27
> Scope: Admin-only validation for the tutor app shell

---

## 1. What Was Added

Admin documentation now covers:

- admin as the only global role inside the same app shell
- admin relationship to teacher, student, and parent scopes
- global oversight expectations for users, classes, KBs, personas, and analytics
- override and repair expectations for future admin tooling

---

## 2. Data Source

Admin test data comes from these files:

- schema: `backend/db/init.sql`
- seed data: `backend/db/seed.sql`
- local-dev auth accounts: `backend/app/config.py`

The local auth config inserts deterministic admin login data:

- admin account: `admin@local.dev`
- password: `devpass123`
- teacher comparison account: `teacher@local.dev`
- student comparison account: `student@local.dev`
- parent comparison account: `parent@local.dev`

Current seeded teacher/class data useful for admin validation:

- class: `Grade 8 Physics A`
- KB: `Newton Laws Unit`
- teacher demo account and linked class data

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

## 5. Admin Login

1. Open `http://localhost:5174`
2. Click `Login with Local Dev Account`
3. Use:

```text
email: admin@local.dev
password: devpass123
```

If local auth is not enabled, set `AUTH_MODE=local_dev` in `backend/.env`.

---

## 6. Admin Test Sequence

### A. Admin Home / Role Boundary

Confirm:

- admin lands in the same app shell
- role resolves to `admin`
- admin is treated as elevated/global rather than student or teacher-only

### B. Current Elevated Route Access

Current repo reality:

- admin can use teacher/admin shared routes through RBAC
- dedicated admin global routes are not fully implemented yet

Actions:

1. open the current elevated workspace
2. verify admin can access teacher-capable sections
3. verify admin is not blocked from current teacher/admin management surfaces

### C. Teacher/Class Inspection

Use current seeded class data:

- `Grade 8 Physics A`
- teacher demo account and linked student data

Actions:

1. inspect current class management surfaces
2. inspect current teacher analytics surfaces
3. verify admin can review class-level state

### D. KB And Persona Inspection

Actions:

1. inspect KB management surfaces
2. inspect assigned KB state
3. inspect persona management or preview surfaces
4. verify admin can review the instructional asset state

### E. Negative Check Against Teacher Scope

This check is required even before dedicated admin routes exist.

Actions:

1. log in as teacher in a separate pass
2. verify teacher can use teacher-scoped management
3. verify the documentation still treats teacher as non-global
4. do not treat teacher access to shared routes as proof of admin-global governance

### F. Future Admin Route Readiness

Once dedicated admin routes are implemented later, validate:

1. user-role inventory
2. role promotion or correction
3. relationship repair
4. global analytics
5. teacher-negative checks for admin-only routes

---

## 7. Admin API Checks

Run these after admin login so the browser session cookie is present, or use an API client that carries session cookies.

Current admin-accessible route groups through RBAC:

- `GET /api/me`
- `GET /api/teacher/classes`
- `GET /api/teacher/roster`
- `GET /api/teacher/join-requests`
- `GET /api/teacher/personas`
- `GET /api/teacher/monitoring`
- `GET /api/teacher/analytics/struggling`
- `GET /api/teacher/reports`
- `GET /api/teacher/assessments`

Planned admin-only checks once implemented:

- `GET /api/admin/users`
- `POST /api/admin/users/{id}/role`
- `GET /api/admin/classes`
- `GET /api/admin/analytics/global`
- `POST /api/admin/governance/repair`

Negative scope checks to preserve:

- teacher must not gain admin-global route access once those routes exist
- student must not gain admin-global route access
- parent must not gain admin-global route access

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

RBAC Playwright coverage exists, but the mocked-browser auth harness still does not consistently enter the authenticated shell in the current setup.

Relevant specs:

- `frontend/e2e/role-routing-rbac.spec.ts`
- `frontend/e2e/teacher-dashboard.spec.ts`

Use them as the starting point after the auth-harness issue is fixed, but for now the most reliable admin validation path is:

1. static validation
2. seeded local admin login
3. real browser pass through the elevated-access checks above
