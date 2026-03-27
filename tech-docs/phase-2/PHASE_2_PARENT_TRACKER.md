# Phase 2 Parent Section Tracker

> Date: 2026-03-27
> Scope: Execution tracker for the parent/guardian section inside the single RBAC-driven tutor app
> Canonical spec: [PHASE_2_PARENT_SECTION_PLAN.md](./PHASE_2_PARENT_SECTION_PLAN.md)

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

Every parent workstream must be completed in this order:

1. backend or data changes
2. frontend wiring in the same app shell
3. automated validation
4. browser workflow validation
5. checklist/doc update

No parent task is complete until role-boundary testing is also verified.

---

## 3. Workstream Tracker

## 3.1 Single-App Shell + RBAC Routing

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Parent lands in role-specific dashboard inside the same app shell | `Planned` | `/api/me`, frontend RBAC gating | Browser smoke later | Role exists, dedicated parent workspace still minimal |
| Parent role resolves through local auth and tutor RBAC | `Done` | local auth config, role resolver | API + browser | `parent@local.dev` exists |
| Parent remains linked-child scoped rather than teacher/admin scoped | `Planned` | parent route design | API + browser later | Canonical boundary rule |
| Admin remains the only global role | `Done` | RBAC rules | API + doc review | Parent must never become global |

## 3.2 Child-Link Visibility

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Parent-child link model documented | `Done` | documentation | Doc review | Canonical link rule locked |
| Parent-linked child list route | `Planned` | `parent_student_links`, parent route design | API + browser | Not implemented yet |
| Empty-state guidance when no child is linked | `Planned` | parent UX design | Browser | Important first-run parent behavior |

## 3.3 Child Progress Read Access

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Parent child overview view | `Planned` | parent linked-child routes | API + browser | Not implemented yet |
| Parent child progress summary | `Planned` | progress read model for parent | API + browser | Not implemented yet |
| Parent-readable mastery and misconception summaries | `Planned` | parent view contracts | API + browser | Should remain summary-oriented |
| Parent cannot access unrelated student detail | `Planned` | parent RBAC and scope filters | API negative checks | Critical boundary rule |

## 3.4 Reports / Summary Access

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Teacher parent-summary draft concept exists | `Done` | teacher reports contract | API + browser | Draft-only teacher-side concept implemented |
| Parent-facing report retrieval route | `Planned` | parent route design | API + browser | Not implemented yet |
| Parent summary consumption flow | `Planned` | parent UI + report contract | Browser | Not implemented yet |

## 3.5 Controls And Support Surfaces

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Parent control surfaces documented as future linked-child features | `Done` | documentation | Doc review | Keep scoped to child support |
| Content or quiet-hour controls | `Blocked` | future product scope | API + browser later | Better aligned with Phase 3 parent work |
| Co-learning and teacher communication surfaces | `Blocked` | future product scope | API + browser later | Documented as future handoff only |

## 3.6 Boundary Protection

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Parent cannot access teacher roster or class management | `Planned` | parent RBAC checks | API negative checks | Must be validated once parent UI is active |
| Parent cannot access admin-global tools | `Planned` | admin route separation | API negative checks | Must remain true |
| Parent remains read-heavy and support-oriented | `Done` | documentation | Doc review | Canonical boundary rule |

## 3.7 Testing Coverage

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Static validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | lint, compile, link sanity |
| API validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | RBAC + parent flow checks |
| Browser validation workflow documented in `AGENTS.md` | `Done` | agent rules update | Doc review | Mandatory for parent changes |
| Parent role-routing smoke coverage | `Blocked` | mocked auth harness + parent shell | `npm run e2e:list` passes; authenticated shell issue still blocks broad role smoke confidence | Same repo limitation |
| Real backend parent pass | `Planned` | seeded linked-child data | Full e2e run | Requires deterministic parent-child links or seed updates |

## 3.8 Documentation Alignment

| Item | Status | Dependencies | Validation | Notes |
|---|---|---|---|---|
| Parent section plan doc exists | `Done` | none | Doc review | Canonical parent planning spec |
| Parent tracker doc exists | `Done` | none | Doc review | This file |
| Shared phase docs reference parent plan/tracker | `Done` | doc update | Link check | Cross-role consistency |
| Progress checklist references parent doc pack | `Done` | doc update | Link check | Parent docs visible from one place |

---

## 4. Recommended Execution Order

1. lock linked-child scope boundaries
2. add deterministic parent-child read model
3. add parent overview and progress summary surfaces
4. add parent-facing report and teacher handoff consumption
5. add future controls and communications only after core linked-child visibility is correct

---

## 5. Validation Checklist For Future Implementers

- `cmd /c npm run lint` in `frontend`
- `python -m compileall backend/app`
- targeted API verification for changed parent endpoints
- browser validation of the exact parent flow touched
- explicit RBAC check that parent cannot access unrelated students or teacher/admin-only routes
- docs updated if workflow, route contract, or boundary rules change

---

## 6. Current Implementation Snapshot

Implemented now:

- single app shell with parent role available in local auth and role resolution
- parent role is part of RBAC vocabulary
- teacher reports mention parent handoff draft concepts

Remaining implementation gap:

- linked-child parent routes and UI
- parent progress and report surfaces
- parent control and communication surfaces
- deterministic seeded parent-child browser validation path
