# AI Tutor Testing Guide (Simple)

This is a beginner-friendly guide for your current project state (up to Phase 2).

## 1) What You Should Test

Test in this order:

1. App starts correctly (backend + frontend + DB + Redis).
2. Basic login/session flow works.
3. Core tutor flow works (experts, session, chat, streaming).
4. Phase 2 features work (hints, quiz, explain-my-answer, flashcards, mastery, misconceptions, dashboards).
5. Build/type/sanity checks pass.

## 2) One-Time Setup

From project root (`d:\USA\clever-ai-tutor`):

```powershell
docker compose up -d tutor-db tutor-redis
```

In another terminal:

```powershell
cd backend
pip install -r requirements.txt
cd ../frontend
npm install
```

## 3) Route URLs (Where To Get Them)

Use these base URLs:

- Backend API base: `http://localhost:8003`
- Frontend app: `http://localhost:5174`
- Auto-generated API docs (all routes): `http://localhost:8003/docs`

Most important routes for your testing:

- Health: `GET http://localhost:8003/health`
- Auth/session: `GET http://localhost:8003/api/me`
- Experts: `GET http://localhost:8003/api/experts?domain=expert-chat`
- Chat: `POST http://localhost:8003/api/expert-chat`
- Streaming chat: `POST http://localhost:8003/api/expert-chat/stream`
- Sessions:
  - `POST http://localhost:8003/api/tutor/sessions`
  - `GET http://localhost:8003/api/tutor/sessions`
  - `GET http://localhost:8003/api/tutor/sessions/{session_id}`
  - `PATCH http://localhost:8003/api/tutor/sessions/{session_id}/mode`
- Modes: `GET http://localhost:8003/api/tutor/modes`
- Hints:
  - `POST http://localhost:8003/api/tutor/hints/start`
  - `POST http://localhost:8003/api/tutor/hints/{progression_id}/next`
  - `GET http://localhost:8003/api/tutor/hints/{progression_id}`
- Quiz:
  - `POST http://localhost:8003/api/tutor/quiz/generate`
  - `POST http://localhost:8003/api/tutor/quiz/{quiz_id}/submit`
  - `POST http://localhost:8003/api/tutor/quiz/{quiz_id}/explain-my-answer`
  - `GET http://localhost:8003/api/tutor/quiz/history`
- Flashcards:
  - `POST http://localhost:8003/api/tutor/flashcards/decks`
  - `GET http://localhost:8003/api/tutor/flashcards/decks`
  - `POST http://localhost:8003/api/tutor/flashcards/generate`
  - `GET http://localhost:8003/api/tutor/flashcards/review`
  - `POST http://localhost:8003/api/tutor/flashcards/{card_id}/review`
- Mastery:
  - `GET http://localhost:8003/api/tutor/mastery`
  - `POST http://localhost:8003/api/tutor/mastery/recompute`
- Misconceptions:
  - `GET http://localhost:8003/api/tutor/misconceptions`
  - `POST http://localhost:8003/api/tutor/misconceptions/{misconception_id}/resolve`
- Progress dashboards:
  - `GET http://localhost:8003/api/tutor/progress/student`
  - `GET http://localhost:8003/api/tutor/progress/teacher?class_id={class_id}`

## 4) Fast "Is It Alive?" Test (5 minutes)

1. Start backend:

```powershell
cd backend
uvicorn app.main:app --reload --port 8003
```

2. Start frontend:

```powershell
cd frontend
npm run dev
```

3. Open `http://localhost:5174`.
4. Confirm app loads and auth gate/login appears.
5. Confirm backend health works:

```powershell
curl http://localhost:8003/health
```

Expected: JSON response with healthy status.

## 5) Automated Checks You Already Have

From root:

```powershell
make test
```

This currently does:
- Backend syntax compile check.
- Frontend production build.

Extra checks:

```powershell
make lint
cd frontend; npm run e2e:list
cd frontend; npm run e2e
```

Notes:
- Your E2E tests exist and run with Playwright.
- Current E2E uses route mocks, so it validates UI flow without real backend dependency for those mocked calls.

## 6) Manual Feature Tests (Phase 2)

After login in the UI, test these one by one.

## Core tutor flow

- `Experts`: expert list appears.
- `Sessions`: create a new session and reopen it from history.
- `Chat`: send a normal message and get response.
- `Streaming`: response appears progressively (not only all at once).

## Hint progression

- Start hint flow.
- Click next hint until level 3.
- Confirm no invalid skip behavior.

## Adaptive quiz + explain-my-answer

- Generate quiz question.
- Submit an answer and get correctness feedback.
- Use explain-my-answer and confirm personalized explanation appears.

## Flashcards + spaced repetition

- Create or generate a deck.
- Review cards and submit rating/quality.
- Confirm next review updates logically.

## Mastery + misconception + progress dashboards

- Open mastery panel and refresh/recompute.
- Submit wrong quiz answer and check misconception appears.
- Resolve a misconception and verify status changes.
- Check student dashboard metrics update.
- If teacher role available: check teacher progress dashboard for class rollups.

## 7) Pass/Fail Rule (Simple)

Mark a feature as "tested" only if:

1. UI action succeeds without error.
2. Data persists after refresh/reload.
3. Related dashboard/panel reflects the change.

If any of these fail, treat as not done.

## 8) Recommended First Real Test Session

Do this exact sequence once:

1. Login.
2. Create session.
3. Send streamed chat message.
4. Do hint levels 1 -> 2 -> 3.
5. Generate quiz, answer wrong, run explain-my-answer.
6. Generate flashcards and review at least 2 cards.
7. Open mastery/misconception/dashboard and confirm updates.

If all 7 pass, your Phase 2 baseline is functionally validated.

## 9) If Swagger Shows Only A Few Routes

If `/docs` only shows auth/health/proxy routes, do this:

1. Stop old backend processes/containers using port `8003`.
2. Reinstall backend deps (important):

```powershell
cd backend
pip install -r requirements.txt
```

3. Start backend again from this repo:

```powershell
cd backend
uvicorn app.main:app --reload --port 8003
```

4. Hard refresh Swagger: `http://localhost:8003/docs`.

Why this happens:
- Often an old backend instance is still running on `8003`.
- Or a dependency was missing and some newer routes could not load correctly.
