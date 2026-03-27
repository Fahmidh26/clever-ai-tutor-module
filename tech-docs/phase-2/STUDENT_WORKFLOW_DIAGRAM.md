# Student Workflow Diagram

> Date: 2026-03-27
> Scope: Detailed student flow inside the single tutor app shell
> Purpose: Show what the student should start with first, what depends on what, and how the full student experience should flow in practice

---

## 1. Start Order

Use this order when testing or demonstrating the student workflow:

1. student login and role landing
2. student class context review
3. class selection or no-class fallback
4. persona selection
5. session start or session resume
6. tutor chat
7. hints, quizzes, or flashcards
8. mastery and misconception review
9. student dashboard review
10. teacher read-side verification later if needed

This order matters because:

- assigned materials are easier to reason about after class context loads
- session behavior is clearer after persona and class context are chosen
- dashboard and progress review are not meaningful before activity exists
- teacher monitoring should be checked only after student-owned activity is created

---

## 2. High-Level Flow

```mermaid
flowchart TD
    A[Student Logs In] --> B[Role Resolves To Student]
    B --> C[Student Lands In Single App Shell]

    C --> D[Open My Class Context]
    D --> E{Has Enrolled Class?}
    E -->|Yes| F[Select Active Class]
    E -->|No| G[Continue Without Class Or Join By Invite]

    F --> H[Load Assigned KBs]
    F --> I[Load Class Persona Defaults]
    G --> J[Use General Tutor Context]

    H --> K[Choose Persona]
    I --> K
    J --> K

    K --> L[Open Or Create Session]
    L --> M[Ask Question / Start Learning]
    M --> N[Persist Messages]
    M --> O[Use Hints / Quiz / Flashcards]

    O --> P[Mastery Updates]
    O --> Q[Misconception Updates]
    N --> R[Session History]
    P --> S[Student Dashboard]
    Q --> S
    R --> S
```

---

## 3. Detailed Student Workflow

### Phase A. Student Identity And Landing

Student starts here first.

```mermaid
sequenceDiagram
    participant S as Student
    participant FE as Frontend
    participant API as Backend
    participant DB as Tutor DB

    S->>FE: Open app
    S->>FE: Login with student account
    FE->>API: GET /api/me
    API->>DB: Resolve tutor user and role
    DB-->>API: role=student
    API-->>FE: student session payload
    FE-->>S: Student shell + student workspace
```

Expected result:

- student is inside the same app shell as everyone else
- student sees tutor workspace and student progress surfaces
- teacher/admin controls are not the primary workspace

What to verify first:

- login succeeds
- role resolves to `student`
- student sees self-scoped workspace controls

---

### Phase B. Class Context

Student should load class context before interpreting assigned materials.

```mermaid
flowchart LR
    A[Student Home] --> B[Open My Class Context]
    B --> C{Enrolled Class Exists?}
    C -->|Yes| D[Select Class]
    C -->|No| E[Show Empty State Or Join Option]
    D --> F[Load Assigned Materials]
    D --> G[Load Class Persona Defaults]
```

Why this comes early:

- assigned KBs depend on class context
- class persona defaults depend on class context
- session context is clearer after class selection

Student actions:

1. open `My Class Context`
2. select an enrolled class if one exists
3. review assigned materials
4. note whether a class persona default exists

Outputs:

- active class context
- assigned materials view
- class tutor defaults view

---

### Phase C. Persona And Session Setup

Student chooses how tutoring starts.

```mermaid
flowchart TD
    A[Student Context Ready] --> B[Choose Persona]
    B --> C[Create Or Resume Session]
    C --> D[Session Carries Persona]
    C --> E[Session May Carry Class Context]
```

Student actions:

1. choose a tutor persona
2. create a new session or resume an existing one
3. confirm class-aware context if using a class
4. confirm active tutoring mode

Important rules:

- session remains student-owned
- class defaults can influence tutoring style
- student still owns resulting session and messages

Outputs:

- active session
- selected persona
- optional class-scoped tutoring context

---

### Phase D. Tutor Chat

Student now starts the real tutoring loop.

```mermaid
sequenceDiagram
    participant S as Student
    participant FE as Frontend
    participant API as Backend
    participant DB as Tutor DB
    participant AI as LLM + Retrieval

    S->>FE: Send message
    FE->>API: POST /api/expert-chat or /api/expert-chat/stream
    API->>DB: Load session + class context
    API->>AI: Apply persona + KB retrieval if assigned
    API->>DB: Save tutor_messages
    API-->>FE: Tutor response + citations when available
```

Student actions:

1. ask a question
2. review citations when class KBs are assigned
3. continue the conversation
4. confirm history persists in session

Outputs:

- saved messages
- KB-backed response when available
- reusable session history

---

### Phase E. Learning Tools

Student should now use the supporting learning tools.

```mermaid
flowchart LR
    A[Student Session] --> B[Hint Mode]
    A --> C[Quiz Mode]
    A --> D[Flashcards Mode]
    B --> E[Hint progression state]
    C --> F[Quiz attempts + explain-my-answer]
    D --> G[Decks + review schedule]
```

Student actions:

1. start a hint progression
2. run a quiz
3. use `Explain My Answer`
4. generate or review flashcards

Outputs:

- hint records
- quiz records
- mistake and misconception signals
- flashcard review records

---

### Phase F. Dashboard And Review

Student reviews the learning result after activity exists.

```mermaid
flowchart TD
    A[Student Activity Exists] --> B[Open Student Dashboard]
    B --> C[Review session and message counts]
    B --> D[Review mastery]
    B --> E[Review misconceptions]
    B --> F[Review flashcard due items]
```

Student actions:

1. open dashboard
2. review mastery changes
3. review misconceptions
4. decide whether to resume a session or review flashcards

Outputs:

- student-owned progress summary
- next-action review loop

---

## 4. Recommended Real Testing Path

If you want the most realistic student test sequence, do it in exactly this order:

```mermaid
flowchart TD
    A[Login As Student] --> B[Open My Class Context]
    B --> C{Has Class?}
    C -->|Yes| D[Select Class And Review Materials]
    C -->|No| E[Use Empty State Or Join By Invite]
    D --> F[Choose Persona]
    E --> F
    F --> G[Create Or Resume Session]
    G --> H[Run Tutor Chat]
    H --> I[Use Hint Or Quiz]
    I --> J[Review Flashcards]
    J --> K[Open Student Dashboard]
    K --> L[Verify Mastery And Misconceptions]
```

---

## 5. Quick Decision Rules

When unsure what comes first:

- if login fails, stop at role resolution first
- if no class exists, use empty-state tutoring or join by invite before testing assigned materials
- if no session exists, create one before testing chat or learning tools
- if no activity exists, do not test dashboard depth yet
- if no KB is assigned, expect general tutoring rather than citation-backed class tutoring

---

## 6. Expected Student Mental Model

The student workflow should feel like this:

1. understand my current class context
2. choose how I want the tutor to help me
3. start or resume learning
4. use chat and learning tools
5. review my own progress
6. decide what to study next

That is the intended student flow for both implementation and testing.
