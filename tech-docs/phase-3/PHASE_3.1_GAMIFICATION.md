# Functional Phase 3.1: Gamification & Streak Systems

> **Status**: Not Started
> **Estimated Duration**: 2 weeks
> **Dependencies**: Phase 2 complete (mastery tracking, adaptive quiz, flashcards, spaced repetition)
> **Sprint Reference**: Sprint 3.1 in AI_TUTOR_MODULE.md (Section 22.1)
> **Priority**: P0 — High (XP system is foundational for Phases 3.5, 3.6)

---

## 1. Executive Summary

Gamification transforms passive learning into active engagement by rewarding effort, consistency, and mastery. This phase introduces an enterprise-grade motivation system: XP earning across 8+ action types, age-themed level progression, daily streaks with freeze mechanics, achievement badges, opt-in class leaderboards, challenge modes, and a reward marketplace. Every subsequent phase (gaming engine, test prep) depends on this XP/reward infrastructure.

---

## 2. Target Users and Personas

| User Type | Goals | How This Phase Serves Them |
|-----------|-------|---------------------------|
| **Student (K-2)** | Fun, visual rewards, simple progress | Large badges, animated celebrations, pet/avatar rewards |
| **Student (3-5)** | Collecting, competing, streaks | Badge gallery, streak calendar, friend challenges |
| **Student (6-8)** | Social status, competition, customization | Leaderboard rank, avatar customization, team challenges |
| **Student (9-12)** | Achievement, self-improvement tracking | XP analytics, mastery-linked rewards, portfolio badges |
| **Teacher** | Motivate class, track engagement | Class gamification settings, challenge creation, engagement analytics |
| **Parent** | Understand child's engagement | See streaks, XP, badges in parent dashboard (Phase 3.2) |

---

## 3. Features and Sub-Features

### 3.1.1 XP (Experience Points) System — P0
- Award XP from 8 action types:
  | Action | Base XP | Notes |
  |--------|---------|-------|
  | Complete tutoring session (≥5 min) | +10 | Only once per session |
  | Quiz correct answer | +5 | Per question |
  | Flashcard review | +2 | Per card reviewed |
  | Daily login | +5 | Once per calendar day |
  | Mastery level-up | +25 | When topic mastery increases a level |
  | Streak milestone (7/30/100 days) | +10/day | Bonus on milestone days |
  | Show Your Thinking mode | +15 | Per session (encourages explanation) |
  | Peer help (future) | +10 | When helping classmate |
- XP multipliers:
  - 1.5x for Show Your Thinking mode
  - 2x for streak days beyond 7
  - 1.25x for harder quiz difficulty
- XP history with source attribution (what earned it, when, how much)
- XP is earned, never lost (engagement-positive design)
- **Acceptance Criteria**: XP awards trigger in real-time after qualifying actions; XP total visible in header; history shows last 100 transactions

### 3.1.2 Level System — P0
- Age-themed level names (5 levels per grade band):
  | Band | Lvl 1 | Lvl 2 | Lvl 3 | Lvl 4 | Lvl 5 |
  |------|-------|-------|-------|-------|-------|
  | K-2 | Seedling | Sprout | Bloom | Garden | Rainbow |
  | 3-5 | Learner | Explorer | Achiever | Champion | Master |
  | 6-8 | Rookie | Contender | Warrior | Legend | GOAT |
  | 9-12 | Apprentice | Scholar | Expert | Visionary | Polymath |
- XP thresholds per level: 0, 100, 300, 700, 1500
- Level-up triggers celebration animation (confetti + tutor message)
- Level displayed as badge next to username throughout the app
- **Acceptance Criteria**: Level auto-updates when XP threshold crossed; celebration plays once; level persists across sessions

### 3.1.3 Daily Streaks — P0
- Track consecutive days with qualifying activity (≥1 session OR ≥1 quiz OR ≥5 flashcard reviews)
- Streak freeze tokens:
  - Earned by reaching 50 XP in a single day
  - Max 3 stored
  - Auto-consumed when a day is missed (if available)
- Streak shield: One free miss per 30-day period (no freeze token needed)
- GitHub-style calendar heatmap visualization:
  - Green intensity = activity level (1-4 scale)
  - Freeze days shown in blue
  - Missed days in gray
  - Current streak highlighted
- Milestone celebrations at 7, 14, 30, 60, 100, 365 days
- **Acceptance Criteria**: Streak updates daily at midnight UTC; freeze auto-applies; heatmap shows last 365 days; milestone triggers badge + XP bonus

### 3.1.4 Badge System — P1
- Badge categories:
  | Category | Examples |
  |----------|---------|
  | Achievement | First Step, 7-Day Streak, Deep Thinker, Sharpshooter (10 quizzes 100%) |
  | Subject | Master of Math, Science Sage, Word Wizard, History Hero |
  | Effort | Persistence (5 attempts), Night Owl (late study), Early Bird |
  | Social | Helpful (peer help), Team Player (class challenge) |
  | Special | Seasonal events, teacher-awarded, milestone |
- Badge display: profile page, badge gallery (grid), mini-badge row on dashboard
- Badge rarity: Common, Rare, Epic, Legendary (visual distinction)
- Badge notification: toast popup when earned, unread indicator on profile
- Teacher can create custom class badges
- **Acceptance Criteria**: Badges evaluate after each qualifying action; toast shows immediately; gallery shows all badges (earned glowing, locked grayed with hint)

### 3.1.5 Leaderboard — P1
- **Opt-in only** (FERPA compliance — no student is on a leaderboard without explicit consent)
- Scoped to class level (no cross-school, no global)
- Weekly reset cycle (resets Sunday midnight UTC)
- Ranking by XP earned that week (not cumulative)
- Anonymous mode: student appears as "Learner #42" instead of name
- Top 3 visual distinction (gold/silver/bronze)
- Teacher can disable leaderboard for their class
- **Acceptance Criteria**: Only shows opted-in students; resets weekly; teacher toggle works; anonymous mode hides identity

### 3.1.6 XP Multipliers & Bonus Events — P2
- Time-limited bonus events (2x XP weekend, subject spotlight week)
- Teacher-configurable multipliers per assignment
- Multiplier stacking rules (max 3x cap)
- Visual indicator when multiplier is active
- **Acceptance Criteria**: Multipliers apply correctly in XP calculation; visual indicator in header; event schedule manageable by admin

### 3.1.7 Celebrations & Animations — P1
- Confetti animation on level-up (canvas-confetti library or CSS)
- Tutor persona congratulatory message (contextual to achievement)
- Optional sound effects (toggle in user settings, default OFF)
- Progress milestone popups (e.g., "You've answered 100 questions!")
- Respect `prefers-reduced-motion` — fall back to subtle fade
- Age-adapted celebrations:
  - K-2: Larger animations, fun characters, stickers
  - 3-5: Badge unlock animations, sparkle effects
  - 6-8: Clean achievement banners
  - 9-12: Minimal toast notifications
- **Acceptance Criteria**: Animations play at correct triggers; sound toggle works; reduced-motion respected; age-band appropriate

### 3.1.8 Gamification Dashboard Widget — P0
- Compact widget on student home page showing:
  - Current streak count (with flame icon)
  - XP this week / total XP
  - Level + progress bar to next level
  - Recent badges (last 3 earned)
  - Leaderboard position (if opted in)
- Expandable to full gamification dashboard
- **Acceptance Criteria**: Widget loads on dashboard; data updates in real-time; click expands to full view

### 3.1.9 Challenge Modes — P2
- **Daily Challenge**: Curated hard problem, 50 XP bonus, new every day at midnight UTC
  - AI-generated based on student's weakest topics
  - Time-limited (complete within 24 hours)
- **Weekly Class Challenge**: Teacher creates, assigns to class
  - Subject/topic scoped
  - Class-wide leaderboard for the challenge
  - XP bonus for completion, extra for top 3
- **Friend Challenge (1v1)**: Student invites classmate to quiz race
  - Same questions, timed
  - Both earn XP, winner gets bonus
  - Requires both students in same class
- **Acceptance Criteria**: Daily challenge refreshes at midnight; teacher can create/manage class challenges; friend invite works; results show for both participants

### 3.1.10 Reward Marketplace — P2
- Students spend XP on cosmetic rewards:
  | Category | Examples | XP Cost Range |
  |----------|---------|---------------|
  | Avatar Accessories | Hats, glasses, pets | 50-500 |
  | Theme Colors | Custom accent colors | 100-300 |
  | Persona Unlocks | Special tutor personas | 500-1000 |
  | Profile Frames | Decorative borders | 200-500 |
  | Celebration Styles | Custom confetti patterns | 150-400 |
- XP spent does NOT reduce level (levels are permanent)
- Teacher/admin can configure which rewards are available
- Seasonal/limited-time rewards
- **Acceptance Criteria**: Purchase deducts XP; reward applies immediately; level unaffected; inventory persists

---

## 4. Pages, Views, and UI Components

### 4.1 Page Inventory

| Page | Route | Access Role | Description |
|------|-------|-------------|-------------|
| Gamification Dashboard | `/dashboard/gamification` | student | Full gamification overview |
| Leaderboard | `/dashboard/leaderboard` | student | Class leaderboard with opt-in |
| Badge Gallery | `/dashboard/badges` | student | All badges (earned + locked) |
| Challenge Hub | `/dashboard/challenges` | student | Daily/weekly/friend challenges |
| Reward Marketplace | `/dashboard/rewards` | student | Browse and purchase rewards |
| Teacher Gamification | `/teacher/gamification` | teacher | Class gamification settings |
| Teacher Challenges | `/teacher/challenges` | teacher | Create/manage challenges |

### 4.2 Layout Mockup Descriptions

#### Gamification Dashboard (`/dashboard/gamification`)
**Desktop (>1024px)**:
- Top bar: Current level badge + XP count + streak flame + leaderboard rank (inline)
- Left column (60%):
  - Streak calendar heatmap (52 weeks × 7 days grid)
  - XP history chart (line graph, last 30 days)
  - Recent activity feed (last 10 XP transactions)
- Right column (40%):
  - Level progress card (circular progress ring, level name, XP to next)
  - Badge showcase (last 4 earned, "View All" link)
  - Active challenges card (daily + any class challenges)
  - Quick links: Leaderboard, Marketplace, Challenges

**Tablet (640-1024px)**:
- Stats row at top (level, XP, streak, rank — horizontal cards)
- Single column below: calendar heatmap (compressed), badge row (horizontal scroll), challenges, activity feed

**Mobile (<640px)**:
- Sticky header: streak flame + XP count
- Swipeable stat cards (level, badges, rank)
- Calendar heatmap as mini 4-week view (expandable)
- Stacked cards: challenges, recent activity
- Bottom floating button: "Earn XP" → navigates to learning activities

#### Badge Gallery (`/dashboard/badges`)
**Desktop**: Grid layout (4 columns). Each badge card: icon (64x64), name, description, rarity border color, earned date or "How to earn" hint. Filter tabs: All | Earned | Locked | By Category
**Tablet**: 3-column grid
**Mobile**: 2-column grid, larger tap targets

#### Leaderboard (`/dashboard/leaderboard`)
**Desktop**: Table layout. Columns: Rank | Avatar + Name | XP This Week | Level | Streak. Top 3 highlighted with gold/silver/bronze. Opt-in toggle at top. Class selector dropdown.
**Tablet**: Same table, slightly compressed
**Mobile**: Card list (one student per row). Rank, name, XP. Top 3 as featured cards at top.

#### Reward Marketplace (`/dashboard/rewards`)
**Desktop**: Grid of reward cards (3 columns). Each card: preview image, name, XP cost, "Purchase" button. Category tabs: Avatars | Themes | Personas | Frames | Celebrations. Student's XP balance shown in sticky header.
**Mobile**: 2-column grid. Sticky XP balance bar at top.

### 4.3 Component Hierarchy

```
components/gamification/
├── GamificationWidget.tsx        (compact dashboard widget for home page)
├── GamificationDashboard.tsx     (full dashboard page)
├── XPDisplay.tsx                 (XP count with animation on change)
├── LevelBadge.tsx                (level icon + name, used everywhere)
├── LevelProgressRing.tsx         (circular progress to next level)
├── StreakCounter.tsx              (flame icon + day count)
├── StreakCalendar.tsx             (GitHub-style heatmap)
├── BadgeCard.tsx                  (individual badge display)
├── BadgeGallery.tsx              (grid of all badges)
├── BadgeToast.tsx                (notification when badge earned)
├── LeaderboardTable.tsx          (class leaderboard)
├── LeaderboardOptIn.tsx          (consent toggle)
├── ChallengeCard.tsx             (daily/weekly/friend challenge)
├── ChallengeHub.tsx              (all challenges page)
├── FriendChallengeInvite.tsx     (invite flow for 1v1)
├── RewardCard.tsx                (marketplace item)
├── RewardMarketplace.tsx         (full marketplace page)
├── CelebrationOverlay.tsx        (confetti + level-up animation)
└── XPMultiplierBanner.tsx        (shows active multiplier)
```

---

## 5. Backend API Endpoints

| Method | Path | Description | Auth | Rate Limit |
|--------|------|-------------|------|------------|
| GET | `/api/gamification/profile` | XP, level, streak, badges, rank | student | 60/min |
| GET | `/api/gamification/xp/history` | XP transaction history (paginated) | student | 30/min |
| POST | `/api/gamification/xp/award` | Award XP (internal — called by other services) | internal | N/A |
| GET | `/api/gamification/streak` | Streak details + freeze token count | student | 60/min |
| POST | `/api/gamification/streak/freeze` | Manually use a streak freeze | student | 5/min |
| GET | `/api/gamification/badges` | All badges with earned status | student | 30/min |
| GET | `/api/gamification/leaderboard/{class_id}` | Class leaderboard (weekly) | student | 30/min |
| PUT | `/api/gamification/leaderboard/opt-in` | Toggle leaderboard opt-in | student | 10/min |
| GET | `/api/gamification/challenges/daily` | Today's daily challenge | student | 30/min |
| POST | `/api/gamification/challenges/daily/submit` | Submit daily challenge answer | student | 10/min |
| GET | `/api/gamification/challenges/class/{class_id}` | Class challenges | student | 30/min |
| POST | `/api/gamification/challenges/friend/invite` | Invite friend to 1v1 | student | 10/min |
| POST | `/api/gamification/challenges/friend/{id}/accept` | Accept friend challenge | student | 10/min |
| GET | `/api/gamification/rewards` | Available rewards catalog | student | 30/min |
| POST | `/api/gamification/rewards/{id}/purchase` | Purchase a reward | student | 10/min |
| GET | `/api/gamification/rewards/inventory` | Student's purchased rewards | student | 30/min |
| GET | `/api/teacher/gamification/settings/{class_id}` | Teacher: class gamification config | teacher | 30/min |
| PUT | `/api/teacher/gamification/settings/{class_id}` | Teacher: update config | teacher | 10/min |
| POST | `/api/teacher/challenges` | Teacher: create class challenge | teacher | 10/min |
| GET | `/api/teacher/challenges/{class_id}` | Teacher: list class challenges | teacher | 30/min |

---

## 6. Database Schema Additions

```sql
-- Leverage existing tables: student_xp, xp_transactions, badges, student_badges

-- New tables for Phase 3.1:

CREATE TABLE IF NOT EXISTS challenges (
    id              SERIAL PRIMARY KEY,
    type            VARCHAR(30) NOT NULL CHECK (type IN ('daily', 'weekly', 'friend')),
    class_id        INTEGER REFERENCES classes(id),
    creator_id      INTEGER REFERENCES tutor_users(id),
    subject         VARCHAR(255),
    topic           VARCHAR(255),
    difficulty      SMALLINT DEFAULT 3 CHECK (difficulty BETWEEN 1 AND 5),
    config_json     JSONB NOT NULL DEFAULT '{}',
    xp_reward       INTEGER DEFAULT 50,
    active_from     TIMESTAMPTZ NOT NULL,
    active_until    TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_challenges_type_active ON challenges(type, active_from, active_until);
CREATE INDEX idx_challenges_class ON challenges(class_id);

CREATE TABLE IF NOT EXISTS challenge_attempts (
    id              SERIAL PRIMARY KEY,
    challenge_id    INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    answers_json    JSONB,
    score           INTEGER,
    time_taken_ms   INTEGER,
    completed       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(challenge_id, student_id)
);
CREATE INDEX idx_challenge_attempts_student ON challenge_attempts(student_id);

CREATE TABLE IF NOT EXISTS reward_items (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    type            VARCHAR(50) NOT NULL CHECK (type IN ('avatar', 'theme', 'persona_unlock', 'frame', 'celebration')),
    xp_cost         INTEGER NOT NULL CHECK (xp_cost > 0),
    asset_url       VARCHAR(1000),
    rarity          VARCHAR(20) DEFAULT 'common' CHECK (rarity IN ('common', 'rare', 'epic', 'legendary')),
    is_seasonal     BOOLEAN DEFAULT FALSE,
    available_from  TIMESTAMPTZ,
    available_until TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS student_rewards (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    reward_id       INTEGER NOT NULL REFERENCES reward_items(id),
    xp_spent        INTEGER NOT NULL,
    equipped        BOOLEAN DEFAULT FALSE,
    purchased_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_id, reward_id)
);
CREATE INDEX idx_student_rewards_student ON student_rewards(student_id);

-- Add streak_freeze_tokens column to student_xp if not exists
-- ALTER TABLE student_xp ADD COLUMN IF NOT EXISTS streak_freeze_tokens INTEGER DEFAULT 0;
-- ALTER TABLE student_xp ADD COLUMN IF NOT EXISTS streak_shield_used_at TIMESTAMPTZ;
-- ALTER TABLE student_xp ADD COLUMN IF NOT EXISTS leaderboard_opt_in BOOLEAN DEFAULT FALSE;
-- ALTER TABLE student_xp ADD COLUMN IF NOT EXISTS leaderboard_anonymous BOOLEAN DEFAULT FALSE;

-- Gamification settings per class
CREATE TABLE IF NOT EXISTS class_gamification_settings (
    id              SERIAL PRIMARY KEY,
    class_id        INTEGER NOT NULL REFERENCES classes(id) UNIQUE,
    leaderboard_enabled BOOLEAN DEFAULT TRUE,
    challenges_enabled  BOOLEAN DEFAULT TRUE,
    marketplace_enabled BOOLEAN DEFAULT TRUE,
    xp_multiplier   REAL DEFAULT 1.0,
    custom_badges_json JSONB DEFAULT '[]',
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 7. Service Layer Architecture

### New File: `backend/app/services/gamification.py`

```
class GamificationService:
    async award_xp(student_id, action_type, base_xp, metadata) → XPTransaction
    async get_profile(student_id) → GamificationProfile
    async check_and_update_streak(student_id) → StreakStatus
    async use_streak_freeze(student_id) → bool
    async evaluate_badges(student_id) → list[Badge]
    async get_leaderboard(class_id, week_start) → list[LeaderboardEntry]
    async toggle_leaderboard_opt_in(student_id, opt_in, anonymous) → None
    async get_daily_challenge(student_id) → Challenge
    async generate_daily_challenge() → Challenge  # Celery-triggered
    async submit_challenge_attempt(student_id, challenge_id, answers) → ChallengeResult
    async create_friend_challenge(inviter_id, invitee_id, config) → Challenge
    async get_rewards_catalog(filters) → list[RewardItem]
    async purchase_reward(student_id, reward_id) → StudentReward
    async get_student_inventory(student_id) → list[StudentReward]
```

### Integration Points with Existing Services:
- `adaptive_quiz.py`: After quiz submission → `award_xp("quiz_correct", 5)` per correct answer
- `flashcards.py`: After card review → `award_xp("flashcard_review", 2)`
- `mastery_tracking.py`: After mastery level change → `award_xp("mastery_up", 25)`
- `chat_execution.py`: After session ≥5 min → `award_xp("session_complete", 10)`
- `hint_progression.py`: After Show Your Thinking → `award_xp("show_thinking", 15)`

### New Router: `backend/app/routers/gamification.py`
- Mounts at `/api/gamification/`
- All endpoints require `student` role (except teacher endpoints)
- Teacher gamification endpoints in `backend/app/routers/teacher_gamification.py`

---

## 8. Celery Task Definitions

| Task | Trigger | Frequency | Description |
|------|---------|-----------|-------------|
| `generate_daily_challenge` | Cron | Daily at 00:00 UTC | Generates next day's challenge for each active student |
| `reset_weekly_leaderboard` | Cron | Sunday 00:00 UTC | Archives current leaderboard, resets weekly XP |
| `check_streaks` | Cron | Daily at 00:05 UTC | Checks all active streaks, applies freezes, breaks streaks |
| `evaluate_badge_candidates` | Event | After XP award | Checks if student qualifies for new badges |

---

## 9. State Management (Frontend)

### New Store: `frontend/stores/gamification-store.ts`

```typescript
interface GamificationState {
  // Profile
  xp: number;
  level: number;
  levelName: string;
  xpToNextLevel: number;

  // Streak
  streakDays: number;
  freezeTokens: number;
  streakCalendar: Record<string, number>; // date → activity level

  // Badges
  badges: Badge[];
  unreadBadges: Badge[];

  // Leaderboard
  leaderboardOptIn: boolean;
  leaderboardRank: number | null;

  // Challenges
  dailyChallenge: Challenge | null;
  classChallenges: Challenge[];
  friendChallenges: Challenge[];

  // Rewards
  inventory: RewardItem[];
  xpSpendable: number; // XP available for marketplace

  // Actions
  fetchProfile: () => Promise<void>;
  awardXPOptimistic: (amount: number) => void;
  fetchBadges: () => Promise<void>;
  dismissBadgeNotification: (badgeId: number) => void;
  fetchLeaderboard: (classId: number) => Promise<void>;
  fetchDailyChallenge: () => Promise<void>;
  purchaseReward: (rewardId: number) => Promise<void>;
}
```

---

## 10. Integration Points with Existing Systems

| System | Integration |
|--------|------------|
| Auth/RBAC | Student role required; teacher role for management |
| Mastery Tracker | Mastery level-up triggers XP award |
| Adaptive Quiz | Correct answers trigger XP; quiz difficulty affects multiplier |
| Flashcards | Card reviews trigger XP |
| Chat Execution | Session completion triggers XP |
| Hint Progression | Show Your Thinking triggers bonus XP |
| Parent Dashboard (3.2) | Parent sees child's XP, streak, badges |
| Gaming Engine (3.5) | Games award XP; game leaderboard feeds into main leaderboard |
| Test Prep (3.6) | Mock test completion awards XP |

---

## 11. Real-Time and Streaming Requirements

| Feature | Mechanism | Event Schema |
|---------|-----------|-------------|
| XP award notification | SSE (via existing chat stream pattern) | `{type: "xp_award", amount, total, source}` |
| Badge earned notification | SSE | `{type: "badge_earned", badge: {id, name, icon, rarity}}` |
| Level-up notification | SSE | `{type: "level_up", newLevel, levelName}` |
| Leaderboard update | Polling (30s interval) | Standard REST response |
| Friend challenge invite | SSE | `{type: "challenge_invite", challenger, config}` |

---

## 12. Testing Strategy

### Backend Tests (`backend/tests/test_gamification.py`)
- XP award calculation with multipliers
- Streak check/update logic (normal, freeze, shield, break)
- Badge evaluation (each badge type)
- Leaderboard ranking with opt-in/anonymous
- Challenge CRUD and submission
- Reward purchase (sufficient XP, insufficient XP, duplicate)

### Frontend E2E (`frontend/e2e/gamification.spec.ts`)
- Student views gamification dashboard
- XP increases after quiz
- Streak calendar renders correctly
- Badge gallery shows earned/locked
- Leaderboard opt-in toggle
- Reward purchase flow
- Daily challenge completion

---

## 13. Deployment Considerations

- **New env vars**: None required (uses existing DB/Redis)
- **Redis keys**: `streak:{student_id}`, `leaderboard:{class_id}:{week}`, `daily_challenge:{date}`
- **Celery beat**: Add 3 new periodic tasks to celery beat schedule
- **Migration**: `backend/db/migrations/2026-03-XX_gamification_tables.sql`

---

## 14. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Gamification fatigue | Students ignore rewards | Age-adaptive rewards; teacher can adjust; variety in challenge types |
| Leaderboard anxiety | Weaker students demotivated | Opt-in only; weekly reset; anonymous mode; effort-based not just performance |
| XP inflation | Meaningless numbers | Cap multipliers at 3x; periodic reward cost rebalancing |
| FERPA compliance | Leaderboard exposure | Opt-in consent; class-scoped; anonymous mode; teacher control |

---

## 15. Implementation Checklist

- [ ] `3.1.1` XP system — backend service + DB + API endpoints
- [ ] `3.1.1` XP system — frontend XPDisplay component + integration with quiz/flashcard/chat
- [ ] `3.1.2` Level system — backend level calculation + API
- [ ] `3.1.2` Level system — frontend LevelBadge + LevelProgressRing + CelebrationOverlay
- [ ] `3.1.3` Daily streaks — backend streak tracking + freeze logic + Celery task
- [ ] `3.1.3` Daily streaks — frontend StreakCounter + StreakCalendar
- [ ] `3.1.4` Badge system — backend badge definitions + evaluation engine
- [ ] `3.1.4` Badge system — frontend BadgeGallery + BadgeToast
- [ ] `3.1.5` Leaderboard — backend ranking + opt-in/anonymous + weekly reset
- [ ] `3.1.5` Leaderboard — frontend LeaderboardTable + LeaderboardOptIn
- [ ] `3.1.6` XP multipliers — backend multiplier logic + event system
- [ ] `3.1.7` Celebrations — frontend CelebrationOverlay + age-adaptive + reduced motion
- [ ] `3.1.8` Gamification dashboard widget — frontend GamificationWidget on home page
- [ ] `3.1.8` Gamification dashboard — full page `/dashboard/gamification`
- [ ] `3.1.9` Challenge modes — backend daily/class/friend challenges + Celery generation
- [ ] `3.1.9` Challenge modes — frontend ChallengeHub + ChallengeCard + FriendChallengeInvite
- [ ] `3.1.10` Reward marketplace — backend catalog + purchase + inventory
- [ ] `3.1.10` Reward marketplace — frontend RewardMarketplace + RewardCard
- [ ] `3.1.T` Teacher gamification settings + challenge management pages
- [ ] `3.1.E2E` Playwright E2E tests for gamification flows
- [ ] `3.1.INT` Integration testing — XP awards from quiz, flashcard, mastery, chat
