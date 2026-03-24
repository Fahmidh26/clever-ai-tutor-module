# Functional Phase 3.4: Audio Lessons, Mind Maps, Memory Score

> **Status**: Not Started
> **Estimated Duration**: 2 weeks
> **Dependencies**: Phase 2 (flashcards, mastery tracking, spaced repetition), OpenAI TTS API access
> **Sprint Reference**: Sprint 3.4 in AI_TUTOR_MODULE.md (Section 22.4)
> **Priority**: P1 — Medium (multimodal learning for diverse learning styles)

---

## 1. Executive Summary

This phase introduces multimodal study tools that go beyond text-based tutoring. Audio lessons let students learn through AI-generated conversational podcasts. Mind maps visualize knowledge structures with mastery-colored nodes. Memory score predicts when students will forget material and proactively schedules reviews. Roleplay scenarios bring subjects to life through character-driven interactions. Together, these tools serve visual, auditory, and kinesthetic learners — ensuring no student is left behind by a text-only approach.

---

## 2. Target Users and Personas

| User Type | Goals | How This Phase Serves Them |
|-----------|-------|---------------------------|
| **Student (K-2)** | Listen to stories, visual learning | Story-mode audio lessons, simple visual mind maps |
| **Student (3-5)** | Variety in study methods, exploration | Audio deep dives, mind map exploration, memory reminders |
| **Student (6-8)** | Retention, self-directed study | Memory score for exam prep, roleplay for history/science |
| **Student (9-12)** | Efficient review, advanced topics | Deep dive audio for commute, mind maps for essay planning |
| **Teacher** | Create audio content, track retention | Generate audio from KB, memory analytics, assign roleplays |
| **Parent** | Monitor study patterns | See audio/mindmap activity in parent dashboard |

---

## 3. Features and Sub-Features

### 3.4.1 Audio Lesson Generator ("Deep Dive") — P0
- **AI-Scripted Conversations**: Two AI hosts discuss a topic in conversational dialogue
  - Host A: Enthusiastic explainer
  - Host B: Curious questioner (represents the student's perspective)
  - Natural flow: introduction → key concepts → examples → summary
- **TTS Rendering**: OpenAI TTS API
  - Voice pairs: alloy + echo, nova + fable, shimmer + onyx (configurable)
  - High-quality audio (mp3, 128kbps)
  - Voice speed: normal generation, playback adjustable
- **Lesson Formats**:
  | Format | Duration | Use Case |
  |--------|----------|----------|
  | Brief | 2-3 min | Quick overview of a concept |
  | Deep Dive | 8-12 min | Thorough exploration |
  | Debate | 5-8 min | Two perspectives on a topic |
  | Story Mode | 5-10 min | Narrative format for K-5 |
- **Generation Flow**:
  1. Student/teacher selects topic + format
  2. AI generates script (Celery background task)
  3. TTS renders audio (Celery background task)
  4. Audio stored in S3, served via signed URL
  5. Status polling: generating script → rendering audio → ready
- **Audio Player UI**:
  - Waveform visualizer (optional, decorative)
  - Playback controls: play/pause, skip ±15s, speed (0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x)
  - Progress bar with time stamps
  - Bookmark button: mark moments for later review
  - Transcript panel: synchronized text that highlights as audio plays
  - Sleep timer (for before-bed listening)
- **Teacher Audio Management**:
  - Generate audio from any KB document or topic
  - Assign audio lessons to classes
  - View listen completion rates
- **Acceptance Criteria**: Audio generation completes in <60s (brief) to <180s (deep dive); playback smooth; transcript syncs; bookmarks persist; assigned audio appears in student library

### 3.4.2 Mind Map Generation — P0
- **AI Topic Structure**: AI generates hierarchical concept map as JSON node/edge data
  - Root node: main topic
  - Branch nodes: sub-concepts, key terms, examples
  - Edge labels: relationship types (is-a, has-a, causes, requires)
  - Depth: typically 3-4 levels
- **Interactive Rendering (react-flow)**:
  - Draggable, zoomable canvas
  - Auto-layout: tree, radial, force-directed (student can switch)
  - Color-coded by mastery level:
    - Green (solid): mastered
    - Yellow (dashed): learning
    - Red (dotted): struggling / not started
  - Node click → options: "Start tutoring on this", "Quiz me", "Show flashcards"
- **Knowledge Graph Integration**:
  - Merges with existing `concept_nodes` / `concept_edges` tables
  - Mind map reflects actual learned relationships, not just generated ones
  - Student-specific: shows their mastery colors
- **Export Options**:
  - PNG image (high-res)
  - PDF (with legend)
  - Interactive shareable link (read-only view)
  - JSON data (for reimport)
- **Age Adaptations**:
  - K-2: Simple tree with icons instead of text, large nodes, bright colors
  - 3-5: Standard tree layout, tooltip explanations on hover
  - 6-8: Multiple layout options, edge labels visible
  - 9-12: Full force-directed graph, cross-connections, annotation support
- **Acceptance Criteria**: Mind map generates in <5s; rendering smooth with up to 100 nodes; mastery colors accurate; click-to-learn works; export produces clean output

### 3.4.3 Memory Score — P1
- **Forgetting Curve Model**: Track personal retention per flashcard and topic
  - Based on Ebbinghaus curve with individual calibration
  - Factors: review count, accuracy at review, time since last review, complexity
  - Formula: R(t) = e^(-t / (S × personal_factor)) where S = stability, t = time elapsed
- **Predictions**:
  - Per flashcard: predicted retention % right now
  - Per topic: aggregate retention based on component cards/quizzes
  - "You'll forget 40% of fractions by Thursday — review Wednesday!"
- **Proactive Review Reminders**:
  - Push notification (in-app + optional email) when retention drops below threshold (default: 70%)
  - Suggested review session: "Quick 5-min review: 8 cards about fractions"
  - One-tap to start review
- **Enhanced Spaced Repetition**:
  - Feeds into existing SM-2 algorithm in flashcards service
  - Replaces fixed intervals with personalized intervals based on memory score
  - Accounts for cross-topic interference (similar topics reviewed together for differentiation)
- **Memory Score Dashboard Widget**:
  - Color-coded topic cards: green (>80% retention), yellow (50-80%), red (<50%)
  - "Forgetting forecast": graph showing predicted retention over next 7 days
  - "Review now" buttons for at-risk topics
- **Acceptance Criteria**: Retention predictions within 15% of actual (validated by quiz performance); reminders trigger at threshold; personalized intervals improve recall vs fixed SM-2

### 3.4.4 Roleplay Scenarios — P1
- **Subject-Appropriate Roleplays**:
  | Subject | Scenario Types |
  |---------|---------------|
  | History | Debate historical figures, interview a president, experience an era |
  | Science | Conduct a virtual experiment, defend a hypothesis, interview a scientist |
  | Literature | Character dialogue, author interview, reimagine an ending |
  | Languages | Restaurant ordering, travel conversation, job interview |
  | Math | "Math Court" — defend your solution, teach a concept |
- **Character Personas**:
  - AI assumes character: Albert Einstein, Marie Curie, Shakespeare, Abraham Lincoln
  - Character-appropriate language, knowledge, and personality
  - Historical accuracy (AI stays in character's era/knowledge)
- **Roleplay Flow**:
  1. Student picks scenario type + character
  2. AI introduces the scenario and sets the scene
  3. Student responds in character or as interviewer
  4. Multi-turn conversation (5-15 exchanges)
  5. AI evaluates performance at the end
- **Rubric-Based Evaluation**:
  - Criteria: content accuracy, critical thinking, creativity, communication
  - Score: 1-5 per criterion
  - Personalized feedback: "You showed great understanding of Newton's laws, but could have explored the implications for space travel"
- **Integration with Existing Modes**:
  - Extends the existing "Debate/Roleplay" interaction mode
  - Can be triggered from chat: "Let's do a roleplay about the American Revolution"
- **Acceptance Criteria**: AI maintains character; evaluation rubric consistent; roleplay saves to session; XP awarded for completion

---

## 4. Pages, Views, and UI Components

### 4.1 Page Inventory

| Page | Route | Access Role | Description |
|------|-------|-------------|-------------|
| Audio Lesson Library | `/study-tools/audio` | student | Browse/listen to audio lessons |
| Audio Player | `/study-tools/audio/{id}` | student | Full audio player with transcript |
| Mind Map Viewer | `/study-tools/mind-map` | student | Generate/view mind maps |
| Memory Score Dashboard | `/study-tools/memory` | student | Retention overview + review actions |
| Roleplay Hub | `/study-tools/roleplay` | student | Browse/start roleplay scenarios |
| Roleplay Session | `/study-tools/roleplay/{id}` | student | Active roleplay conversation |
| Teacher Audio Management | `/teacher/audio-lessons` | teacher | Create/assign audio lessons |
| Teacher Roleplay Management | `/teacher/roleplays` | teacher | Create custom scenarios |
| Study Tools Hub | `/study-tools` | student | Central hub for all study tools |

### 4.2 Layout Mockup Descriptions

#### Study Tools Hub (`/study-tools`)
**Desktop**: Grid of 4 large tool cards: Audio Lessons (headphone icon), Mind Maps (network icon), Memory Score (brain icon), Roleplay (theater icon). Each card shows: description, recent activity, "Start" button. Sidebar: subject/topic quick-filter.
**Mobile**: Vertical list of tool cards. Subject filter as horizontal pill scroll at top.

#### Audio Player (`/study-tools/audio/{id}`)
**Desktop**: Two-column. Left (60%): Waveform visualizer + controls (play/pause/speed/skip) + progress bar + bookmark button. Right (40%): Synchronized transcript with highlighted current sentence, bookmark markers.
**Tablet**: Same layout, slightly compressed.
**Mobile**: Full-width player controls at bottom (sticky). Transcript above (scrollable). Speed/bookmark in expandable drawer.

#### Mind Map Viewer (`/study-tools/mind-map`)
**Desktop**: Full-width canvas with react-flow. Toolbar at top: layout switcher (tree/radial/force), zoom controls, export button, regenerate button. Legend at bottom-right: mastery colors. Side panel (collapsible): node details when clicked.
**Mobile**: Full-screen canvas with pinch-zoom. Floating toolbar (minimized, expand on tap). Node details as bottom sheet.

#### Memory Score Dashboard (`/study-tools/memory`)
**Desktop**: Top: summary stats (total topics tracked, average retention, at-risk count). Grid of topic cards (3 columns) color-coded by retention. Each card: topic name, retention %, predicted forget date, "Review Now" button. Right panel: 7-day forgetting forecast line chart.
**Mobile**: Stats row at top. Single column topic cards. Forecast chart full-width below stats.

### 4.3 Component Hierarchy

```
components/study-tools/
├── StudyToolsHub.tsx             (central hub page)
│
├── audio/
│   ├── AudioLibrary.tsx          (browse lessons)
│   ├── AudioLessonCard.tsx       (lesson card in library)
│   ├── AudioPlayer.tsx           (full player component)
│   ├── AudioControls.tsx         (play/pause/speed/skip)
│   ├── AudioWaveform.tsx         (visual waveform)
│   ├── AudioTranscript.tsx       (synced transcript)
│   ├── AudioBookmark.tsx         (bookmark control)
│   ├── AudioGenerator.tsx        (generate new lesson form)
│   └── AudioAssignment.tsx       (teacher: assign to class)
│
├── mindmap/
│   ├── MindMapViewer.tsx         (react-flow canvas)
│   ├── MindMapNode.tsx           (custom node component)
│   ├── MindMapToolbar.tsx        (layout/zoom/export controls)
│   ├── MindMapLegend.tsx         (mastery color legend)
│   ├── MindMapNodeDetail.tsx     (side panel on node click)
│   └── MindMapGenerator.tsx      (topic input + generate)
│
├── memory/
│   ├── MemoryDashboard.tsx       (full memory score page)
│   ├── MemoryTopicCard.tsx       (topic retention card)
│   ├── MemoryForecastChart.tsx   (7-day prediction chart)
│   ├── MemoryWidget.tsx          (compact widget for home)
│   └── ReviewPrompt.tsx          (notification to review)
│
└── roleplay/
    ├── RoleplayHub.tsx           (browse scenarios)
    ├── RoleplayScenarioCard.tsx  (scenario selection card)
    ├── RoleplaySession.tsx       (active roleplay chat)
    ├── RoleplayCharacterCard.tsx (character selection)
    ├── RoleplayEvaluation.tsx    (rubric-based results)
    └── RoleplayGenerator.tsx     (teacher: create custom)
```

---

## 5. Backend API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/study-tools/audio/generate` | Generate audio lesson (async) | student, teacher |
| GET | `/api/study-tools/audio/library` | List audio lessons (filtered) | student |
| GET | `/api/study-tools/audio/{id}` | Get lesson details + audio URL + transcript | student |
| GET | `/api/study-tools/audio/{id}/status` | Check generation status | student |
| POST | `/api/study-tools/audio/{id}/bookmark` | Add/remove bookmark at timestamp | student |
| POST | `/api/study-tools/audio/{id}/complete` | Mark as listened | student |
| POST | `/api/study-tools/mind-map/generate` | Generate mind map for topic | student |
| GET | `/api/study-tools/mind-map/{id}` | Get mind map data (nodes + edges) | student |
| PUT | `/api/study-tools/mind-map/{id}` | Save edited mind map layout | student |
| GET | `/api/study-tools/mind-map/export/{id}` | Export as PNG/PDF/JSON | student |
| GET | `/api/study-tools/memory/scores` | Memory scores for all topics | student |
| GET | `/api/study-tools/memory/forecast` | 7-day retention forecast | student |
| POST | `/api/study-tools/memory/recompute` | Force recomputation | student |
| GET | `/api/study-tools/memory/review-queue` | Cards needing review now | student |
| POST | `/api/study-tools/roleplay/start` | Start roleplay scenario | student |
| POST | `/api/study-tools/roleplay/{id}/respond` | Send student's response | student |
| GET | `/api/study-tools/roleplay/{id}` | Get roleplay state | student |
| POST | `/api/study-tools/roleplay/{id}/evaluate` | Trigger evaluation | student |
| GET | `/api/study-tools/roleplay/scenarios` | List available scenarios | student |
| POST | `/api/teacher/audio-lessons` | Create audio lesson for class | teacher |
| POST | `/api/teacher/audio-lessons/{id}/assign` | Assign to class | teacher |
| GET | `/api/teacher/audio-lessons/analytics` | Listen completion rates | teacher |
| POST | `/api/teacher/roleplays` | Create custom roleplay scenario | teacher |

---

## 6. Database Schema Additions

```sql
CREATE TABLE IF NOT EXISTS audio_lessons (
    id              SERIAL PRIMARY KEY,
    creator_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    title           VARCHAR(255) NOT NULL,
    subject         VARCHAR(255),
    topic           VARCHAR(255),
    format          VARCHAR(20) NOT NULL CHECK (format IN ('brief', 'deep_dive', 'debate', 'story')),
    script_text     TEXT,
    audio_url       VARCHAR(1000),
    transcript_json JSONB,
    duration_seconds INTEGER,
    voice_pair      VARCHAR(50) DEFAULT 'alloy_echo',
    status          VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'scripting', 'rendering', 'ready', 'failed')),
    kb_id           INTEGER REFERENCES knowledge_bases(id),
    class_id        INTEGER REFERENCES classes(id),
    error_message   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_audio_lessons_creator ON audio_lessons(creator_id);
CREATE INDEX idx_audio_lessons_class ON audio_lessons(class_id);

CREATE TABLE IF NOT EXISTS audio_lesson_progress (
    id              SERIAL PRIMARY KEY,
    lesson_id       INTEGER NOT NULL REFERENCES audio_lessons(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    progress_seconds INTEGER DEFAULT 0,
    completed       BOOLEAN DEFAULT FALSE,
    bookmarks_json  JSONB DEFAULT '[]',
    last_played_at  TIMESTAMPTZ,
    UNIQUE(lesson_id, student_id)
);

CREATE TABLE IF NOT EXISTS mind_maps (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    subject         VARCHAR(255),
    topic           VARCHAR(255) NOT NULL,
    layout_type     VARCHAR(20) DEFAULT 'tree',
    nodes_json      JSONB NOT NULL DEFAULT '[]',
    edges_json      JSONB NOT NULL DEFAULT '[]',
    metadata_json   JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_mind_maps_student ON mind_maps(student_id, subject);

CREATE TABLE IF NOT EXISTS memory_scores (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    content_type    VARCHAR(30) NOT NULL CHECK (content_type IN ('flashcard', 'topic', 'quiz_concept')),
    content_id      INTEGER NOT NULL,
    stability       REAL DEFAULT 1.0,
    retention_rate  REAL DEFAULT 1.0,
    predicted_forget_at TIMESTAMPTZ,
    last_reviewed_at TIMESTAMPTZ,
    review_count    INTEGER DEFAULT 0,
    personal_decay_rate REAL DEFAULT 0.5,
    difficulty_factor REAL DEFAULT 1.0,
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_id, content_type, content_id)
);
CREATE INDEX idx_memory_scores_student ON memory_scores(student_id, retention_rate);
CREATE INDEX idx_memory_scores_forget ON memory_scores(predicted_forget_at) WHERE retention_rate < 0.7;

CREATE TABLE IF NOT EXISTS roleplay_sessions (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    scenario_type   VARCHAR(50) NOT NULL,
    character_name  VARCHAR(255),
    subject         VARCHAR(255),
    topic           VARCHAR(255),
    messages_json   JSONB DEFAULT '[]',
    evaluation_json JSONB,
    score           REAL,
    completed       BOOLEAN DEFAULT FALSE,
    xp_awarded      INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_roleplay_student ON roleplay_sessions(student_id, created_at DESC);

CREATE TABLE IF NOT EXISTS roleplay_scenarios (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    scenario_type   VARCHAR(50) NOT NULL,
    character_name  VARCHAR(255),
    subject         VARCHAR(255),
    topic           VARCHAR(255),
    system_prompt   TEXT NOT NULL,
    rubric_json     JSONB NOT NULL DEFAULT '[]',
    age_band        VARCHAR(10),
    difficulty      SMALLINT DEFAULT 3,
    created_by      INTEGER REFERENCES tutor_users(id),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 7. Service Layer Architecture

### New Files:
- `backend/app/services/audio_lessons.py` — Script generation, TTS orchestration, S3 upload
- `backend/app/services/mind_map.py` — AI topic structure generation, concept graph integration
- `backend/app/services/memory_score.py` — Forgetting curve computation, review scheduling, predictions
- `backend/app/services/roleplay.py` — Character persona management, evaluation rubric engine

### New Routers:
- `backend/app/routers/study_tools.py` — All study tool endpoints
- `backend/app/routers/teacher_study_tools.py` — Teacher audio/roleplay management

### Integration with Existing Services:
- `flashcards.py` — Memory score enhances SM-2 scheduling
- `mastery_tracking.py` — Mind map mastery colors sourced from mastery data
- `chat_execution.py` — Roleplay uses chat execution for AI responses
- `gamification.py` — Audio completion, mind map creation, roleplay completion award XP

---

## 8. Celery Task Definitions

| Task | Trigger | Description |
|------|---------|-------------|
| `generate_audio_script` | API call | AI generates 2-host conversational script |
| `render_audio_tts` | After script | TTS API call, upload to S3 |
| `compute_memory_scores` | Daily 02:00 UTC | Batch recompute all active students' scores |
| `send_review_reminders` | Every 4 hours | Check memory scores, send notifications for <70% retention |
| `cleanup_expired_audio` | Weekly | Remove old unassigned audio files from S3 |

---

## 9. State Management (Frontend)

### New Store: `frontend/stores/study-tools-store.ts`

```typescript
interface StudyToolsState {
  // Audio
  audioLibrary: AudioLesson[];
  currentAudio: AudioLesson | null;
  audioPlaying: boolean;
  audioProgress: number;
  audioSpeed: number;

  // Mind Map
  currentMindMap: MindMap | null;
  mindMapLayout: 'tree' | 'radial' | 'force';

  // Memory
  memoryScores: MemoryScore[];
  reviewQueue: FlashcardCard[];
  forecast: ForecastPoint[];

  // Roleplay
  activeRoleplay: RoleplaySession | null;
  scenarios: RoleplayScenario[];

  // Actions
  fetchAudioLibrary: (filters: AudioFilters) => Promise<void>;
  generateAudioLesson: (topic: string, format: string) => Promise<void>;
  generateMindMap: (topic: string) => Promise<void>;
  fetchMemoryScores: () => Promise<void>;
  startRoleplay: (scenarioId: number) => Promise<void>;
  respondInRoleplay: (message: string) => Promise<void>;
}
```

---

## 10. Third-Party API Dependencies

| API | Purpose | Cost Consideration |
|-----|---------|-------------------|
| OpenAI TTS (`tts-1`, `tts-1-hd`) | Audio lesson rendering | ~$15/1M characters; Deep Dive ~8K chars = $0.12/lesson |
| OpenAI GPT-4o | Script generation, roleplay, evaluation | Existing provider; reuse chat execution service |
| S3-compatible storage | Audio file hosting | Storage + bandwidth; consider CDN for playback |

---

## 11. Testing Strategy

### Backend Tests
- Audio generation pipeline: script → TTS → S3 → status tracking
- Mind map generation: verify node/edge structure, mastery color mapping
- Memory score computation: verify forgetting curve math, threshold alerts
- Roleplay: character consistency, evaluation rubric scoring

### Frontend E2E
- Generate and play audio lesson
- Generate mind map, switch layouts, click node to learn
- View memory dashboard, start review from at-risk card
- Complete a roleplay scenario, view evaluation

---

## 12. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| TTS API cost at scale | High operational cost | Cache generated audio; limit free tier; batch off-peak |
| Audio generation latency | Poor UX | Async generation with status polling; show estimated time |
| Memory score accuracy | Wrong predictions frustrate students | Calibrate with quiz results; A/B test against fixed SM-2 |
| Roleplay hallucination | Historically inaccurate content | Character-specific system prompts with fact constraints; disclaimer |

---

## 13. Implementation Checklist

- [ ] `3.4.1` Audio — backend script generation service + Celery task
- [ ] `3.4.1` Audio — TTS rendering service + S3 upload
- [ ] `3.4.1` Audio — frontend AudioPlayer + AudioLibrary + AudioControls
- [ ] `3.4.1` Audio — transcript sync + bookmarks + speed control
- [ ] `3.4.1` Audio — teacher generation from KB + class assignment
- [ ] `3.4.2` Mind map — backend AI generation + concept graph integration
- [ ] `3.4.2` Mind map — frontend react-flow canvas + mastery colors
- [ ] `3.4.2` Mind map — layout switcher + export (PNG/PDF/JSON)
- [ ] `3.4.2` Mind map — click-to-learn integration (start session from node)
- [ ] `3.4.3` Memory score — backend forgetting curve model + computation
- [ ] `3.4.3` Memory score — review reminders (Celery + notifications)
- [ ] `3.4.3` Memory score — frontend dashboard + forecast chart + review actions
- [ ] `3.4.3` Memory score — integration with flashcard SM-2 scheduler
- [ ] `3.4.4` Roleplay — backend scenario engine + character personas
- [ ] `3.4.4` Roleplay — frontend session UI + character selection
- [ ] `3.4.4` Roleplay — evaluation rubric + scoring + feedback
- [ ] `3.4.T` Study Tools Hub page
- [ ] `3.4.E2E` Playwright E2E tests for all study tools
