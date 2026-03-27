# Phase 2 Ecosystem Mapping

> Date: 2026-03-25
> Purpose: Canonical map for how identity, classroom setup, tutor personas, KB/RAG, student activity, and dashboards link together inside the tutor repo.

---

## Planning References

- Teacher section architecture and workflows: [PHASE_2_TEACHER_SECTION_PLAN.md](./PHASE_2_TEACHER_SECTION_PLAN.md)
- Teacher implementation tracker: [PHASE_2_TEACHER_TRACKER.md](./PHASE_2_TEACHER_TRACKER.md)
- Teacher-only seeded validation flow: [TEACHER_TESTING_GUIDE.md](./TEACHER_TESTING_GUIDE.md)

## 1. Core Principle

Keep these responsibilities separate:

- `role` decides access
- `class` decides grouping and assignment scope
- `persona` decides how the tutor responds
- `knowledge base` decides what source material the tutor can use
- `session` decides which student interaction thread is active
- `dashboard` summarizes activity from the underlying learning tables

If those responsibilities blur together, the system becomes hard to reason about.

---

## 2. Entity Map

| Entity | Owned By | Created By | Used By | Primary Tables / Routes |
|---|---|---|---|---|
| Identity | auth layer | local auth / future main site | all roles | `tutor_users`, `/api/me`, `/api/local-auth/*` |
| Role / RBAC | auth layer | auth sync | routers, frontend gating | `role`, `rbac.py` |
| Class | teacher/admin | teacher/admin | teacher dashboard, student class context, KB assignment | `classes`, `/api/teacher/classes` |
| Enrollment | classroom layer | teacher/admin | student class access, teacher roster | `class_enrollments` |
| Tutor Persona | tutor config layer | seeded/custom teacher/admin | sessions, chat UX | `tutor_personas`, `/api/experts` |
| Session | student | student | chat, hints, quizzes, flashcards | `tutor_sessions`, `/api/tutor/sessions` |
| Messages | student session | chat flow | history, teacher activity metrics | `tutor_messages`, `/api/expert-chat*` |
| Knowledge Base | teacher/admin | teacher/admin | assigned class tutoring | `knowledge_bases`, `/api/teacher/kb` |
| KB Documents | teacher/admin | teacher/admin | retrieval pipeline | `kb_documents` |
| KB Chunks | KB pipeline | document processing | RAG retrieval | `kb_chunks` |
| KB Assignment | classroom + KB bridge | teacher/admin | student class materials, chat retrieval | `kb_class_assignments`, `/api/teacher/kb/{kb_id}/assignments` |
| Hint Progression | student | student | hint workflow | `hint_progressions` |
| Quiz Attempt | student | student | quiz workflow, mastery | `adaptive_quiz_attempts` |
| Flashcards | student | student | revision workflow | `flashcard_decks`, `flashcards` |
| Mastery | derived learning state | quiz/mastery logic | student + teacher dashboards | `student_mastery` |
| Misconceptions | derived learning state | quiz explanation flow | student + teacher dashboards | `misconception_log` |
| Student Dashboard | reporting layer | derived | student | `/api/tutor/progress/student` |
| Teacher Dashboard | reporting layer | derived | teacher/admin | `/api/tutor/progress/teacher` |

---

## 3. Relationship Diagram

```text
tutor_users
  -> one role per actor

teacher/admin
  -> owns classes
  -> owns knowledge_bases

classes
  -> has many class_enrollments
  -> has many assigned knowledge_bases through kb_class_assignments

student
  -> belongs to classes through class_enrollments
  -> has many tutor_sessions
  -> has many learning records

tutor_sessions
  -> belongs to one student
  -> uses one tutor_persona
  -> may belong to one class context

tutor_messages
  -> belongs to one session
  -> may reference one KB used during chat

knowledge_bases
  -> owned by teacher/admin
  -> has many documents
  -> has many chunks
  -> assigned to classes
```

### Visual Ecosystem Diagram

```mermaid
flowchart TD
  A[Login / Auth] --> B[tutor_users + role]

  B --> C[Teacher/Admin]
  B --> D[Student]
  B --> E[Parent Future]

  C --> F[Create Class]
  F --> G[classes]
  C --> H[Enroll Students]
  H --> I[class_enrollments]
  C --> J[Create Knowledge Base]
  J --> K[knowledge_bases]
  C --> L[Upload Documents]
  L --> M[kb_documents]
  C --> N[Process Documents]
  N --> O[kb_chunks]
  C --> P[Assign KB to Class]
  P --> Q[kb_class_assignments]

  D --> R[Open My Class Context]
  R --> S[See enrolled classes]
  R --> T[See assigned materials]

  D --> U[Pick Tutor Persona]
  U --> V[tutor_personas]
  D --> W[Start Session]
  W --> X[tutor_sessions]
  X --> Y[Session carries class context]

  D --> Z[Chat / Hint / Quiz / Flashcards]
  Z --> AA[tutor_messages]
  Z --> AB[hint_progressions]
  Z --> AC[adaptive_quiz_attempts]
  Z --> AD[flashcard_decks + flashcards]

  Y --> AE[Use class-assigned KBs in chat]
  Q --> AE
  O --> AE

  Z --> AF[student_mastery]
  Z --> AG[misconception_log]
  Z --> AH[mistake_journal]

  AF --> AI[Student Dashboard]
  AG --> AI
  AA --> AJ[Teacher Dashboard]
  AC --> AJ
  AF --> AJ
  AG --> AJ
  Q --> AJ
```

### Runtime Meaning Diagram

```mermaid
flowchart LR
  A[Class] -->|organizes| B[Students]
  A -->|receives| C[Assigned KBs]
  B -->|starts| D[Session]
  D -->|uses| E[Persona / Expert]
  D -->|uses| C
  D -->|produces| F[Messages]
  D -->|produces| G[Hints / Quizzes / Flashcards]
  G -->|updates| H[Mastery / Misconceptions]
  B -->|sees| I[Student Dashboard]
  A -->|scopes| J[Teacher Dashboard]
```

---

## 4. Who Creates What

### Teacher/Admin creates

- class
- class roster
- KB
- KB documents
- KB processing
- KB-to-class assignment

### Student creates

- session
- messages
- hint progressions
- quiz attempts
- flashcard decks and cards
- derived mastery and misconception signals

### Teacher/Admin reads

- class roster
- assigned class materials
- class-level activity summary
- student-level progress summary

---

## 5. End-to-End Operational Flow

### Step 1: Identity

- user logs in
- user is synced to `tutor_users`
- role is resolved locally

### Step 2: Classroom Setup

- teacher creates class
- teacher enrolls student
- teacher creates KB
- teacher uploads and processes docs
- teacher assigns KB to class

### Step 3: Student Context

- student opens tutor app
- student sees `My Class Context`
- student sees enrolled classes
- student sees assigned materials for selected class

### Step 4: Session Start

- student chooses tutor persona
- student starts session with selected class context
- session persists `class_id`

### Step 5: Learning Loop

- student chats / requests hints / runs quiz / generates flashcards
- chat can use assigned KB context from class
- message history persists
- KB-backed messages persist KB usage

### Step 6: Reporting

- student dashboard reads student-owned activity
- teacher dashboard reads class-scoped student activity
- teacher can see active students, session/message volume, and KB-backed activity

### Sequence Workflow

```mermaid
sequenceDiagram
  participant T as Teacher/Admin
  participant S as Student
  participant FE as Frontend
  participant API as Tutor Backend
  participant DB as Tutor DB
  participant AI as Persona + RAG

  T->>FE: Login
  FE->>API: local auth / api/me
  API->>DB: sync tutor_user

  T->>FE: Create class
  FE->>API: POST /api/teacher/classes
  API->>DB: insert classes

  T->>FE: Enroll student
  FE->>API: POST /api/teacher/classes/{class_id}/enroll
  API->>DB: insert class_enrollments

  T->>FE: Create KB + upload + process
  FE->>API: /api/teacher/kb*
  API->>DB: insert knowledge_bases / kb_documents / kb_chunks

  T->>FE: Assign KB to class
  FE->>API: POST /api/teacher/kb/{kb_id}/assignments
  API->>DB: insert kb_class_assignments

  S->>FE: Login
  FE->>API: local auth / api/me
  API->>DB: sync tutor_user

  S->>FE: Open My Class Context
  FE->>API: GET /api/tutor/classes
  API->>DB: load enrollments + assigned KBs
  API->>FE: classes + assigned materials

  S->>FE: Pick persona and start session
  FE->>API: POST /api/tutor/sessions
  API->>DB: insert tutor_sessions with class_id

  S->>FE: Chat / Hint / Quiz / Flashcards
  FE->>API: tutor endpoints
  API->>DB: load session + class context
  API->>AI: persona prompt + KB retrieval
  API->>DB: save messages + learning data

  S->>FE: Open student dashboard
  FE->>API: GET /api/tutor/progress/student
  API->>DB: aggregate student activity

  T->>FE: Open teacher dashboard
  FE->>API: GET /api/tutor/progress/teacher?class_id=...
  API->>DB: aggregate class activity + KB-backed usage
```

### Plain Text Workflow

```text
Teacher/Admin
  -> login
  -> create class
  -> enroll student
  -> create KB
  -> upload docs
  -> process docs into chunks
  -> assign KB to class

Student
  -> login
  -> open My Class Context
  -> select class
  -> see assigned materials
  -> pick tutor persona
  -> start session
  -> chat / hint / quiz / flashcards
  -> generate mastery / misconception data
  -> view student dashboard

Teacher/Admin
  -> open class dashboard
  -> see roster
  -> see active students
  -> see message/session counts
  -> see KB-backed usage
  -> see mastery / quiz / misconception trends
```

---

## 6. Canonical Runtime Meaning

### Class

Class is not the owner of student learning records.

Class is the scope for:

- roster
- assigned materials
- session context
- teacher dashboard aggregation

### Persona / Expert

Persona is not a classroom teacher.

Persona is the tutor identity that controls:

- explanation style
- teaching tone
- pedagogical framing
- subject emphasis

### Knowledge Base

KB is not a class by itself.

KB is a teacher-owned content set that becomes useful to students only after assignment or explicit access.

---

## 7. What Frontend Should Communicate Clearly

Student should understand:

- which class is currently active
- which materials are assigned to that class
- which tutor persona is active
- whether tutor output is grounded in KB sources

Teacher should understand:

- which class is selected
- which students are enrolled
- which KBs are assigned to that class
- which student activity came from classroom usage

---

## 8. Required Invariants

These rules should remain true:

1. Every learning record belongs to a student.
2. Every teacher dashboard view is scoped by class.
3. Every class-assigned KB is visible from the classroom context.
4. Every session may carry class context.
5. Every KB-backed chat can be reported as KB-backed usage.
6. Personas remain separate from classes and KBs.

---

## 9. Current Implemented Ecosystem Links

- local role login and tutor user sync
- teacher class CRUD + enrollment
- KB CRUD + processing
- KB-to-class assignment routes
- student class listing with assigned materials
- class-aware session creation
- class-aware KB retrieval during chat
- citation display in tutor workspace
- expanded teacher dashboard activity metrics

Teacher planning follow-up:

- use [PHASE_2_TEACHER_SECTION_PLAN.md](./PHASE_2_TEACHER_SECTION_PLAN.md) for the granular teacher workflows, role-scope model, and student-profile handoff points
- use [PHASE_2_TEACHER_TRACKER.md](./PHASE_2_TEACHER_TRACKER.md) for execution order, status, and validation requirements

---

## 10. Remaining Non-Goals For This Phase

These may still be deferred:

- parent-specific UX
- student self-join by invite code
- class-scoped assignments/homework products
- parent dashboard
- advanced teacher analytics beyond current class metrics
