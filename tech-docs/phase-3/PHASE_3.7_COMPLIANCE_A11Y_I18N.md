# Functional Phase 3.7: Compliance, Accessibility, i18n

> **Status**: Not Started
> **Estimated Duration**: 3 weeks
> **Dependencies**: All prior phases (this phase audits and hardens everything)
> **Sprint Reference**: Sprint 3.7 in AI_TUTOR_MODULE.md (Section 22.7)
> **Priority**: P0 — High (legal requirement for under-13 users, market expansion blocker)

---

## 1. Executive Summary

This phase transforms the platform from a feature-rich prototype into a production-ready, legally compliant, globally accessible educational product. Compliance ensures legal operation (COPPA for under-13, FERPA for education records, GDPR for international users). Accessibility makes the platform usable by students with disabilities (WCAG 2.1 AA). Internationalization opens the platform to non-English markets. Additionally, the Wellness Guardian protects students from overuse, and Micro-Tutoring enables quick learning sessions for busy schedules. This phase audits and hardens ALL prior work.

---

## 2. Target Users and Personas

| User Type | Goals | How This Phase Serves Them |
|-----------|-------|---------------------------|
| **Student (disability)** | Full platform access | Screen reader support, keyboard nav, dyslexia font, high contrast |
| **Student (international)** | Learn in native language | 6 languages, RTL support, bilingual explanations |
| **Student (ESL/ELL)** | Language learning support | Bilingual mode, simplified vocabulary, pronunciation help |
| **Student (all)** | Healthy study habits | Session limits, break reminders, wellness guardian |
| **Parent (under-13)** | Legal consent | COPPA consent flow, data controls |
| **Administrator** | Legal compliance, audit | Audit logs, data retention, compliance dashboard |
| **Organization** | Deploy at scale | Multi-tenant compliance, data isolation |

---

## 3. Features and Sub-Features

### 3.7.1 COPPA Compliance (Children Under 13) — P0
- **Verifiable Parental Consent**:
  - Auto-detect under-13 (birthdate during registration OR grade K-5)
  - Account enters "pending consent" state (chat disabled, limited browse)
  - Parent receives consent request via email with unique link
  - Verification method: email confirmation + knowledge-based question
  - Consent expires annually — renewal reminders 30 days before
- **Data Minimization**:
  - Under-13 accounts collect minimum required data
  - No behavioral profiling for advertising (our platform doesn't advertise, but enforce the principle)
  - No third-party data sharing without explicit consent
- **Parent Controls**:
  - Parent can review all data collected about child
  - Parent can request complete data deletion (72-hour SLA)
  - Parent can revoke consent (account deactivated immediately)
- **Under-13 Restrictions**:
  - No public leaderboard participation (even if opted in by parent)
  - No multiplayer with unknown users (class-only)
  - No external link navigation
  - Simplified privacy notices (kid-friendly language)
- **Acceptance Criteria**: Under-13 detection works; consent blocks full access; deletion completes in 72h; annual renewal triggers; audit trail complete

### 3.7.2 FERPA Compliance (Education Records) — P0
- **Access Control**:
  - Student records accessible only to: the student, linked parents, assigned teachers, school admins
  - No cross-school data access
  - Teacher sees only their class data
- **Audit Logging**:
  - Every record access logged: who, what, when, from where
  - Every modification logged: old value, new value, actor
  - Log retention: 7 years minimum
  - Immutable audit trail (append-only table, no delete)
- **Directory Information**:
  - Opt-out mechanism for directory information (name in leaderboard, etc.)
  - Default: opted out for under-13
- **Data Portability**:
  - Student/parent can request full data export (JSON + CSV)
  - Export includes: sessions, quiz results, mastery data, flashcards, badges
  - Generated as downloadable ZIP file
- **Acceptance Criteria**: Access control enforced at API level; audit log captures all data access; export generates complete dataset; opt-out works

### 3.7.3 GDPR Compliance (International Users) — P1
- **Consent Management**:
  - Granular consent: data processing, analytics, email communications
  - Consent can be revoked at any time
  - Pre-checked boxes prohibited
  - Cookie consent banner (if cookies used beyond essential)
- **Right to Erasure**:
  - User requests deletion → 30-day grace period → permanent deletion
  - Cascade: all related records (sessions, quizzes, mastery, flashcards, messages)
  - Anonymization option: keep aggregate data, delete PII
- **Data Portability**:
  - GDPR-compliant JSON export (machine-readable)
  - Includes all personal data the system holds
- **Data Processing Records**:
  - Maintain record of processing activities
  - Data protection impact assessment documentation
- **Acceptance Criteria**: Consent granular and revocable; deletion cascades completely; export is machine-readable; processing records maintained

### 3.7.4 Audit System — P0
- **Audit Middleware**: Intercepts all data-modifying requests
  - Captures: actor_id, actor_role, action, resource_type, resource_id, old_value, new_value, IP, timestamp
  - Stored in append-only `audit_log` table
  - Performance: async write (don't slow down requests)
- **Admin Audit Dashboard**:
  - Search/filter by actor, action, resource, date range
  - Export as CSV for compliance reporting
  - Alert on suspicious patterns (bulk access, unusual hours)
- **Acceptance Criteria**: All data modifications logged; query performance <2s for 1M+ rows; export works; no audit gaps

### 3.7.5 Data Retention Policies — P1
- **Configurable Per Resource**:
  | Resource | Default Retention | Action |
  |----------|------------------|--------|
  | Session messages | 2 years | Anonymize |
  | Quiz attempts | 3 years | Delete |
  | Flashcard reviews | 1 year | Delete |
  | Audit logs | 7 years | Archive |
  | Generated audio | 90 days (unassigned) | Delete |
  | Code executions | 1 year | Delete |
  | Uploaded documents | Until KB deleted + 30 days | Delete |
- **Automated Cleanup**: Celery task runs daily, processes expired records
- **Admin Configuration**: UI to view/adjust retention policies
- **Acceptance Criteria**: Cleanup runs daily without errors; deleted records unrecoverable; admin can adjust policies

### 3.7.6 Accessibility — Keyboard Navigation — P0
- **Full Tab Navigation**:
  - All interactive elements reachable via Tab
  - Logical tab order (top→bottom, left→right)
  - Skip-to-content link at top of every page
  - Focus trap in modals and dialogs
- **Arrow Key Navigation**:
  - Lists, menus, tabs navigable with arrow keys
  - Radio groups cycle with arrows
  - Grid components (leaderboard, badge gallery) support 2D arrow nav
- **Keyboard Shortcuts**:
  - `Escape`: Close modal, cancel action
  - `Enter`/`Space`: Activate buttons
  - `Ctrl+/`: Open keyboard shortcut help
  - Chat-specific: `Enter` to send, `Shift+Enter` for newline
- **Focus Indicators**:
  - Visible focus ring on all elements (Tailwind `ring-2 ring-offset-2`)
  - Custom focus styles for dark/light mode
  - Never `outline-none` without replacement
- **Acceptance Criteria**: Every interactive element keyboard-accessible; focus visible; tab order logical; modals trap focus; shortcuts documented

### 3.7.7 Accessibility — Screen Reader Compatibility — P0
- **Semantic HTML**:
  - `<nav>`, `<main>`, `<aside>`, `<header>`, `<footer>` landmarks
  - `<h1>`-`<h6>` hierarchy (one `<h1>` per page)
  - `<button>` for actions, `<a>` for navigation (never vice versa)
  - `<ul>`/`<ol>` for lists
- **ARIA Labels**:
  - `aria-label` for icon-only buttons
  - `aria-describedby` for form fields with help text
  - `aria-live="polite"` for chat messages (new messages announced)
  - `aria-live="assertive"` for error messages and alerts
  - `aria-expanded` for collapsible sections
  - `role="status"` for loading states
- **Dynamic Content**:
  - Chat messages: announced as they arrive
  - Toasts/notifications: announced immediately
  - Loading states: announced when starting and completing
  - Route changes: announce new page title
- **Images & Media**:
  - All images have `alt` text
  - AI-generated diagrams: AI generates alt text description
  - Decorative images: `alt=""`
  - Audio: transcript always available
- **Acceptance Criteria**: VoiceOver/NVDA/JAWS can navigate all pages; dynamic content announced; no unlabeled controls

### 3.7.8 Accessibility — Visual — P0
- **Color Contrast**: OKLCH system ensures 4.5:1 minimum (AA) for normal text, 3:1 for large text
  - Audit all color combinations with automated tool
  - Fix any failing combinations
- **Dyslexia Font Option**: Toggle in settings to switch to OpenDyslexic
  - Applied globally via CSS custom property
  - Font loaded lazily from CDN
- **High Contrast Mode**: Toggle that increases contrast ratios to 7:1 (AAA)
  - Stronger borders, bolder text, high-contrast backgrounds
- **Font Size Control**: Small / Medium / Large / Extra Large
  - Applied via Tailwind responsive scale (not hardcoded px)
- **Reduced Motion**: Respects `prefers-reduced-motion` media query
  - Toggle in settings to override system preference
  - Affects: confetti, slide transitions, loading spinners, auto-scroll
  - Fallback: instant state changes instead of animations
- **Acceptance Criteria**: All text passes AA contrast; dyslexia font toggles globally; high contrast works in light+dark; reduced motion removes all animations

### 3.7.9 Accessibility — Automated Testing — P1
- **axe-core Integration**:
  - Run axe-core on every page during E2E tests
  - Fail CI if any critical/serious issues detected
  - Report minor issues as warnings
- **Lighthouse Accessibility Audit**: Score >90 on all pages
- **Manual Testing Checklist**: Screen reader walkthrough for critical flows
- **Acceptance Criteria**: CI blocks on accessibility regressions; Lighthouse >90; manual test documented

### 3.7.10 Multi-Language Support (i18n) — P0
- **Framework**: `next-intl` for Next.js App Router
- **Initial Languages**:
  | Language | Code | Direction | Priority |
  |----------|------|-----------|----------|
  | English | `en` | LTR | P0 — Default |
  | Spanish | `es` | LTR | P0 — US market |
  | French | `fr` | LTR | P1 — Canada/Africa |
  | Arabic | `ar` | RTL | P1 — MENA market |
  | Mandarin Chinese | `zh` | LTR | P1 — Asian market |
  | Hindi | `hi` | LTR | P2 — India market |
- **Translation Pipeline**:
  - All UI strings extracted to `frontend/messages/{locale}.json`
  - String IDs: `{page}.{section}.{key}` (e.g., `dashboard.gamification.xpLabel`)
  - AI-assisted translation (validated by native speakers before production)
  - Fallback chain: preferred language → English
- **RTL Layout Support**:
  - Tailwind `dir="rtl"` on `<html>` element
  - Tailwind `rtl:` variant for directional styles
  - Swap left/right padding, margins, borders
  - Mirror icons that imply direction (arrows, progress bars)
  - Test: Arabic layout review for every page
- **AI Content Localization**:
  - `preferred_language` field on `tutor_users` table
  - AI responses generated in student's preferred language
  - System prompts include language instruction
  - Subject-specific terms use locale-appropriate vocabulary
- **Locale-Aware Formatting**:
  - Date: locale format (MM/DD/YYYY vs DD/MM/YYYY)
  - Numbers: locale separators (1,000 vs 1.000)
  - Currency: locale symbol
  - Time: 12h vs 24h based on locale
- **Acceptance Criteria**: All UI strings translated; RTL layouts correct for Arabic; AI responds in preferred language; formatting locale-aware; language switch instant (no page reload)

### 3.7.11 ESL/ELL Bilingual Mode — P2
- **Dual-Language Explanations**: AI provides explanation in student's language + English side-by-side
- **Simplified Vocabulary**: AI uses simpler English when ESL mode active
- **Key Term Translation**: Technical terms translated inline (hover for definition in native language)
- **Pronunciation Help**: Word-level pronunciation guide for English terms
- **Acceptance Criteria**: Bilingual mode shows two-column text; vocabulary simplified; terms translated on hover

### 3.7.12 Wellness Guardian — P0
- **Age-Based Session Limits**:
  | Grade Band | Default Max | Configurable Range |
  |------------|-------------|-------------------|
  | K-2 | 20 min | 10-30 min |
  | 3-5 | 30 min | 15-45 min |
  | 6-8 | 45 min | 20-60 min |
  | 9-12 | 60 min | 30-120 min |
- **Break Reminders**:
  - 20-20-20 rule: Every 20 minutes → "Look at something 20 feet away for 20 seconds"
  - Gentle reminder (not blocking): animated eye icon, dismissible
  - After 3 dismissals → stronger reminder
- **Session Limit Enforcement**:
  - Warning at 5 minutes remaining
  - Gentle wind-down: "Let's finish this last question and take a break!"
  - Hard stop: save session, show friendly "break time" screen
  - No immediate re-entry: 5-minute cooldown (configurable)
- **Quiet Hours** (parent-configurable):
  - Default: none (parent must explicitly set)
  - During quiet hours: app shows "It's rest time" screen
  - School night detection: "It's 11 PM on a school night — time to rest!"
  - Notification suppression during quiet hours
- **Post-Session Cooldown**:
  - Breathing exercise: 4-7-8 technique (animated guide)
  - Fun fact of the day
  - Encouragement message from tutor persona
- **Acceptance Criteria**: Limits enforce accurately; reminders appear at correct intervals; quiet hours block access; cooldown shows after session end; parent can override limits

### 3.7.13 Micro-Tutoring — P2
- **Quick Quiz** (5 minutes):
  - 3-5 targeted questions from at-risk memory topics
  - Launched from notification: "Quick review: 5 questions on fractions"
  - Results update mastery + memory scores
- **Daily Review**:
  - Spaced repetition micro-session
  - 8-10 flashcards due today
  - Takes 3-5 minutes
  - Available as notification action
- **Bus-Stop Learning** (audio-based):
  - 3-minute audio summaries of recent topics
  - Optimized for headphone listening
  - Auto-play queue: topic1 → topic2 → topic3
  - No screen required after starting
- **Acceptance Criteria**: Quick quiz loads in <2s; daily review pulls correct cards; audio summaries generate from recent topics; all work on mobile

---

## 4. Pages, Views, and UI Components

### 4.1 Page Inventory

| Page | Route | Access Role | Description |
|------|-------|-------------|-------------|
| Accessibility Settings | `/settings/accessibility` | all | Font, contrast, motion, keyboard |
| Language Settings | `/settings/language` | all | Language selector + preferences |
| Privacy Settings | `/settings/privacy` | all | Consent management + data controls |
| Data Export | `/settings/privacy/export` | all | Request/download data export |
| Data Deletion | `/settings/privacy/delete` | all | Request account/data deletion |
| Admin Audit Log | `/admin/audit-log` | admin | Search/filter/export audit records |
| Admin Data Retention | `/admin/data-retention` | admin | Configure retention policies |
| Admin Compliance Dashboard | `/admin/compliance` | admin | COPPA/FERPA/GDPR status overview |
| Micro-Tutoring | `/micro` | student | Quick quiz, daily review, bus-stop audio |
| Break Time Screen | `/break` | student | Shown during session cooldown |

### 4.2 Layout Mockup Descriptions

#### Accessibility Settings (`/settings/accessibility`)
**Desktop**: Form layout with grouped sections. Font section: font family selector (System/OpenDyslexic), size slider (S/M/L/XL), preview text area. Visual section: high contrast toggle, reduced motion toggle. Keyboard section: shortcut reference table. All changes apply instantly with preview.
**Mobile**: Same form, single column. Preview area shows current page adjusted.

#### Language Settings (`/settings/language`)
**Desktop**: Language grid (6 cards with flag + name). Active language highlighted. Below: content language preference (may differ from UI language). RTL preview when Arabic selected.
**Mobile**: Language list with radio buttons. Flag icons for quick recognition.

#### Admin Audit Log (`/admin/audit-log`)
**Desktop**: Full-width table with filters at top (actor, action, resource, date range). Columns: Timestamp, Actor, Role, Action, Resource, Details, IP. Pagination. Export CSV button. Click row for full detail modal.
**Mobile**: Simplified card list (timestamp, actor, action). Filter as bottom sheet.

#### Micro-Tutoring (`/micro`)
**Desktop**: Three large cards: Quick Quiz (brain icon, "5 min"), Daily Review (cards icon, "3 min"), Bus-Stop Audio (headphone icon, "3 min"). Each shows: count of items due, estimated time, "Start" button. Below: history of recent micro-sessions.
**Mobile**: Full-width cards stacked. Quick-launch from notification pulls directly into session.

### 4.3 Component Hierarchy

```
components/settings/
├── AccessibilitySettings.tsx     (full settings page)
├── FontSelector.tsx              (font family + size)
├── ContrastToggle.tsx            (high contrast on/off)
├── MotionToggle.tsx              (reduced motion on/off)
├── KeyboardShortcutTable.tsx     (reference table)
├── LanguageSettings.tsx          (language selection page)
├── LanguageCard.tsx              (individual language option)
├── PrivacySettings.tsx           (consent + data controls)
├── ConsentManager.tsx            (granular consent toggles)
├── DataExportButton.tsx          (trigger export)
├── DataDeletionFlow.tsx          (deletion request wizard)
└── PreviewPanel.tsx              (live preview of settings)

components/admin/
├── AuditLogTable.tsx             (filterable audit log)
├── AuditLogFilters.tsx           (filter controls)
├── AuditLogDetail.tsx            (row detail modal)
├── DataRetentionSettings.tsx     (retention policy editor)
├── ComplianceDashboard.tsx       (COPPA/FERPA/GDPR status)
└── ComplianceStatusCard.tsx      (individual compliance area)

components/wellness/
├── SessionTimer.tsx              (countdown timer)
├── BreakReminder.tsx             (20-20-20 popup)
├── SessionLimitWarning.tsx       (5-min warning)
├── BreakTimeScreen.tsx           (cooldown screen)
├── BreathingExercise.tsx         (4-7-8 animated guide)
├── QuietHoursScreen.tsx          (rest time display)
└── FunFact.tsx                   (post-session fun fact)

components/micro/
├── MicroTutoringHub.tsx          (hub with 3 options)
├── QuickQuiz.tsx                 (5-min quiz session)
├── DailyReview.tsx               (flashcard micro-session)
└── BusStopAudio.tsx              (audio queue player)
```

---

## 5. Backend API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/settings/preferences` | Get user preferences (language, a11y, wellness) | all |
| PUT | `/api/settings/preferences` | Update preferences | all |
| GET | `/api/settings/privacy/consents` | Get consent status | all |
| PUT | `/api/settings/privacy/consents` | Update consents | all |
| POST | `/api/settings/privacy/export` | Request data export | all |
| GET | `/api/settings/privacy/export/{id}` | Download export (when ready) | all |
| POST | `/api/settings/privacy/delete` | Request account deletion | all |
| GET | `/api/admin/audit-log` | Query audit log (filtered, paginated) | admin |
| GET | `/api/admin/audit-log/export` | Export audit log CSV | admin |
| GET | `/api/admin/data-retention` | Get retention policies | admin |
| PUT | `/api/admin/data-retention` | Update retention policies | admin |
| GET | `/api/admin/compliance` | Compliance status dashboard data | admin |
| GET | `/api/wellness/status` | Current session time, limit, break schedule | student |
| POST | `/api/wellness/break/dismiss` | Dismiss break reminder | student |
| POST | `/api/wellness/session/extend` | Request time extension (teacher/parent approval) | student |
| GET | `/api/micro/queue` | Get micro-tutoring queue (quiz + review + audio) | student |
| POST | `/api/micro/quick-quiz/start` | Start quick quiz | student |
| POST | `/api/micro/daily-review/start` | Start daily review | student |
| GET | `/api/micro/bus-stop/playlist` | Get audio queue for bus-stop mode | student |

---

## 6. Database Schema Additions

```sql
CREATE TABLE IF NOT EXISTS audit_log (
    id              BIGSERIAL PRIMARY KEY,
    actor_id        INTEGER REFERENCES tutor_users(id),
    actor_role      VARCHAR(20),
    action          VARCHAR(100) NOT NULL,
    resource_type   VARCHAR(50),
    resource_id     INTEGER,
    old_value_json  JSONB,
    new_value_json  JSONB,
    details_json    JSONB DEFAULT '{}',
    ip_address      VARCHAR(45),
    user_agent      VARCHAR(500),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
-- Partitioned by month for performance at scale
CREATE INDEX idx_audit_log_actor ON audit_log(actor_id, created_at DESC);
CREATE INDEX idx_audit_log_resource ON audit_log(resource_type, resource_id);
CREATE INDEX idx_audit_log_action ON audit_log(action, created_at DESC);
CREATE INDEX idx_audit_log_date ON audit_log(created_at);

CREATE TABLE IF NOT EXISTS consent_records (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES tutor_users(id),
    consent_type    VARCHAR(50) NOT NULL CHECK (consent_type IN (
        'coppa_parental', 'data_processing', 'analytics', 'email_communications',
        'third_party_sharing', 'cookie_consent'
    )),
    status          VARCHAR(20) NOT NULL CHECK (status IN ('granted', 'revoked', 'expired', 'pending')),
    granted_at      TIMESTAMPTZ,
    revoked_at      TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    ip_address      VARCHAR(45),
    evidence_json   JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_consent_user ON consent_records(user_id, consent_type);

CREATE TABLE IF NOT EXISTS data_retention_policies (
    id              SERIAL PRIMARY KEY,
    resource_type   VARCHAR(50) NOT NULL UNIQUE,
    retention_days  INTEGER NOT NULL,
    action          VARCHAR(20) DEFAULT 'delete' CHECK (action IN ('delete', 'anonymize', 'archive')),
    is_active       BOOLEAN DEFAULT TRUE,
    updated_by      INTEGER REFERENCES tutor_users(id),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS data_export_requests (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES tutor_users(id),
    format          VARCHAR(20) DEFAULT 'json',
    status          VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'ready', 'downloaded', 'expired')),
    file_url        VARCHAR(1000),
    file_size_bytes BIGINT,
    requested_at    TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS data_deletion_requests (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES tutor_users(id),
    reason          TEXT,
    status          VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'grace_period', 'processing', 'completed', 'cancelled')),
    grace_period_ends TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    requested_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES tutor_users(id) UNIQUE,
    language        VARCHAR(10) DEFAULT 'en',
    content_language VARCHAR(10),
    theme           VARCHAR(20) DEFAULT 'system' CHECK (theme IN ('light', 'dark', 'system')),
    font_family     VARCHAR(50) DEFAULT 'system',
    font_size       VARCHAR(10) DEFAULT 'medium' CHECK (font_size IN ('small', 'medium', 'large', 'xlarge')),
    high_contrast   BOOLEAN DEFAULT FALSE,
    dyslexia_font   BOOLEAN DEFAULT FALSE,
    reduced_motion  BOOLEAN DEFAULT FALSE,
    session_limit_minutes INTEGER,
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    break_reminder_enabled BOOLEAN DEFAULT TRUE,
    notification_preferences JSONB DEFAULT '{}',
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS session_wellness_log (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    session_id      INTEGER REFERENCES tutor_sessions(id),
    session_start   TIMESTAMPTZ NOT NULL,
    session_end     TIMESTAMPTZ,
    duration_minutes INTEGER,
    breaks_taken    INTEGER DEFAULT 0,
    break_reminders_dismissed INTEGER DEFAULT 0,
    limit_reached   BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_wellness_log_student ON session_wellness_log(student_id, session_start DESC);
```

---

## 7. Service Layer Architecture

### New Files:
- `backend/app/services/audit.py` — Audit logging (async, non-blocking)
- `backend/app/services/compliance.py` — COPPA/FERPA/GDPR enforcement, consent management
- `backend/app/services/data_export.py` — Full data export generation (JSON + CSV)
- `backend/app/services/data_retention.py` — Automated cleanup per retention policies
- `backend/app/services/wellness.py` — Session tracking, break scheduling, limit enforcement
- `backend/app/services/micro_tutoring.py` — Quick quiz, daily review, bus-stop audio queue

### New Middleware:
- `backend/app/middleware/audit_middleware.py` — Intercepts all write requests for audit logging

### New Routers:
- `backend/app/routers/settings.py` — User preferences, privacy, consent
- `backend/app/routers/admin_compliance.py` — Admin audit, retention, compliance
- `backend/app/routers/wellness.py` — Session wellness endpoints
- `backend/app/routers/micro.py` — Micro-tutoring endpoints

### Frontend i18n Setup:
- `frontend/messages/en.json` — English strings
- `frontend/messages/es.json` — Spanish strings
- `frontend/messages/fr.json` — French strings
- `frontend/messages/ar.json` — Arabic strings
- `frontend/messages/zh.json` — Mandarin strings
- `frontend/messages/hi.json` — Hindi strings
- `frontend/middleware.ts` — Locale detection and routing

---

## 8. Celery Task Definitions

| Task | Trigger | Description |
|------|---------|-------------|
| `run_data_retention_cleanup` | Daily 01:00 UTC | Delete/anonymize/archive expired records |
| `generate_data_export` | API request | Create ZIP with user's complete data |
| `process_data_deletion` | After grace period | Cascade delete all user data |
| `check_consent_expiry` | Daily 06:00 UTC | Send renewal reminders for expiring consents |
| `generate_audit_report` | Weekly Monday 07:00 UTC | Admin summary of audit activity |
| `check_break_reminders` | Every 5 minutes | Check active sessions needing break reminders |
| `generate_micro_quiz` | Daily 05:00 UTC | Pre-generate quick quiz questions for active students |

---

## 9. State Management (Frontend)

### New Store: `frontend/stores/preferences-store.ts`

```typescript
interface PreferencesState {
  // Language
  language: string;
  contentLanguage: string;

  // Accessibility
  fontFamily: 'system' | 'opendyslexic';
  fontSize: 'small' | 'medium' | 'large' | 'xlarge';
  highContrast: boolean;
  reducedMotion: boolean;
  theme: 'light' | 'dark' | 'system';

  // Wellness
  sessionLimitMinutes: number;
  sessionTimeRemaining: number;
  breakReminderEnabled: boolean;
  quietHoursActive: boolean;

  // Consent
  consents: Record<string, ConsentStatus>;

  // Actions
  updatePreference: (key: string, value: any) => Promise<void>;
  updateConsent: (type: string, granted: boolean) => Promise<void>;
  requestExport: () => Promise<void>;
  requestDeletion: () => Promise<void>;
  checkWellnessStatus: () => Promise<void>;
}
```

---

## 10. Frontend Package Additions

```json
{
  "next-intl": "^4.0.0"
}
```

Font:
- OpenDyslexic loaded from CDN on toggle (lazy-loaded, ~200KB)

---

## 11. Testing Strategy

### Backend Tests
- Audit logging: verify all write endpoints generate audit records
- COPPA: consent flow, under-13 detection, data deletion cascade
- FERPA: access control (teacher can't see other classes)
- GDPR: export completeness, deletion cascade, consent revocation
- Wellness: session time tracking, break trigger timing, limit enforcement
- Data retention: cleanup correctly deletes/anonymizes per policy

### Frontend E2E
- Accessibility:
  - Tab through entire dashboard flow
  - axe-core audit on every page (integrated in CI)
  - Screen reader simulation tests
- i18n:
  - Switch language, verify all strings translated
  - Switch to Arabic, verify RTL layout
  - Verify date/number formatting per locale
- Wellness:
  - Session timer countdown
  - Break reminder appears at 20 minutes
  - Quiet hours block access
- Micro-tutoring:
  - Start quick quiz, complete, verify mastery update
  - Start daily review, complete flashcard micro-session

### Lighthouse Audits
- Performance: >80
- Accessibility: >90
- Best Practices: >90
- SEO: >80

---

## 12. Deployment Considerations

- **next-intl**: Add to `frontend/package.json`; configure middleware for locale routing
- **OpenDyslexic**: Load from `https://cdn.jsdelivr.net/npm/open-dyslexic/` or self-host
- **Audit log**: Consider table partitioning by month for performance at scale
- **Data export**: ZIP files stored temporarily (S3 or local), auto-deleted after 7 days
- **COPPA**: Legal review required before enabling under-13 registration
- **New env vars**: none required (all configurable via admin UI)

---

## 13. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Legal non-compliance | Fines, shutdown | Legal counsel review; third-party compliance audit; annual review |
| Accessibility regression | Discrimination, lawsuits | axe-core in CI; accessibility champion review; user testing with disabled users |
| Translation quality | Poor UX in non-English | AI translation + native speaker review; community feedback loop |
| Audit log size | Performance degradation | Table partitioning; archive old logs to cold storage; indexed queries |
| Wellness enforcement workaround | Students circumvent limits | Server-side enforcement; parent notification on limit reached |

---

## 14. Implementation Checklist

### Compliance
- [ ] `3.7.1` COPPA — under-13 detection + consent flow + data minimization
- [ ] `3.7.1` COPPA — parent data review + deletion + revocation
- [ ] `3.7.2` FERPA — access control enforcement + directory opt-out
- [ ] `3.7.2` FERPA — data portability (export as ZIP)
- [ ] `3.7.3` GDPR — consent management UI + right to erasure + data portability
- [ ] `3.7.4` Audit system — middleware + audit_log table + admin dashboard
- [ ] `3.7.5` Data retention — policies config + automated Celery cleanup

### Accessibility
- [ ] `3.7.6` Keyboard navigation — tab order + arrow keys + shortcuts + focus indicators
- [ ] `3.7.7` Screen reader — semantic HTML + ARIA labels + live regions + dynamic content
- [ ] `3.7.8` Visual — contrast audit + dyslexia font + high contrast + font size + reduced motion
- [ ] `3.7.9` Automated testing — axe-core in CI + Lighthouse audits

### Internationalization
- [ ] `3.7.10` i18n setup — next-intl + message files (en, es) + locale routing
- [ ] `3.7.10` i18n expansion — fr, ar, zh, hi translations
- [ ] `3.7.10` RTL support — Arabic layout + Tailwind rtl: variants + mirrored icons
- [ ] `3.7.10` AI content localization — preferred_language in prompts + locale formatting
- [ ] `3.7.11` ESL/ELL bilingual mode — dual-language display + simplified vocabulary

### Wellness
- [ ] `3.7.12` Wellness guardian — session limits + break reminders + quiet hours
- [ ] `3.7.12` Wellness guardian — post-session cooldown (breathing + fun fact)
- [ ] `3.7.12` Wellness guardian — parent-configurable overrides

### Micro-Tutoring
- [ ] `3.7.13` Quick quiz — 5-min targeted quiz from at-risk topics
- [ ] `3.7.13` Daily review — flashcard micro-session from due cards
- [ ] `3.7.13` Bus-stop audio — short audio summaries with auto-play queue

### Cross-Cutting
- [ ] `3.7.AUDIT` Audit ALL prior phase features (retroactive accessibility + compliance pass)
- [ ] `3.7.E2E` Playwright E2E tests for settings, compliance, wellness, micro flows
- [ ] `3.7.CI` axe-core + Lighthouse integrated in CI pipeline
