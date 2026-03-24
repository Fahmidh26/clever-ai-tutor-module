# User Flows and Diagrams: Student vs Teacher/Admin

## ✅ High-level "Who does what" (Student vs Admin/Teacher)

This app is a **single-page Next.js frontend** that talks to a **FastAPI backend**.  
The overall user flow is:

1. **Open the site** → Frontend loads (React/Next).
2. **Sign in** → Backend OAuth / session established.
3. **Frontend fetches your profile & role** → decides whether to show student UI or teacher/admin UI.
4. **Use the app features** (chat tutoring, quizzes, dashboards, class/KB management, etc.).

---

## 🎓 Student (Learner) Flow

### 1) Go to the site
- Open the web UI (likely `http://localhost:3000/` in dev mode)
- If not signed in: you'll see **Sign in / Login**.

### 2) Sign in
- Click **Sign in**
- Frontend sends you to: **`/oauth/login`** (backend)
- After successful auth, you're redirected back to frontend and the session is stored in a cookie.

### 3) Frontend detects you as a student
- Frontend calls: **`GET /api/me`**
- Backend returns: `{ user, role }` (role = student/teacher/admin)
- Frontend shows the student workspace.

### 4) Student workspace actions (core paths / routes)
These are internal UI actions (not separate pages), but the backend endpoints used are:

- **Chat tutoring / AI help**
  - `POST /api/expert-chat`
- **Quiz + mastery tracking**
  - Likely uses: `POST /api/quizzes` / `GET /api/quiz...`
- **Progress dashboard**
  - `GET /api/tutor/progress/student`
- **Hints / flashcards / misconceptions**
  - `GET/POST /api/hints`
  - `GET/POST /api/flashcards`
  - `GET/POST /api/misconceptions`

### 5) Example Student journey (what they do in the UI)
1. Click "Ask a question" / type into chat
2. Choose a "mode" (e.g., "Teach me", "Quiz me", "Explain my answer")
3. Hit Send → backend calls `/api/expert-chat` → returns assistant response
4. Check progress via student dashboard (`/api/tutor/progress/student`)
5. Use flashcards, review misconceptions, etc.

---

## 🧑‍🏫 Teacher / Admin Flow (Class + Knowledge Base Management)

### 1) Go to the site → Sign in 
Same as student flow: open UI → sign in → backend stores session → frontend calls `GET /api/me`.

### 2) Frontend sees you as teacher/admin
- Role is determined by backend logic in: `app/services/rbac.py`
- If you're teacher/admin, the UI will expose "teacher dashboard" features.

### 3) Teacher/Admin core operations (key backend routes)

#### Class management
- Create a new class → `POST /api/teacher/classes`
- List your classes → `GET /api/teacher/classes`
- View roster + class stats → `GET /api/teacher/classes/{class_id}`

**What students do**: they enroll using the generated `invite_code`.

#### Teacher dashboard (class progress)
- Class-level progress (mastery, quiz accuracy, misconceptions) →  
  `GET /api/tutor/progress/teacher?class_id=<class_id>`

#### Knowledge Base (KB) management
- Create a KB → `POST /api/teacher/kb`
- List KBs you own → `GET /api/teacher/kb`
- Upload documents into KBs (PDF/DOCX/MD/etc) → `POST /api/teacher/kb/{kb_id}/documents`
- Remove / preview docs via `/api/teacher/kb/*`

**What this enables for students**:  
When a student chats through `/api/expert-chat`, they can request context from a KB with `kb_id` and the system will include RAG citations from your KB.

---

## 📌 Example diagram (student vs teacher flow)

### Mermaid-style flow (text diagram)

```mermaid
flowchart TD
  A[User opens site] --> B[Frontend loads]
  B --> C{Not signed in?}
  C -->|Yes| D[Click Sign in → /oauth/login]
  D --> E[OAuth provider → callback → session cookie]
  C -->|No| F[Already signed in]

  E --> G[Frontend calls /api/me]
  F --> G

  G --> H{Role?}
  H -->|Student| I[Show student UI]
  H -->|Teacher/Admin| J[Show teacher/admin UI]

  I --> K[Ask question → POST /api/expert-chat]
  I --> L[View progress → GET /api/tutor/progress/student]
  I --> M[Flashcards / hints / quizzes etc]

  J --> N[Create class → POST /api/teacher/classes]
  J --> O[View roster → GET /api/teacher/classes/{id}]
  J --> P[Create/manage KB → /api/teacher/kb]
  J --> Q[View class progress → /api/tutor/progress/teacher?class_id=...]
```

---

## ✅ Quick summary (where to go, what buttons do)

### Student
- **Go to**: main UI (root)
- **Login**: click login
- **Use**:
  - Chat: `POST /api/expert-chat`
  - Dashboard: `GET /api/tutor/progress/student`

### Teacher/Admin
- **Go to**: same UI; feature availability depends on role
- **Manage classes**:
  - Create: `POST /api/teacher/classes`
  - List: `GET /api/teacher/classes`
  - Detail: `GET /api/teacher/classes/{class_id}`
- **Manage KBs**:
  - Create: `POST /api/teacher/kb`
  - Upload docs: `POST /api/teacher/kb/{kb_id}/documents`
- **View progress**: `GET /api/tutor/progress/teacher?class_id=...`

---

If you want, I can also show the **exact UI screen/controls** (which buttons/actions in the React UI map to which API calls) by looking at the front-end components (like `page.tsx`, `chat-store.ts`, etc.).</content>
<parameter name="filePath">d:\USA\clever-ai-tutor\USER_FLOWS_DIAGRAMS.md