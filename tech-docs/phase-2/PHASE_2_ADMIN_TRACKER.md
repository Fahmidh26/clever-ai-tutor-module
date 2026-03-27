# Phase 2 Admin Section Tracker

> Date: 2026-03-27
> Scope: Execution tracker for the admin/global-operator section inside the single RBAC-driven tutor app
> Canonical spec: [PHASE_2_ADMIN_SECTION_PLAN.md](./PHASE_2_ADMIN_SECTION_PLAN.md)

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

Every admin workstream must be completed in this order:

1. backend or data changes
2. frontend wiring in the same app shell
3. automated validation
4. browser workflow validation
5. checklist/doc update

No admin task is complete until role-boundary testing is also verified.

---

## 3. Workstream Tracker

## 3.1 Single-App Shell + RBAC Routing

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Admin lands in role-specific dashboard inside the same app shell | `Done` | `/api/me`, frontend RBAC gating | Browser smoke | No separate admin app/portal |
| Admin is the only global role | `Done` | RBAC rules | API + browser | Canonical architecture rule |
| Teacher remains teacher-scoped rather than admin-global | `Done` | roster/class scope rules | API checks | Teacher does not inherit global visibility |
| Parent remains linked-child scoped | `Planned` | parent role workflows | Route/API smoke later | Parent product surface still scaffolded |

## 3.2 Role Management

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Admin local role exists in local auth and tutor role resolution | `Done` | local auth config, tutor sync | API + browser | `admin@local.dev` exists |
| Admin can inspect role-based behavior through `/api/me` and frontend gating | `Done` | auth/session contract | Browser | Current role resolution works |
| Dedicated admin role promotion endpoint | `Planned` | admin route design | API + browser | Needed for true admin governance |
| Dedicated admin user inventory view | `Planned` | admin route + UI design | API + browser | Not implemented yet |

## 3.3 Global Class Oversight

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Admin can access class management routes already shared with teacher scope | `Done` | teacher/admin RBAC | API + browser | Current repo behavior |
| Dedicated admin class inventory across all teachers | `Planned` | admin global query layer | API + browser | Not implemented yet |
| Class enrollment repair tooling | `Planned` | admin governance routes | API + browser | Future admin-specific scope |

## 3.4 Global KB Oversight

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Admin can access teacher KB management routes through RBAC | `Done` | teacher/admin RBAC | API + browser | Current repo behavior |
| Dedicated admin KB inventory and ownership inspection | `Planned` | admin route design | API + browser | Not implemented yet |
| KB assignment governance and orphan detection | `Planned` | admin analytics/governance routes | API + browser | Future global oversight |

## 3.5 Global Analytics Visibility

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Admin can access teacher analytics routes through current RBAC | `Done` | teacher analytics routes | API + browser | Current elevated visibility path |
| Dedicated admin global analytics dashboard | `Planned` | global aggregation queries | API + browser | Not implemented yet |
| Cross-class anomaly detection | `Planned` | governance analytics | API + browser | Future admin scope |

## 3.6 Boundary Enforcement

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Teacher cannot perform admin-global actions | `Planned` | dedicated admin routes | API negative checks | Must be validated once admin routes exist |
| Admin can inspect teacher/student/parent structures without changing ownership semantics | `Planned` | admin route design | API + doc review | Spec locked now, implementation later |
| Student remains self-scoped under admin-governed system | `Done` | student scope rules | API + browser | Existing invariant |
| Parent remains non-global and support-oriented | `Planned` | parent role implementation | Doc review + future API checks | Must remain true |

## 3.7 Governance / Audit Surfaces

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Admin governance spec exists | `Done` | documentation | Doc review | Locked in section plan |
| Dedicated audit log surface | `Planned` | future compliance work | API + browser | Likely Phase 3.7 aligned |
| Relationship repair tooling | `Planned` | admin repair route design | API + browser | Not implemented yet |

## 3.8 Testing Coverage

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Static validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | lint, compile, link sanity |
| API validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | RBAC + admin flow checks |
| Browser validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | Mandatory for admin changes |
| RBAC role-routing Playwright smoke test | `Blocked` | mocked auth harness | `npm run e2e:list` passes; authenticated shell still blocked in current mocked-browser setup | Existing repo limitation |
| Real backend admin elevated-access pass | `Planned` | seeded admin workflow | Full e2e run | Use local admin account |

## 3.9 Documentation Alignment

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Admin section plan doc exists | `Done` | none | Doc review | Canonical admin planning spec |
| Admin tracker doc exists | `Done` | none | Doc review | This file |
| Shared phase docs reference admin plan/tracker | `Done` | doc update | Link check | Cross-role consistency |
| Progress checklist references admin doc pack | `Done` | doc update | Link check | Global-role docs visible from one place |

---

## 4. Recommended Execution Order

1. lock admin as the only global role in docs and RBAC understanding
2. add explicit admin role management and user inventory
3. add dedicated global class and KB oversight surfaces
4. add dedicated global analytics and governance repair tools
5. validate negative checks proving teacher cannot perform admin-global actions

---

## 5. Validation Checklist For Future Implementers

- `cmd /c npm run lint` in `frontend`
- `python -m compileall backend/app`
- targeted API verification for changed admin endpoints
- browser validation of the exact admin flow touched
- explicit RBAC check that teacher cannot use admin-global routes
- docs updated if workflow, route contract, or governance rule changes

---

## 6. Current Implementation Snapshot

Implemented now:

- single app shell with admin role resolution
- admin local-dev account and frontend role routing
- admin access to current teacher/admin shared routes through RBAC

Remaining implementation gap:

- dedicated admin global workspace
- dedicated admin route groups
- explicit role promotion, relationship repair, and audit tooling
- authenticated-shell Playwright coverage still blocked by current mocked-browser auth harness issue
