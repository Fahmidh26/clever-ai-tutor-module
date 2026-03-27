# Teacher Testing Guide

> Date: 2026-03-26
> Scope: Teacher-only validation for the tutor app shell

---

## 1. What Was Added

Teacher flows now cover:

- roster links separate from class enrollments
- teacher join codes and join request approval
- class invite rotation and student class self-join
- class-level persona policy with overlay instructions
- teacher monitoring, struggling queue, and session replay
- draft-only co-pilot suggestions, worksheet drafts, and report drafts
- teacher assessment authoring basics

---

## 2. Data Source

Teacher test data comes from these files:

- schema: `backend/db/init.sql`
- migration: `backend/db/migrations/2026-03-26_phase2_teacher_completion.sql`
- seed data: `backend/db/seed.sql`
- local-dev auth accounts: `backend/app/config.py`

The seed inserts a deterministic teacher demo setup:

- teacher account: `teacher@local.dev`
- password: `devpass123`
- student accounts:
  - `student@local.dev`
  - seeded DB-only students `Ava Newton` and `Leo Faraday`
- class: `Grade 8 Physics A`
- class invite code: `PHY8A`
- teacher join code: `TEACHPHY8`
- KB: `Newton Laws Unit`
- assessment: `Physics Checkpoint 1`
- report draft: `Physics Progress Draft`

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

## 5. Teacher Login

1. Open `http://localhost:5174`
2. Click `Login with Local Dev Account`
3. Use:

```text
email: teacher@local.dev
password: devpass123
```

If local auth is not enabled, set `AUTH_MODE=local_dev` in `backend/.env`.

---

## 6. Teacher Test Sequence

### A. Teacher Home / Role Boundary

Confirm:

- teacher lands in the same app shell
- teacher sees `Teacher Control Center`
- teacher sees teacher sections, not student-only gating

### B. Roster + Join Handshake

Expected seeded data:

- linked students include `Student Demo`, `Ava Newton`, `Leo Faraday`
- unassigned queue includes `Leo Faraday`
- pending join requests include `Leo Faraday`
- join code list includes `TEACHPHY8`

Actions:

1. open `Roster And Join Flow`
2. verify pending request exists
3. click `Approve`
4. verify `Leo Faraday` leaves the pending list
5. verify roster still contains the student

### C. Class Management

Expected seeded data:

- class `Grade 8 Physics A`
- invite code `PHY8A`

Actions:

1. open `Class & Roster Basics`
2. select `Grade 8 Physics A`
3. verify enrolled students include `Student Demo` and `Ava Newton`
4. optionally rotate class invite:
   - call `POST /api/teacher/classes/{class_id}/invite`

### D. Persona Policy

Expected seeded data:

- class persona already assigned from seeded persona `Reza`

Actions:

1. open `Class Persona Policy`
2. click `Preview Policy`
3. verify effective prompt preview appears
4. change overlay text
5. click `Save Class Persona`
6. verify updated class policy preview appears

### E. Monitoring + Replay

Expected seeded data:

- `Student Demo` has a physics session
- at least one misconception exists
- teacher monitoring shows class metrics

Actions:

1. open `Monitoring And Session Replay`
2. click `Student Demo`
3. verify student drill-down loads
4. verify replay dropdown contains a session
5. verify messages display in the replay pane
6. verify struggling queue shows at least one flagged student

### F. Reports + Co-Pilot

Expected seeded data:

- one saved draft report: `Physics Progress Draft`

Actions:

1. select a student in monitoring
2. open `Reports And Co-Pilot Drafts`
3. click `Generate Suggestions`
4. click `Draft Worksheet`
5. click `Save Draft Report`
6. verify the draft list updates

### G. Assessments

Expected seeded data:

- one assessment: `Physics Checkpoint 1`

Actions:

1. open `Assessments`
2. verify `Physics Checkpoint 1` appears
3. select it and verify its seeded question
4. add a new question
5. verify it appears in the detail pane

---

## 7. Teacher API Checks

Run these after teacher login so the browser session cookie is present, or use an API client that carries session cookies.

Teacher endpoints:

- `GET /api/teacher/roster`
- `POST /api/teacher/join-codes`
- `GET /api/teacher/join-requests`
- `POST /api/teacher/join-requests/{id}/approve`
- `POST /api/teacher/classes/{id}/invite`
- `POST /api/tutor/classes/join`
- `GET /api/teacher/personas`
- `POST /api/teacher/personas/classes/{id}`
- `GET /api/teacher/analytics/class/{id}`
- `GET /api/teacher/analytics/students/{id}`
- `GET /api/teacher/analytics/struggling`
- `GET /api/teacher/session-replay/{id}`
- `POST /api/teacher/copilot/suggest`
- `POST /api/teacher/copilot/worksheet`
- `GET /api/teacher/reports`
- `POST /api/teacher/reports`
- `GET /api/teacher/assessments`
- `POST /api/teacher/assessments`

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

Teacher Playwright specs currently exist, but the mocked-browser auth harness still falls back to the local auth gate in the current setup instead of entering the authenticated shell.

Relevant specs:

- `frontend/e2e/teacher-dashboard.spec.ts`
- `frontend/e2e/role-routing-rbac.spec.ts`

Use them as the starting point after the auth-harness issue is fixed, but for now the most reliable teacher validation path is:

1. static validation
2. seeded local login
3. real browser pass through the teacher flows above

