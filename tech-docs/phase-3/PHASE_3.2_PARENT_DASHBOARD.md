# Functional Phase 3.2: Parent Dashboard & Co-Learning

> **Status**: Not Started
> **Estimated Duration**: 2 weeks
> **Dependencies**: Phase 2 complete, `parent_student_links` table exists, RBAC parent role exists, FP 3.1 (gamification data for parent view)
> **Sprint Reference**: Sprint 3.2 in AI_TUTOR_MODULE.md (Section 22.2)
> **Priority**: P0 — High (parent engagement critical for K-8 users, COPPA requirement)

---

## 1. Executive Summary

The Parent Dashboard transforms parent involvement from passive observation to active co-learning. Parents get real-time visibility into their child's learning journey — mastery progress, study habits, streak engagement, and AI-generated summaries — with controls to set boundaries and communicate with teachers. The co-learning mode lets parents join sessions alongside their child, creating shared learning moments. This phase is also critical for COPPA compliance (under-13 parental consent).

---

## 2. Target Users and Personas

| User Type | Goals | How This Phase Serves Them |
|-----------|-------|---------------------------|
| **Parent (K-2 child)** | Monitor screen time, ensure safety, participate | Time controls, co-learning, activity feed, COPPA consent |
| **Parent (3-5 child)** | Track progress, help with homework, celebrate | Progress reports, conversation starters, badge visibility |
| **Parent (6-8 child)** | Ensure focus, communicate with teachers | Content controls, teacher messaging, alert system |
| **Parent (9-12 child)** | Light oversight, college prep awareness | High-level progress, test prep tracking, reduced controls |
| **Teacher** | Communicate with parents, share progress | Messaging, alert triggers, progress sharing |
| **Student** | Privacy-appropriate sharing with parents | Age-appropriate data visibility, co-learning partner |

---

## 3. Features and Sub-Features

### 3.2.1 Child Progress Overview — P0
- Multi-child dashboard with per-child drill-down
- Per-subject mastery radar chart (Math, Science, English, History, etc.)
- Time spent per subject per week (stacked bar chart)
- Session stats: total sessions, questions asked, hints used, quiz scores
- Standards mastery vs grade-level expectations (color-coded progress bars)
- Gamification summary: XP, level, streak, recent badges (from FP 3.1)
- Trend indicators: improving (↑), stable (→), needs attention (↓)
- **Acceptance Criteria**: Dashboard loads all linked children; per-child data accurate; charts render responsively; trend calculated from last 4 weeks

### 3.2.2 Activity Feed — P0
- Chronological daily log:
  - Topics studied + duration
  - Quiz scores and performance
  - Flashcard reviews completed
  - Streak updates (maintained, frozen, broken)
  - XP earned and badges received
  - Mastery level changes
- AI-generated daily summary (1-2 sentences, parent-friendly language):
  - "Alex studied fractions for 20 minutes and scored 85% on a quiz. Great progress!"
- Grouped by day with expandable detail
- Filterable by subject, date range
- **Acceptance Criteria**: Feed updates within 5 minutes of activity; AI summary generated daily; filter/search works; pagination for long history

### 3.2.3 Report Generation — P1
- Auto-generated reports:
  - Weekly snapshot (emailed Sunday evening)
  - Monthly detailed report (emailed 1st of month)
  - On-demand PDF download
- Report contents:
  - Mastery progress per subject (vs. grade expectations)
  - Time breakdown (heatmap of study hours)
  - Quiz performance trends
  - Strengths and areas for improvement (AI analysis)
  - Recommendations for parent support
- Standards-aligned: maps progress to Common Core / NGSS / state standards
- NO peer comparison (FERPA — never compare to other students)
- Email delivery: configurable schedule + manual trigger
- **Acceptance Criteria**: PDF renders cleanly; email delivery works; no PII of other students; standards mapping accurate

### 3.2.4 Content Controls — P0
- Subject/topic restrictions:
  - Block specific subjects (e.g., "no science for now")
  - Restrict to specific topics (e.g., "only fractions this week")
- Time limits:
  - Daily session time limit (15-120 minutes, configurable)
  - Weekly total time limit
  - Countdown warning at 5 minutes remaining
  - Hard stop when limit reached (save session, friendly message)
- Age-appropriate content level override:
  - Parent can set effective grade level (e.g., 8th grader working at 6th grade level)
- Mode blocking:
  - Disable specific interaction modes (e.g., no Debate mode for K-2)
- Quiet hours:
  - Set time ranges when the app is unavailable (e.g., 9PM-7AM)
  - Friendly "it's quiet time" screen during restricted hours
- **Acceptance Criteria**: Restrictions enforced server-side (not just UI); time limits count accurately; quiet hours block access; settings persist across sessions

### 3.2.5 COPPA Consent Flow — P0
- Required for ALL users under 13
- Consent flow:
  1. Student registers → detected as under-13 (by birthdate or grade)
  2. Account placed in "pending consent" state (limited access)
  3. Parent receives email/link with consent form
  4. Parent verifies identity (email confirmation + knowledge-based question)
  5. Parent grants consent → student account fully activated
- Consent management:
  - View current consent status
  - Revoke consent (deactivates child's account, preserves data for 30 days)
  - Renew consent (annual requirement)
  - Delete all child data (GDPR right to erasure)
- Consent record stored: parent_id, student_id, consent_type, timestamp, IP, evidence
- **Acceptance Criteria**: Under-13 users cannot access full app without consent; consent revocation deactivates within 1 hour; data deletion completes within 72 hours; audit trail maintained

### 3.2.6 Multi-Child Support — P0
- Parent links to multiple children
- Dashboard shows:
  - Child selector (sidebar on desktop, dropdown on mobile)
  - Per-child detail view
  - Aggregate family view: total family study time, combined achievements
- Add/remove child flow:
  - Parent invites child via email/code
  - Child confirms link (or auto-linked for under-13)
- **Acceptance Criteria**: Parent sees all linked children; switching is instant; aggregate stats calculate correctly; add/remove works

### 3.2.7 Co-Learning Mode — P1
- Parent joins child's active tutoring session
- Roles:
  - **Observer**: See messages in real-time (read-only)
  - **Participant**: Can type messages (AI acknowledges both users)
- Dual-audience AI responses:
  - AI detects co-learning mode and adjusts tone
  - Explains to child + provides parent context
  - Example: "Great question, Alex! *[For parent: This topic builds on the fraction basics we covered last week]*"
- Real-time sync via WebSocket:
  - Parent sees messages as they stream
  - Participant messages appear for both users
- Session indicator: Both users see "Co-Learning Active" badge
- **Acceptance Criteria**: Parent can join/leave without interrupting child; real-time message sync; dual-audience mode works; observer can't type; indicator visible to both

### 3.2.8 Parent Guide Sidebar — P2
- Context-aware tips panel:
  - "How to help with fractions without giving the answer"
  - "Questions to ask about today's science lesson"
  - "When to step back and let the AI tutor guide"
- Age-appropriate guidance:
  - K-2: "Sit with your child, read questions aloud, celebrate attempts"
  - 6-8: "Ask about what they learned, avoid looking at answers"
  - 9-12: "Check in weekly, discuss goals, respect independence"
- Subject-specific resources:
  - Links to parent-friendly explanations
  - Recommended activities for home practice
- **Acceptance Criteria**: Tips contextual to child's current subject/topic; age-band appropriate; refreshes when child switches subjects

### 3.2.9 Teacher Communication — P1
- In-app messaging between parent and teacher:
  - Thread-based (per student)
  - Subject line + message body
  - Read receipts
  - Attachment support (images, PDFs)
- Alert system (teacher → parent):
  - Configurable alert types:
    | Alert | Trigger | Default |
    |-------|---------|---------|
    | Struggling | 3+ low scores in a row | ON |
    | Inactive | No activity for 3+ days | ON |
    | Milestone | Level-up, mastery achieved | ON |
    | Streak broken | Lost streak | OFF |
    | Time limit reached | Daily limit hit | ON |
  - Delivery: in-app notification + email (configurable)
- Teacher broadcast: Message all parents in a class
- **Acceptance Criteria**: Messages deliver in real-time; alerts trigger correctly; email delivery works; broadcast reaches all class parents

### 3.2.10 Shared Session History & Conversation Starters — P2
- Parent views child's session transcripts (read-only)
- Bookmarkable moments: Parent marks specific exchanges for teacher discussion
- Pre-built conversation starters:
  - "Let's learn about [child's current topic] together"
  - "Can you teach me what you learned about [topic] today?"
  - Weekly family challenge from the AI
- **Acceptance Criteria**: Transcripts load correctly; bookmarks persist; conversation starters contextual to child's activity

---

## 4. Pages, Views, and UI Components

### 4.1 Page Inventory

| Page | Route | Access Role | Description |
|------|-------|-------------|-------------|
| Parent Dashboard Home | `/parent` | parent | Overview of all children |
| Child Detail View | `/parent/children/{id}` | parent | Per-child mastery + stats |
| Activity Feed | `/parent/children/{id}/activity` | parent | Chronological activity log |
| Progress Report | `/parent/children/{id}/report` | parent | PDF report view/download |
| Content Controls | `/parent/children/{id}/controls` | parent | Restrictions + time limits |
| Co-Learning Session | `/parent/children/{id}/co-learn` | parent | Join child's session |
| Messages | `/parent/messages` | parent | Teacher communication |
| Consent Management | `/parent/consent` | parent | COPPA consent status |
| Add Child | `/parent/add-child` | parent | Link to child account |

### 4.2 Layout Mockup Descriptions

#### Parent Dashboard Home (`/parent`)
**Desktop (>1024px)**:
- Left sidebar (250px): Child list — avatar + name + streak flame + level badge. "Add Child" button at bottom.
- Main area: Selected child's overview
  - Top row: Key stats cards (4): Total Study Time, Quiz Average, Current Streak, Mastery Level
  - Middle: Two charts side by side — Mastery radar chart (left), Weekly time bar chart (right)
  - Bottom: Recent activity feed (last 5 items) + AI daily summary card
- Right panel (300px): Alerts/notifications + Quick links (Controls, Reports, Messages)

**Tablet (640-1024px)**:
- Child selector: horizontal pill tabs at top
- Two-column layout: Stats cards (2×2 grid) + charts (stacked) on left, activity feed + alerts on right

**Mobile (<640px)**:
- Child selector: dropdown at top with avatar
- Stacked cards: stats row (horizontal scroll), mastery chart (full width), time chart, activity feed (last 3 items + "View All"), alerts
- Bottom nav: Dashboard | Activity | Controls | Messages

#### Co-Learning Session (`/parent/children/{id}/co-learn`)
**Desktop**: Split screen — child's chat view (left 60%) with real-time messages, parent guide sidebar (right 40%) with tips + observer/participant toggle
**Mobile**: Full-screen chat view, parent guide as bottom sheet (swipe up), role toggle as floating button

### 4.3 Component Hierarchy

```
components/parent/
├── ParentDashboard.tsx           (main dashboard layout)
├── ChildSelector.tsx             (sidebar/dropdown child picker)
├── ChildCard.tsx                 (child overview in selector)
├── ChildProgressOverview.tsx     (stats + charts for one child)
├── MasteryRadarChart.tsx         (per-subject radar chart)
├── TimeBreakdownChart.tsx        (weekly time bar chart)
├── StatCard.tsx                  (key metric card)
├── TrendIndicator.tsx            (↑ → ↓ with color)
├── ActivityFeed.tsx              (chronological activity log)
├── ActivityFeedItem.tsx          (single activity entry)
├── AIDailySummary.tsx            (AI-generated daily recap)
├── ReportViewer.tsx              (PDF report view/download)
├── ContentControls.tsx           (restrictions settings page)
├── TimeLimitSettings.tsx         (daily/weekly time controls)
├── QuietHoursSettings.tsx        (time range picker)
├── SubjectRestrictions.tsx       (toggle subjects/topics)
├── COPPAConsentFlow.tsx          (consent wizard)
├── ConsentStatus.tsx             (current consent state)
├── CoLearningSession.tsx         (join child's session)
├── CoLearningIndicator.tsx       (shows co-learning active)
├── ParentGuideSidebar.tsx        (contextual tips)
├── MessageThread.tsx             (parent-teacher messaging)
├── MessageComposer.tsx           (compose new message)
├── AlertsPanel.tsx               (parent notifications)
├── AlertPreferences.tsx          (configure alert types)
├── ConversationStarters.tsx      (pre-built prompts)
└── FamilyChallenge.tsx           (weekly family activity)
```

---

## 5. Backend API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/parent/children` | List linked children with summary stats | parent |
| POST | `/api/parent/children/link` | Link to child (send invite) | parent |
| DELETE | `/api/parent/children/{id}/unlink` | Remove link to child | parent |
| GET | `/api/parent/children/{id}/progress` | Detailed progress for one child | parent |
| GET | `/api/parent/children/{id}/activity` | Activity feed (paginated) | parent |
| GET | `/api/parent/children/{id}/activity/summary` | AI-generated daily summary | parent |
| GET | `/api/parent/children/{id}/report` | Generate/download PDF report | parent |
| GET | `/api/parent/children/{id}/controls` | Get current content controls | parent |
| PUT | `/api/parent/children/{id}/controls` | Update content controls | parent |
| GET | `/api/parent/children/{id}/sessions` | Child's session history | parent |
| GET | `/api/parent/children/{id}/sessions/{sid}/transcript` | Session transcript | parent |
| POST | `/api/parent/children/{id}/sessions/{sid}/bookmark` | Bookmark a message | parent |
| POST | `/api/parent/children/{id}/co-learn/join` | Join co-learning session | parent |
| POST | `/api/parent/children/{id}/co-learn/leave` | Leave co-learning session | parent |
| GET | `/api/parent/consent` | Get consent status for all children | parent |
| POST | `/api/parent/consent/grant` | Grant COPPA consent | parent |
| POST | `/api/parent/consent/revoke` | Revoke consent | parent |
| POST | `/api/parent/consent/delete-data` | Request data deletion | parent |
| GET | `/api/parent/messages` | Get message threads | parent |
| POST | `/api/parent/messages` | Send message to teacher | parent |
| GET | `/api/parent/messages/{thread_id}` | Get thread messages | parent |
| GET | `/api/parent/alerts` | Get parent alerts | parent |
| PUT | `/api/parent/alerts/preferences` | Update alert preferences | parent |
| POST | `/api/parent/alerts/{id}/dismiss` | Dismiss an alert | parent |
| GET | `/api/parent/conversation-starters` | Get contextual starters | parent |
| GET | `/api/parent/family-stats` | Aggregate family stats | parent |

---

## 6. Database Schema Additions

```sql
CREATE TABLE IF NOT EXISTS parent_alerts (
    id              SERIAL PRIMARY KEY,
    parent_id       INTEGER NOT NULL REFERENCES tutor_users(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    alert_type      VARCHAR(50) NOT NULL CHECK (alert_type IN (
        'struggling', 'inactive', 'milestone', 'streak_broken',
        'time_limit_reached', 'consent_expiring', 'custom'
    )),
    title           VARCHAR(255) NOT NULL,
    message         TEXT,
    data_json       JSONB DEFAULT '{}',
    read_at         TIMESTAMPTZ,
    dismissed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_parent_alerts_parent ON parent_alerts(parent_id, created_at DESC);
CREATE INDEX idx_parent_alerts_unread ON parent_alerts(parent_id) WHERE read_at IS NULL;

CREATE TABLE IF NOT EXISTS parent_alert_preferences (
    id              SERIAL PRIMARY KEY,
    parent_id       INTEGER NOT NULL REFERENCES tutor_users(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    alert_type      VARCHAR(50) NOT NULL,
    enabled         BOOLEAN DEFAULT TRUE,
    email_enabled   BOOLEAN DEFAULT TRUE,
    UNIQUE(parent_id, student_id, alert_type)
);

CREATE TABLE IF NOT EXISTS parent_teacher_messages (
    id              SERIAL PRIMARY KEY,
    thread_id       VARCHAR(100) NOT NULL,
    sender_id       INTEGER NOT NULL REFERENCES tutor_users(id),
    receiver_id     INTEGER NOT NULL REFERENCES tutor_users(id),
    student_id      INTEGER REFERENCES tutor_users(id),
    subject         VARCHAR(255),
    body            TEXT NOT NULL,
    attachments_json JSONB DEFAULT '[]',
    read_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_pt_messages_thread ON parent_teacher_messages(thread_id, created_at);
CREATE INDEX idx_pt_messages_receiver ON parent_teacher_messages(receiver_id, read_at);

CREATE TABLE IF NOT EXISTS co_learning_sessions (
    id              SERIAL PRIMARY KEY,
    parent_id       INTEGER NOT NULL REFERENCES tutor_users(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    session_id      INTEGER NOT NULL REFERENCES tutor_sessions(id),
    role            VARCHAR(20) DEFAULT 'observer' CHECK (role IN ('observer', 'participant')),
    joined_at       TIMESTAMPTZ DEFAULT NOW(),
    left_at         TIMESTAMPTZ
);
CREATE INDEX idx_co_learning_session ON co_learning_sessions(session_id);

CREATE TABLE IF NOT EXISTS session_bookmarks (
    id              SERIAL PRIMARY KEY,
    parent_id       INTEGER NOT NULL REFERENCES tutor_users(id),
    session_id      INTEGER NOT NULL REFERENCES tutor_sessions(id),
    message_index   INTEGER NOT NULL,
    note            TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS consent_records (
    id              SERIAL PRIMARY KEY,
    parent_id       INTEGER NOT NULL REFERENCES tutor_users(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    consent_type    VARCHAR(50) NOT NULL CHECK (consent_type IN ('coppa', 'data_processing', 'marketing')),
    status          VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'granted', 'revoked', 'expired')),
    granted_at      TIMESTAMPTZ,
    revoked_at      TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    ip_address      VARCHAR(45),
    evidence_json   JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_consent_parent_student ON consent_records(parent_id, student_id, consent_type);
CREATE INDEX idx_consent_status ON consent_records(status) WHERE status = 'granted';

-- Extend content_restrictions if needed (already exists in init.sql)
-- ALTER TABLE content_restrictions ADD COLUMN IF NOT EXISTS daily_time_limit_minutes INTEGER;
-- ALTER TABLE content_restrictions ADD COLUMN IF NOT EXISTS weekly_time_limit_minutes INTEGER;
-- ALTER TABLE content_restrictions ADD COLUMN IF NOT EXISTS quiet_hours_json JSONB;
-- ALTER TABLE content_restrictions ADD COLUMN IF NOT EXISTS effective_grade_override VARCHAR(10);
```

---

## 7. Service Layer Architecture

### New Files:
- `backend/app/services/parent_dashboard.py` — Progress aggregation, activity feed, AI summaries
- `backend/app/services/report_generator.py` — PDF report generation (weasyprint or reportlab)
- `backend/app/services/co_learning.py` — WebSocket session management, dual-audience prompting
- `backend/app/services/consent_service.py` — COPPA consent lifecycle
- `backend/app/services/parent_alerts.py` — Alert generation and delivery

### New Router: `backend/app/routers/parent.py`
- All endpoints require `parent` role
- Child access validated: parent can only view linked children

---

## 8. Celery Task Definitions

| Task | Trigger | Frequency | Description |
|------|---------|-----------|-------------|
| `generate_weekly_report` | Cron | Sunday 18:00 UTC | Generate PDF for each parent-child pair |
| `send_parent_digest_email` | Cron | Daily 19:00 UTC | Email with AI activity summary |
| `check_struggling_alerts` | Cron | Every 4 hours | Detect struggling students (3+ low scores) |
| `check_inactive_alerts` | Cron | Daily 12:00 UTC | Detect 3+ day inactivity |
| `check_consent_expiry` | Cron | Weekly Monday | Send renewal reminders for expiring consent |
| `generate_ai_activity_summary` | Event | After session | Generate parent-friendly session summary |

---

## 9. State Management (Frontend)

### New Store: `frontend/stores/parent-store.ts`

```typescript
interface ParentState {
  children: ChildSummary[];
  activeChildId: number | null;

  // Active child data
  progress: ChildProgress | null;
  activityFeed: ActivityItem[];
  controls: ContentControls | null;

  // Alerts & messages
  alerts: ParentAlert[];
  unreadAlerts: number;
  messageThreads: MessageThread[];
  unreadMessages: number;

  // Co-learning
  coLearningActive: boolean;
  coLearningRole: 'observer' | 'participant' | null;

  // Consent
  consentStatuses: ConsentRecord[];

  // Actions
  fetchChildren: () => Promise<void>;
  selectChild: (childId: number) => void;
  fetchProgress: (childId: number) => Promise<void>;
  fetchActivity: (childId: number, page: number) => Promise<void>;
  updateControls: (childId: number, controls: ContentControls) => Promise<void>;
  joinCoLearning: (childId: number, role: string) => Promise<void>;
  leaveCoLearning: () => Promise<void>;
  fetchAlerts: () => Promise<void>;
  dismissAlert: (alertId: number) => Promise<void>;
}
```

---

## 10. Real-Time Requirements

| Feature | Mechanism | Details |
|---------|-----------|---------|
| Co-learning session | WebSocket | Bi-directional message sync between parent and child session |
| Parent alerts | SSE | Push new alerts to parent dashboard |
| Activity feed | SSE | Real-time activity updates as child studies |
| Time limit countdown | Client-side timer | Synced with server on session start |

---

## 11. Testing Strategy

### Backend Tests
- Parent-child linking flow
- Content control enforcement (server-side validation)
- COPPA consent lifecycle (grant, revoke, expire, delete)
- Report generation (PDF output validation)
- Alert trigger conditions
- Co-learning session join/leave

### Frontend E2E
- Parent logs in and sees children
- Navigate to child detail view
- Set content controls and verify enforcement
- COPPA consent flow (complete wizard)
- Join co-learning session
- Send message to teacher

---

## 12. Deployment Considerations

- **WebSocket**: Requires WebSocket support in reverse proxy (nginx/ALB)
- **PDF Generation**: `weasyprint` dependency (or `reportlab`) — add to `requirements.txt`
- **Email Service**: SMTP configuration or email API (SendGrid, SES) for report/alert delivery
- **New env vars**: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_FROM`
- **Storage**: Generated PDFs stored temporarily (S3 or local) with TTL cleanup

---

## 13. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| COPPA non-compliance | Legal liability | Strict consent flow; legal review; audit trail; annual renewal |
| Parent over-monitoring | Student disengagement | Age-appropriate data visibility; privacy boundaries for 9-12 |
| Co-learning complexity | Technical bugs | Start with observer mode; add participant mode iteratively |
| Report generation load | Server performance | Generate async via Celery; cache for 24 hours; limit frequency |

---

## 14. Implementation Checklist

- [ ] `3.2.1` Child progress overview — backend aggregation APIs + frontend charts
- [ ] `3.2.2` Activity feed — backend activity logging + frontend feed component
- [ ] `3.2.2` AI activity summary — backend AI summary generation
- [ ] `3.2.3` Report generation — backend PDF service + Celery task + email delivery
- [ ] `3.2.4` Content controls — backend enforcement + frontend settings UI
- [ ] `3.2.4` Time limits — backend tracking + frontend countdown + quiet hours
- [ ] `3.2.5` COPPA consent flow — backend consent service + frontend wizard
- [ ] `3.2.6` Multi-child support — backend multi-child APIs + frontend child selector
- [ ] `3.2.7` Co-learning mode — backend WebSocket + dual-audience prompting + frontend UI
- [ ] `3.2.8` Parent guide sidebar — frontend contextual tips component
- [ ] `3.2.9` Teacher communication — backend messaging + frontend threads
- [ ] `3.2.9` Alert system — backend alert triggers + Celery tasks + frontend alerts panel
- [ ] `3.2.10` Session history + bookmarks + conversation starters
- [ ] `3.2.E2E` Playwright E2E tests for parent flows
