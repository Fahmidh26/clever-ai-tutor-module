# Functional Phase 3.5: Educational Gaming Engine

> **Status**: Not Started
> **Estimated Duration**: 3 weeks
> **Dependencies**: FP 3.1 (gamification/XP system), Phase 2 (mastery tracker, misconception engine, quiz engine)
> **Sprint Reference**: Sprint 3.5 in AI_TUTOR_MODULE.md (Section 22.5)
> **Priority**: P1 — Medium (high engagement for K-8, differentiated learning)

---

## 1. Executive Summary

The Educational Gaming Engine transforms learning into play through 32 game templates across 4 age bands. Unlike generic educational games, every game is deeply integrated with the mastery tracking system — each correct/incorrect answer feeds the shared intelligence layer, and game content adapts to each student's zone of proximal development (ZPD). Teachers can assign games for remediation, and the system recommends games based on learning gaps. This is not gamification (that's FP 3.1) — this is actual game-based learning where the game IS the lesson.

---

## 2. Target Users and Personas

| User Type | Goals | How This Phase Serves Them |
|-----------|-------|---------------------------|
| **Student (K-2)** | Fun, play-based learning | Story adventures, matching games, virtual pets |
| **Student (3-5)** | Engaging practice, competition | RPG quests, building games, mystery detective |
| **Student (6-8)** | Challenge, social gaming | Escape rooms, civilization builder, coding maze |
| **Student (9-12)** | Real-world simulation, depth | Business sim, debate tournament, stock market |
| **Teacher** | Targeted remediation, engagement | Assign games to learning gaps, view game analytics |
| **Parent** | See learning through play | Game activity visible in parent dashboard |

---

## 3. Features and Sub-Features

### 3.5.1 Game Framework Architecture — P0
- **Template Registry**: JSON-defined game templates
  ```json
  {
    "id": "story_adventure_k2",
    "name": "Story Adventure",
    "ageBand": "K-2",
    "type": "narrative",
    "subjects": ["reading", "science", "social_studies"],
    "minQuestions": 5,
    "maxQuestions": 15,
    "timeLimit": null,
    "xpReward": 30,
    "uiComponent": "StoryAdventureGame"
  }
  ```
- **Game Session Management**:
  - Start: create session, generate age/subject-appropriate content via AI
  - Play: present questions/interactions within game context
  - Answer: validate, update mastery, award XP
  - Complete: show results, update mastery map, award XP/badges
- **Adaptive Difficulty (ZPD Engine)**:
  - Uses mastery data to select questions in the "zone of proximal development"
  - Just challenging enough: 70-80% expected success rate
  - Dynamic: adjusts mid-game based on performance
  - Prevents boredom (too easy) and frustration (too hard)
- **AI Content Generation**:
  - AI generates game-appropriate questions per subject/topic
  - Story contexts, character dialogue, scenario descriptions
  - Culturally diverse and inclusive content
- **Acceptance Criteria**: Games load in <3s; adaptive difficulty adjusts within 3 questions; mastery updates in real-time; all 4 age bands have at least 4 working games

### 3.5.2 K-2 Game Templates (Ages 5-7) — P0

| Game | Type | Mechanic | Subjects |
|------|------|----------|----------|
| **Story Adventure** | Narrative | Choose-your-path story; each choice requires answering a question | Reading, Science, Social Studies |
| **Matching Game** | Memory | Flip cards to match concepts (word↔picture, math↔answer, cause↔effect) | All subjects |
| **Virtual Pet** | Nurture | Feed/care for a pet by answering correctly; pet grows with streaks | Math, Science |
| **Treasure Hunt** | Exploration | Navigate map, solve problems at each location to unlock treasure | Math, Geography |

**K-2 UI Characteristics**:
- Extra-large touch targets (min 64px)
- Bright, vibrant colors with rounded shapes
- Character-driven (friendly animals, robots, fantasy creatures)
- Audio narration for non-readers (TTS for all text)
- Drag-and-drop interactions over typing
- Celebration animations after every correct answer
- No time pressure (no timers for K-2)

### 3.5.3 3-5 Game Templates (Ages 8-10) — P0

| Game | Type | Mechanic | Subjects |
|------|------|----------|----------|
| **RPG Quest** | Adventure | Character goes on quest; battles = quiz questions; XP/equipment rewards | All |
| **Building Game** | Construction | Build structures by earning materials through correct answers | Math, Science, Engineering |
| **Mystery Detective** | Investigation | Solve a mystery by gathering clues (correct answers = new clues) | Reading, Science, Logic |
| **Fraction Pizza Shop** | Simulation | Run a pizza shop; customers order fractions of pizzas | Math (Fractions) |

**3-5 UI Characteristics**:
- Large but standard touch targets (48px)
- Story-driven with character progression
- Simple inventory/collection mechanics
- Light competition (personal best, optional class ranking)
- Timer optional (teacher-configurable)

### 3.5.4 6-8 Game Templates (Ages 11-13) — P1

| Game | Type | Mechanic | Subjects |
|------|------|----------|----------|
| **Escape Room** | Puzzle | Solve increasingly hard puzzles to "escape"; wrong answers add time penalty | All |
| **Civilization Builder** | Strategy | Build a civilization; research = real knowledge, resources = correct answers | History, Science, Economics |
| **Coding Maze** | Logic | Navigate a maze by writing simple code (if/else, loops) | Computer Science, Math |
| **Speed Challenge** | Competition | Timed quiz race; accuracy + speed = score | All subjects |

**6-8 UI Characteristics**:
- Standard UI components
- Timer-based challenges available
- Multiplayer support (paired, class)
- Progress tracking with analytics
- Achievement system integration

### 3.5.5 9-12 Game Templates (Ages 14-18) — P1

| Game | Type | Mechanic | Subjects |
|------|------|----------|----------|
| **Business Simulation** | Simulation | Run a company; make decisions requiring subject knowledge | Economics, Math, Business |
| **Debate Tournament** | Argumentation | AI opponents with different viewpoints; argue with evidence | History, Literature, Ethics |
| **Case Study Mystery** | Analysis | Analyze real-world scenarios; apply knowledge to diagnose/solve | Science, Medicine, Law |
| **Stock Market Sim** | Finance | Virtual stock trading with real concepts (supply/demand, risk) | Math, Economics |

**9-12 UI Characteristics**:
- Professional, clean design
- Data visualization (charts, graphs in sims)
- Long-form gameplay (15-30 min sessions)
- Portfolio/progress tracking
- Real-world application emphasis

### 3.5.6 Multiplayer Modes — P2
- **Class Challenge**: Teacher creates, entire class plays same game simultaneously
  - Class leaderboard during game
  - Teacher sees real-time participation
- **Paired Learning**: Two students collaborate on a game
  - Assigned by teacher or self-selected
  - Complementary roles (one explains, other answers)
- **Friend Challenge**: 1v1 game race
  - Same questions, same difficulty
  - Split-screen view of progress
  - Real-time via WebSocket
- **AI Opponent**: Practice against AI at adjustable difficulty
  - AI makes intentional "mistakes" at easier levels
  - Helps students learn from AI's reasoning

### 3.5.7 Teacher Game Management — P1
- **Assign Games**: Select game + subject/topic + assign to class/students
- **Custom Game Config**: Adjust difficulty, time limit, question count, allowed subjects
- **Game Analytics Dashboard**:
  - Completion rates per game
  - Average score by topic (identify class-wide gaps)
  - Time spent per game
  - Mastery impact (did the game improve mastery scores?)
  - Most/least effective games
- **Remediation Recommendations**: AI suggests specific games for specific students based on misconceptions

### 3.5.8 AI Game Recommendations — P1
- **Smart Recommendation Engine**:
  - Analyzes student's mastery gaps, misconceptions, learning style
  - Recommends the best game + topic combination
  - "You're struggling with fractions — try Fraction Pizza Shop!"
  - Updates recommendations as student improves
- **Pathway Selector**:
  - Student chooses preferred learning modality:
    - Chat (traditional tutoring)
    - Quiz (adaptive quiz)
    - Game (educational game)
    - Audio (listen to lesson)
    - Test Prep (practice tests)
  - AI pre-selects the most effective modality based on student data
  - Shown at session start or after topic selection

---

## 4. Pages, Views, and UI Components

### 4.1 Page Inventory

| Page | Route | Access Role | Description |
|------|-------|-------------|-------------|
| Game Hub | `/games` | student | Browse all games, recommendations |
| Game Browser | `/games/browse` | student | Filter by age, subject, type |
| Game Play | `/games/play/{template_id}/{session_id}` | student | Active game session |
| Game Results | `/games/{session_id}/results` | student | Post-game results + mastery impact |
| Game History | `/games/history` | student | Past game sessions |
| Game Leaderboard | `/games/leaderboard` | student | Game-specific rankings |
| Pathway Selector | `/learn` | student | Choose learning modality |
| Teacher Game Dashboard | `/teacher/games` | teacher | Assign + manage games |
| Teacher Game Analytics | `/teacher/games/analytics` | teacher | Game effectiveness data |

### 4.2 Layout Mockup Descriptions

#### Game Hub (`/games`)
**Desktop**: Hero section with "Recommended for You" (AI picks, 3 cards). Below: "Continue Playing" row (in-progress games). Grid of game category cards (by age band). Each game card: cover art, name, subjects, difficulty stars, XP reward. Right sidebar: quick stats (games played, win rate, XP from games).
**Tablet**: Same layout, 2-column grid.
**Mobile**: Vertical list. Recommended as horizontal scroll at top. Categories as collapsible sections.

#### Game Play (`/games/play/{template_id}/{session_id}`)
**Desktop**: Full-viewport immersive experience. Game-specific layout (varies by template). Persistent header: game name, progress bar, score, timer (if applicable). Pause button → overlay with resume/quit options.
**Mobile**: Full-screen game. Controls designed for touch. Portrait mode for card/quiz games, landscape hint for spatial games.

#### Game Results (`/games/{session_id}/results`)
**Desktop**: Two-column. Left: Score, XP earned, time, accuracy. Right: Mastery impact chart (before vs after), specific topics improved, badges earned. Bottom: "Play Again", "Try Different Game", "Back to Hub" buttons.
**Mobile**: Single column, stacked cards. Celebration animation at top.

#### Pathway Selector (`/learn`)
**Desktop**: 5 large modality cards in a row: Chat (speech icon), Quiz (question icon), Game (controller icon), Audio (headphone icon), Test Prep (exam icon). Each card: brief description, AI recommendation badge if suggested. Below: topic selector (if not already chosen).
**Mobile**: Vertical stack of modality cards. AI recommendation highlighted with glow effect.

### 4.3 Component Hierarchy

```
components/games/
├── GameHub.tsx                   (main hub page)
├── GameCard.tsx                  (game preview card)
├── GameBrowser.tsx               (filtered browse page)
├── GameResults.tsx               (post-game results)
├── GameHistory.tsx               (history page)
├── GameLeaderboard.tsx           (game-specific rankings)
├── PathwaySelector.tsx           (learning modality chooser)
├── GameRecommendation.tsx        (AI recommendation card)
│
├── engine/
│   ├── GameSession.tsx           (game session wrapper)
│   ├── GameHeader.tsx            (progress, score, timer)
│   ├── GameQuestion.tsx          (question presentation)
│   ├── GameFeedback.tsx          (correct/incorrect feedback)
│   ├── GamePause.tsx             (pause overlay)
│   └── GameComplete.tsx          (completion screen)
│
├── templates/
│   ├── k2/
│   │   ├── StoryAdventureGame.tsx
│   │   ├── MatchingGame.tsx
│   │   ├── VirtualPetGame.tsx
│   │   └── TreasureHuntGame.tsx
│   ├── grade3_5/
│   │   ├── RPGQuestGame.tsx
│   │   ├── BuildingGame.tsx
│   │   ├── MysteryDetectiveGame.tsx
│   │   └── FractionPizzaGame.tsx
│   ├── grade6_8/
│   │   ├── EscapeRoomGame.tsx
│   │   ├── CivilizationBuilderGame.tsx
│   │   ├── CodingMazeGame.tsx
│   │   └── SpeedChallengeGame.tsx
│   └── grade9_12/
│       ├── BusinessSimGame.tsx
│       ├── DebateTournamentGame.tsx
│       ├── CaseStudyGame.tsx
│       └── StockMarketGame.tsx
│
├── multiplayer/
│   ├── MultiplayerLobby.tsx
│   ├── FriendChallenge.tsx
│   └── ClassChallenge.tsx
│
└── teacher/
    ├── TeacherGameDashboard.tsx
    ├── GameAssignmentForm.tsx
    └── GameAnalytics.tsx
```

---

## 5. Backend API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/games/templates` | List all game templates (filtered by age/subject) | student |
| GET | `/api/games/templates/{id}` | Get game template details | student |
| GET | `/api/games/recommendations` | AI-recommended games for student | student |
| POST | `/api/games/sessions` | Start a new game session | student |
| GET | `/api/games/sessions/{id}` | Get game session state | student |
| POST | `/api/games/sessions/{id}/answer` | Submit answer in game | student |
| POST | `/api/games/sessions/{id}/complete` | Complete game session | student |
| GET | `/api/games/sessions/{id}/results` | Get game results + mastery impact | student |
| GET | `/api/games/history` | Student's game history | student |
| GET | `/api/games/leaderboard/{template_id}` | Game-specific leaderboard | student |
| POST | `/api/games/multiplayer/create` | Create multiplayer lobby | student |
| POST | `/api/games/multiplayer/{id}/join` | Join multiplayer game | student |
| GET | `/api/games/pathway/recommend` | AI: recommend learning modality | student |
| POST | `/api/teacher/games/assign` | Assign game to class/students | teacher |
| GET | `/api/teacher/games/assignments/{class_id}` | List game assignments | teacher |
| GET | `/api/teacher/games/analytics/{class_id}` | Game effectiveness analytics | teacher |
| GET | `/api/teacher/games/remediation/{class_id}` | AI remediation recommendations | teacher |

---

## 6. Database Schema Additions

```sql
CREATE TABLE IF NOT EXISTS game_templates (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT,
    age_band        VARCHAR(10) NOT NULL CHECK (age_band IN ('K-2', '3-5', '6-8', '9-12')),
    game_type       VARCHAR(50) NOT NULL,
    subjects        TEXT[] NOT NULL,
    ui_component    VARCHAR(100) NOT NULL,
    config_json     JSONB NOT NULL DEFAULT '{}',
    min_questions   INTEGER DEFAULT 5,
    max_questions   INTEGER DEFAULT 20,
    time_limit_seconds INTEGER,
    xp_reward       INTEGER DEFAULT 30,
    cover_image_url VARCHAR(1000),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_game_templates_band ON game_templates(age_band, is_active);

CREATE TABLE IF NOT EXISTS game_sessions (
    id              SERIAL PRIMARY KEY,
    template_id     INTEGER NOT NULL REFERENCES game_templates(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    class_id        INTEGER REFERENCES classes(id),
    subject         VARCHAR(255),
    topic           VARCHAR(255),
    difficulty      SMALLINT DEFAULT 3,
    questions_json  JSONB NOT NULL DEFAULT '[]',
    answers_json    JSONB DEFAULT '[]',
    game_state_json JSONB DEFAULT '{}',
    score           INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    time_taken_ms   INTEGER,
    completed       BOOLEAN DEFAULT FALSE,
    xp_awarded      INTEGER DEFAULT 0,
    multiplayer_id  INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);
CREATE INDEX idx_game_sessions_student ON game_sessions(student_id, created_at DESC);
CREATE INDEX idx_game_sessions_template ON game_sessions(template_id);

CREATE TABLE IF NOT EXISTS game_assignments (
    id              SERIAL PRIMARY KEY,
    teacher_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    class_id        INTEGER NOT NULL REFERENCES classes(id),
    template_id     INTEGER NOT NULL REFERENCES game_templates(id),
    subject         VARCHAR(255),
    topic           VARCHAR(255),
    config_override JSONB DEFAULT '{}',
    due_date        TIMESTAMPTZ,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_game_assignments_class ON game_assignments(class_id, is_active);

CREATE TABLE IF NOT EXISTS game_leaderboard (
    id              SERIAL PRIMARY KEY,
    template_id     INTEGER NOT NULL REFERENCES game_templates(id),
    class_id        INTEGER REFERENCES classes(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    week_start      DATE NOT NULL,
    best_score      INTEGER DEFAULT 0,
    games_played    INTEGER DEFAULT 0,
    total_correct   INTEGER DEFAULT 0,
    UNIQUE(template_id, class_id, student_id, week_start)
);
CREATE INDEX idx_game_leaderboard_rank ON game_leaderboard(template_id, class_id, week_start, best_score DESC);

CREATE TABLE IF NOT EXISTS multiplayer_lobbies (
    id              SERIAL PRIMARY KEY,
    template_id     INTEGER NOT NULL REFERENCES game_templates(id),
    host_id         INTEGER NOT NULL REFERENCES tutor_users(id),
    class_id        INTEGER REFERENCES classes(id),
    lobby_code      VARCHAR(10) NOT NULL UNIQUE,
    max_players     INTEGER DEFAULT 2,
    status          VARCHAR(20) DEFAULT 'waiting' CHECK (status IN ('waiting', 'playing', 'completed')),
    config_json     JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS multiplayer_players (
    id              SERIAL PRIMARY KEY,
    lobby_id        INTEGER NOT NULL REFERENCES multiplayer_lobbies(id) ON DELETE CASCADE,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    score           INTEGER DEFAULT 0,
    joined_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(lobby_id, student_id)
);
```

---

## 7. Service Layer Architecture

### New Files:
- `backend/app/services/game_engine.py` — Core game logic: session management, question generation, scoring, adaptive difficulty
- `backend/app/services/game_content.py` — AI content generation for games (questions in game context)
- `backend/app/services/game_recommendations.py` — AI recommendation engine based on mastery gaps
- `backend/app/services/pathway_selector.py` — Learning modality recommendation
- `backend/app/services/multiplayer.py` — WebSocket lobby management, game synchronization

### New Routers:
- `backend/app/routers/games.py` — Game endpoints
- `backend/app/routers/teacher_games.py` — Teacher game management

### Integration:
- `mastery_tracking.py` — Every game answer updates mastery
- `misconception_detection.py` — Wrong answers feed misconception engine
- `gamification.py` — Game completion awards XP
- `adaptive_quiz.py` — Shares ZPD calculation logic

---

## 8. Celery Task Definitions

| Task | Trigger | Description |
|------|---------|-------------|
| `pregenerate_game_content` | Daily 03:00 UTC | Pre-generate questions for popular game/topic combinations |
| `update_game_leaderboards` | Every 30 minutes | Recompute game leaderboard rankings |
| `cleanup_stale_lobbies` | Hourly | Close multiplayer lobbies inactive for >30 min |

---

## 9. State Management (Frontend)

### New Store: `frontend/stores/games-store.ts`

```typescript
interface GamesState {
  templates: GameTemplate[];
  recommendations: GameTemplate[];
  activeSession: GameSession | null;
  gameState: Record<string, any>;
  history: GameSession[];

  // Multiplayer
  lobby: MultiplayerLobby | null;
  opponents: Player[];

  // Actions
  fetchTemplates: (filters: GameFilters) => Promise<void>;
  fetchRecommendations: () => Promise<void>;
  startGame: (templateId: number, subject: string, topic: string) => Promise<void>;
  submitAnswer: (answer: any) => Promise<AnswerResult>;
  completeGame: () => Promise<GameResults>;
  createLobby: (templateId: number) => Promise<string>;
  joinLobby: (code: string) => Promise<void>;
}
```

---

## 10. Real-Time Requirements

| Feature | Mechanism | Details |
|---------|-----------|---------|
| Multiplayer sync | WebSocket | Real-time game state sync between players |
| Class challenge | WebSocket | Live participation view for teacher |
| Game leaderboard | Polling (30s) | Updated during active class games |
| Speed challenge | WebSocket | Real-time score comparison in 1v1 |

---

## 11. Testing Strategy

### Backend Tests
- ZPD engine: verify difficulty adjusts based on performance
- Game session lifecycle: start → answer → complete
- Mastery integration: verify mastery updates after game
- Multiplayer: lobby creation, join, sync, completion

### Frontend E2E
- Browse game hub, filter by age/subject
- Start and complete a game (one per age band)
- View results and mastery impact
- Pathway selector flow

---

## 12. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Game development complexity | Scope creep, delayed delivery | Start with 4 simplest games (1 per band), iterate |
| Game quality vs educational value | Students play but don't learn | Mastery integration ensures every answer counts; analytics track effectiveness |
| Multiplayer latency | Poor real-time experience | WebSocket with local optimistic updates; graceful degradation to turn-based |
| Content generation quality | Age-inappropriate or incorrect content | Age-band specific prompts; content review pipeline; teacher flagging |

---

## 13. Implementation Checklist

- [ ] `3.5.1` Game framework — template registry + session management + adaptive difficulty engine
- [ ] `3.5.1` Game framework — AI content generation service
- [ ] `3.5.2` K-2 games — Story Adventure + Matching Game
- [ ] `3.5.2` K-2 games — Virtual Pet + Treasure Hunt
- [ ] `3.5.3` 3-5 games — RPG Quest + Building Game
- [ ] `3.5.3` 3-5 games — Mystery Detective + Fraction Pizza Shop
- [ ] `3.5.4` 6-8 games — Escape Room + Civilization Builder
- [ ] `3.5.4` 6-8 games — Coding Maze + Speed Challenge
- [ ] `3.5.5` 9-12 games — Business Simulation + Debate Tournament
- [ ] `3.5.5` 9-12 games — Case Study Mystery + Stock Market Sim
- [ ] `3.5.6` Multiplayer — lobby system + WebSocket sync + class/friend challenges
- [ ] `3.5.7` Teacher management — assignment + analytics dashboard
- [ ] `3.5.8` AI recommendations — recommendation engine + pathway selector
- [ ] `3.5.8` Game Hub page + Game Browser + Game Results pages
- [ ] `3.5.INT` Integration — mastery updates, XP awards, misconception logging
- [ ] `3.5.E2E` Playwright E2E tests for game flows
