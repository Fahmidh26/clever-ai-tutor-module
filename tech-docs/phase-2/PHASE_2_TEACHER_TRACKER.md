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
| Teacher cannot browse unrelated students globally | `Planned` | roster handshake APIs | RBAC API tests | Must stay explicit in future implementation |

## 3.2 Teacher Roster + Join Handshake

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Define teacher roster as separate from class roster | `Planned` | schema and route design | Spec/doc review | Needed before class placement rules |
| Teacher join code / invite flow | `Planned` | roster schema | API + browser | Supports explicit teacher-student linkage |
| Pending join request approval flow | `Planned` | join request model | API + browser | Teacher approval gates visibility |
| Auto-link teacher when student joins by class code | `Planned` | class join flow | API + browser | Hybrid join model |
| Unassigned linked-student queue | `Planned` | teacher roster model | Browser + dashboard | Student linked but not yet in a class |

## 3.3 Class Management

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Teacher create/list/select class | `Done` | `classes`, `/api/teacher/classes` | Browser + API | Existing class manager flow |
| Manual enrollment from teacher-managed list | `Done` | `class_enrollments` | Browser + API | Currently by student id |
| Class invite code scaffold | `Planned` | class invite schema | API + browser | Needed for self-join |
| Bulk import scaffold | `Planned` | roster pipeline | Browser + file contract | Defer execution details |
| Teacher class cockpit as primary workspace | `Planned` | dashboard composition | Browser | Preferred UX direction |

## 3.4 Knowledge Base + Assignment

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Teacher KB create/list/delete | `Done` | `/api/teacher/kb*` | Browser + API | Existing |
| KB document upload/process/preview | `Done` | ingestion pipeline | Browser + API | Existing |
| KB-to-class assignment | `Done` | `kb_class_assignments` | Browser + API | Existing assignment workflow |
| Student sees class-assigned materials | `Done` | student classes API, KB assignment | Browser | Exposed in `My Class Context` |
| KB-backed chat usage appears in teacher metrics | `Done` | message KB linkage | API + browser | Included in teacher summary |
| Teacher "test your tutor" KB preview | `Planned` | preview chat UX | Browser | Recommended next refinement |

## 3.5 Persona / Tutor Policy

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Explain personas as tutor styles, not classroom teachers | `Done` | frontend copy | Browser | Already surfaced in UI |
| Persona selection in student tutoring flow | `Done` | `/api/experts` | Browser | Existing |
| Teacher-assigned persona defaults per class | `Planned` | persona policy routes/schema | API + browser | Important next teacher control |
| Persona preview / teacher overlay instructions | `Planned` | teacher persona management | API + browser | Co-pilot/teaching policy bridge |

## 3.6 Monitoring + Session Replay

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Teacher class summary metrics in dashboard | `Done` | progress router | Browser + API | Includes sessions/messages/KB counts |
| Student summary remains student-owned view | `Done` | student progress router | Browser | Same app shell, different scope |
| Active/inactive student queue | `Planned` | analytics thresholds | API + browser | Define threshold rules |
| Session replay viewer | `Planned` | read-only session detail access | API + browser | High-value teacher feature |
| Evidence-backed at-risk queue | `Planned` | analytics + rubric | API + browser | Needed before parent handoff |

## 3.7 Reports + Co-Pilot

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Class report object definition | `Planned` | reporting contract | API contract tests | Supports exports and parent handoff |
| Student summary object for teacher | `Planned` | analytics contract | API contract tests | Evidence-backed only |
| Parent summary draft scaffold | `Planned` | reporting contract | API + browser | Teacher-reviewed drafts only |
| Worksheet / intervention co-pilot drafts | `Planned` | teacher copilot endpoints | API + browser | Draft-only, no auto-mutation |

## 3.8 Testing Coverage

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Static validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | lint, compile, link sanity |
| API validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | RBAC + teacher flow checks |
| Browser validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | Mandatory for teacher changes |
| Teacher dashboard Playwright smoke test | `Blocked` | mocked API routes | `npm run e2e:list` passes; browser run currently blocked by existing auth-fetch harness issue | Spec scaffold added |
| RBAC role-routing Playwright smoke test | `Blocked` | mocked API routes | `npm run e2e:list` passes; browser run currently blocked by existing auth-fetch harness issue | Spec scaffold added |
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
- teacher class management
- KB management and class assignment
- student class context and assigned materials
- class-aware sessions and KB-backed chat linkage
- richer teacher dashboard metrics
- tutor persona copy clarified in the UI

Planned next:

- teacher roster handshake
- teacher/class invite codes
- unassigned student queue
- class-level persona policy
- teacher session replay
- evidence-backed at-risk queue
- parent summary draft outputs
