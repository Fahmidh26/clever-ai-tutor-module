# Phase 2 Teacher Section Tracker

> Date: 2026-03-26
> Scope: Execution tracker for the teacher/educator section inside the single RBAC-driven tutor app
> Canonical spec: [PHASE_2_TEACHER_SECTION_PLAN.md](./PHASE_2_TEACHER_SECTION_PLAN.md)

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

Every teacher workstream must be completed in this order:

1. backend or data changes
2. frontend wiring in the same app shell
3. automated validation
4. browser workflow validation
5. checklist/doc update

No teacher task is complete until role-boundary testing is also verified.

---

## 3. Workstream Tracker

## 3.1 Single-App Shell + RBAC Routing

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Teacher lands in role-specific dashboard inside the same app shell | `Done` | `/api/me`, frontend RBAC gating | Browser smoke | No separate teacher app/portal |
| Student lands in student workspace inside the same app shell | `Done` | `/api/me`, frontend RBAC gating | Browser smoke | Student remains self-scoped |
| Parent role remains scaffolded in the same shell | `Planned` | parent plan later | Route/API smoke later | Do not split to another app |
| Admin retains global role access inside the same shell | `Done` | RBAC checks | Browser/API smoke | Admin is the only global role |
| Teacher cannot browse unrelated students globally | `Done` | roster handshake APIs | RBAC API tests | Teacher analytics/replay now scope through links or teacher-owned classes |

## 3.2 Teacher Roster + Join Handshake

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Define teacher roster as separate from class roster | `Done` | schema and route design | API + doc review | Implemented via `teacher_student_links` and `/api/teacher/roster` |
| Teacher join code / invite flow | `Done` | roster schema | API + browser | `POST /api/teacher/join-codes` |
| Pending join request approval flow | `Done` | join request model | API + browser | Approve/reject endpoints implemented |
| Auto-link teacher when student joins by class code | `Done` | class join flow | API + browser | `POST /api/tutor/classes/join` ensures teacher link |
| Unassigned linked-student queue | `Done` | teacher roster model | Browser + dashboard | Exposed in teacher control center |

## 3.3 Class Management

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Teacher create/list/select class | `Done` | `classes`, `/api/teacher/classes` | Browser + API | Existing class manager flow |
| Manual enrollment from teacher-managed list | `Done` | `class_enrollments` | Browser + API | Currently by student id |
| Class invite code scaffold | `Done` | class invite schema | API + browser | Invite rotation endpoint and student join flow added |
| Bulk import scaffold | `Planned` | roster pipeline | Browser + file contract | Defer execution details |
| Teacher class cockpit as primary workspace | `Done` | dashboard composition | Browser | Teacher Control Center added inside app shell |

## 3.4 Knowledge Base + Assignment

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Teacher KB create/list/delete | `Done` | `/api/teacher/kb*` | Browser + API | Existing |
| KB document upload/process/preview | `Done` | ingestion pipeline | Browser + API | Existing |
| KB-to-class assignment | `Done` | `kb_class_assignments` | Browser + API | Existing assignment workflow |
| Student sees class-assigned materials | `Done` | student classes API, KB assignment | Browser | Exposed in `My Class Context` |
| KB-backed chat usage appears in teacher metrics | `Done` | message KB linkage | API + browser | Included in teacher summary |
| Teacher "test your tutor" KB preview | `Done` | preview chat UX | Browser | Persona preview plus KB-backed class policy validation now available in teacher shell |

## 3.5 Persona / Tutor Policy

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Explain personas as tutor styles, not classroom teachers | `Done` | frontend copy | Browser | Already surfaced in UI |
| Persona selection in student tutoring flow | `Done` | `/api/experts` | Browser | Existing |
| Teacher-assigned persona defaults per class | `Done` | persona policy routes/schema | API + browser | `/api/teacher/personas/classes/{id}` |
| Persona preview / teacher overlay instructions | `Done` | teacher persona management | API + browser | Preview endpoint and class overlay instructions implemented |

## 3.6 Monitoring + Session Replay

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Teacher class summary metrics in dashboard | `Done` | progress router | Browser + API | Includes sessions/messages/KB counts |
| Student summary remains student-owned view | `Done` | student progress router | Browser | Same app shell, different scope |
| Active/inactive student queue | `Done` | analytics thresholds | API + browser | Included in analytics + struggling queue |
| Session replay viewer | `Done` | read-only session detail access | API + browser | `/api/teacher/session-replay/{id}` plus teacher UI |
| Evidence-backed at-risk queue | `Done` | analytics + rubric | API + browser | `/api/teacher/analytics/struggling` |

## 3.7 Reports + Co-Pilot

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Class report object definition | `Done` | reporting contract | API contract tests | Stored in `teacher_reports` |
| Student summary object for teacher | `Done` | analytics contract | API contract tests | Student analytics endpoint added |
| Parent summary draft scaffold | `Done` | reporting contract | API + browser | Draft reports only |
| Worksheet / intervention co-pilot drafts | `Done` | teacher copilot endpoints | API + browser | Suggestion + worksheet draft endpoints added |

## 3.8.1 Assessments

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Teacher assessment list/create/detail | `Done` | `assessments`, `assessment_questions` | API + browser | `/api/teacher/assessments*` |
| Teacher question authoring | `Done` | assessment routes | API + browser | Simple question bank flow implemented |

## 3.8 Testing Coverage

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Static validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | lint, compile, link sanity |
| API validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | RBAC + teacher flow checks |
| Browser validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | Mandatory for teacher changes |
| Teacher dashboard Playwright smoke test | `Blocked` | mocked API routes | `npm run e2e:list` passes; browser run still blocked by local auth fetch harness issue in current frontend test setup | Spec exists but current mocked-browser run does not reach authenticated shell |
| RBAC role-routing Playwright smoke test | `Blocked` | mocked API routes | `npm run e2e:list` passes; browser run still blocked by local auth fetch harness issue in current frontend test setup | Spec exists but current mocked-browser run does not reach authenticated shell |
| Real backend teacher E2E sequence | `Planned` | stable seeded workflow | Full e2e run | Add when invite flow stabilizes |

## 3.9 Documentation Alignment

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Teacher section plan doc exists | `Done` | none | Doc review | Canonical teacher planning spec |
| Teacher tracker doc exists | `Done` | none | Doc review | This file |
| Ecosystem mapping references teacher plan/tracker | `Done` | doc update | Link check | Keeps one architecture source |
| Local-first phase plan references teacher plan/tracker | `Done` | doc update | Link check | Planning alignment |
| Progress checklist references teacher workstream | `Done` | doc update | Link check | Makes teacher phase visible |

---

## 4. Recommended Execution Order

1. lock single-app role boundaries
2. finish teacher roster + handshake model
3. refine class cockpit and invite/join flows
4. add class-level persona policy
5. add teacher monitoring drill-down and replay
6. add report objects and draft-only co-pilot outputs
7. add parent handoff interfaces without exposing raw teacher analytics

---

## 5. Validation Checklist For Future Implementers

- `cmd /c npm run lint` in `frontend`
- `python -m compileall backend/app`
- targeted API verification for changed teacher endpoints
- browser validation of the exact role flow touched
- explicit RBAC check that teacher cannot see unrelated students
- docs updated if workflow, route contract, or ownership rule changes

---

## 6. Current Implementation Snapshot

Implemented now:

- single app shell with role-driven UX
- teacher class management and class invite rotation
- teacher roster links, join codes, join requests, and unassigned queue
- KB management and class assignment
- student class context, class self-join, and auto-link handshake
- class-aware sessions and KB-backed chat linkage
- richer teacher dashboard metrics, student drill-down, struggling queue, and session replay
- class-level persona policy with preview + overlay instructions
- draft-only co-pilot suggestions, worksheet drafts, and stored report drafts
- teacher assessment authoring basics

Remaining validation gap:

- mocked-browser Playwright auth harness still does not enter the authenticated shell in current local setup, so browser automation is not fully green yet
