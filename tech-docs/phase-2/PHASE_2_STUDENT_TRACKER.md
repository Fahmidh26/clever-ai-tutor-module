# Phase 2 Student Section Tracker

> Date: 2026-03-27
> Scope: Execution tracker for the student/learner section inside the single RBAC-driven tutor app
> Canonical spec: [PHASE_2_STUDENT_SECTION_PLAN.md](./PHASE_2_STUDENT_SECTION_PLAN.md)

---

## 1. Status Legend

| Status | Meaning |
|---|---|
| `Not Started` | No implementation or validation work has begun |
| `Planned` | Scope and dependencies are defined |
| `In Progress` | Work is actively being implemented |
| `Blocked` | Waiting on prerequisite schema, API, UX, or another workstream |
| `Done` | Implemented and validated against the required checks |

---

## 2. Delivery Rule

Every student workstream must be completed in this order:

1. backend or data changes
2. frontend wiring in the same app shell
3. automated validation
4. browser workflow validation
5. checklist/doc update

No student task is complete until role-boundary testing is also verified.

---

## 3. Workstream Tracker

## 3.1 Single-App Shell + RBAC Routing

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Student lands in role-specific dashboard inside the same app shell | `Done` | `/api/me`, frontend RBAC gating | Browser smoke | No separate student app/portal |
| Teacher lands in teacher workspace inside the same shell | `Done` | `/api/me`, frontend RBAC gating | Browser smoke | Teacher remains scoped to linked/enrolled students |
| Parent role remains scaffolded in the same shell | `Planned` | parent plan later | Route/API smoke later | Keep inside same product shell |
| Admin retains global role access inside the same shell | `Done` | RBAC checks | Browser/API smoke | Admin is the only global role |
| Student cannot browse unrelated students or teacher/admin global tools | `Done` | RBAC + self-scope queries | API + browser | Student remains self-scoped |

## 3.2 Student Class Context

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Student sees enrolled classes in `My Class Context` | `Done` | `class_enrollments`, `/api/tutor/classes` | API + browser | Existing class context panel |
| Student sees class-assigned KB/material summaries | `Done` | `kb_class_assignments` | API + browser | Existing assigned materials behavior |
| Student can join by class invite code | `Done` | `/api/tutor/classes/join` | API + browser | Auto-creates teacher link when required |
| Student sees active class as current tutoring context | `Done` | session + class UI state | Browser | Existing flow in tutor workspace |
| Empty-state guidance for no classes assigned | `Done` | frontend student shell | Browser | Student can still use tutor without class context |

## 3.3 Session Lifecycle

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Student create/list/open session | `Done` | `/api/tutor/sessions*` | API + browser | Existing |
| Persona selection in student tutoring flow | `Done` | `/api/experts` | Browser | Existing |
| Session mode switching | `Done` | `/api/tutor/modes`, session mode patch | API + browser | Existing |
| Session history panel | `Done` | session list/load flow | Browser | Existing |
| Session carries optional class context | `Done` | session payload, class context | API + browser | Existing class-aware tutoring flow |

## 3.4 Tutor Learning Loop

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Standard chat persistence | `Done` | `/api/expert-chat`, message persistence | API + browser | Existing |
| Streaming chat persistence | `Done` | `/api/expert-chat/stream` | API + browser | Existing SSE flow |
| Hint progression engine | `Done` | `hint_progressions` | API + browser | Three-level hint flow implemented |
| Adaptive quiz workflow | `Done` | `adaptive_quiz_attempts` | API + browser | Generate, submit, and explain path implemented |
| Flashcard generation and review | `Done` | flashcard tables + review logic | API + browser | Existing SM-2 baseline |

## 3.5 Dashboard + Progress Signals

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Student progress dashboard | `Done` | `/api/tutor/progress/student` | API + browser | Existing self-view summary |
| Mastery view | `Done` | `/api/tutor/mastery` | API + browser | Existing |
| Misconception review view | `Done` | `/api/tutor/misconceptions` | API + browser | Existing |
| Student metrics remain self-owned view | `Done` | progress aggregation rules | API + browser | Teacher reads scoped summaries later |
| Resume/review guidance from recent work | `Done` | frontend workspace state | Browser | Existing session and dashboard pairing |

## 3.6 KB-Backed Class Learning

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Student sees assigned KB-backed materials | `Done` | class assignment routes | Browser + API | Existing |
| Chat retrieval uses class-assigned KBs | `Done` | retrieval pipeline + class context | API + browser | Existing |
| Citation-backed tutor responses in student flow | `Done` | retrieval + response metadata | API + browser | Existing |
| Student can learn without KB when none assigned | `Done` | tutor base chat flow | Browser | Required fallback behavior |

## 3.7 Boundary Protection

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Student cannot access teacher roster or monitoring routes | `Done` | RBAC middleware | API checks | Teacher routes blocked for student |
| Student cannot inspect another student summary | `Done` | self-scope progress queries | API checks | Self-only semantics |
| Student activity remains the source for teacher read-side monitoring | `Done` | progress + analytics aggregation | Doc review + API review | Ownership preserved |
| Class configuration influences student experience without transferring ownership | `Done` | class context + persona policy | Browser + doc review | Existing model |

## 3.8 Testing Coverage

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Static validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | lint, compile, link sanity |
| API validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | RBAC + student flow checks |
| Browser validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | Mandatory for student changes |
| Tutor workspace Playwright smoke test | `Done` | existing mocked coverage | `npm run e2e:list` and repo spec presence | `frontend/e2e/tutor-workspace.spec.ts` exists |
| Role-routing Playwright smoke test for student gating | `Blocked` | mocked auth harness | `npm run e2e:list` passes; browser auth harness still blocks authenticated shell in current local setup | Same limitation as teacher smoke |
| Real backend student E2E sequence | `Done` | seeded local workflow | `cmd /c npm run e2e -- student-real-backend.spec.ts` | Added real local-dev login/browser pass covering class context, session/chat, quiz, and student dashboard |

## 3.9 Documentation Alignment

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Student section plan doc exists | `Done` | none | Doc review | Canonical student planning spec |
| Student tracker doc exists | `Done` | none | Doc review | This file |
| Shared phase docs reference student plan/tracker | `Done` | doc update | Link check | Cross-role consistency |
| Progress checklist references student doc pack | `Done` | doc update | Link check | Role packs visible from one place |

---

## 4. Recommended Execution Order

1. lock single-app role boundaries
2. stabilize student class context and empty states
3. stabilize session creation, history, and class-aware tutoring
4. validate hints, quiz, flashcards, mastery, and misconceptions as one student-owned loop
5. validate teacher read-side monitoring consumes student outputs without leaking student scope

---

## 5. Validation Checklist For Future Implementers

- `cmd /c npm run lint` in `frontend`
- `python -m compileall backend/app`
- targeted API verification for changed student endpoints
- browser validation of the exact student flow touched
- explicit RBAC check that student cannot access teacher/admin-only routes
- docs updated if workflow, route contract, or ownership rule changes

---

## 6. Current Implementation Snapshot

Implemented now:

- single app shell with role-driven UX
- student class context and class self-join
- student session lifecycle and persona selection
- chat, streaming, hints, quizzes, flashcards, mastery, and misconceptions
- student self-view dashboard and review surfaces
- class-aware KB retrieval and citations in tutor responses

Remaining validation gap:

- mocked-browser role-routing auth harness still does not enter the authenticated shell consistently in current local Playwright setup
