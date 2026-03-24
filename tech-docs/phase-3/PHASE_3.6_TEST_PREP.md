# Functional Phase 3.6: Test Prep Framework (IELTS/SAT/ACT/AP)

> **Status**: Not Started
> **Estimated Duration**: 3 weeks
> **Dependencies**: Phase 2 (quiz engine, mastery tracker, flashcard engine), FP 3.1 (XP system)
> **Sprint Reference**: Sprint 3.6 in AI_TUTOR_MODULE.md (Section 22.6)
> **Priority**: P1 — Medium (high-value for 9-12 students, revenue driver)

---

## 1. Executive Summary

The Test Prep Framework provides structured, official-format practice for major standardized tests. Unlike generic quiz apps, this system is locked to official scoring descriptors (IELTS band descriptors, SAT scaled scores, AP rubrics), generates full-length timed mock tests, predicts scores, identifies gaps, and creates personalized week-by-week study plans. The IELTS module goes deepest — with AI examiner for speaking, paragraph-level writing feedback, AI-generated listening passages, and accent-varied audio. SAT/ACT/AP modules provide section-aware practice with official score scaling.

---

## 2. Target Users and Personas

| User Type | Goals | How This Phase Serves Them |
|-----------|-------|---------------------------|
| **Student (9-12)** | College prep, test score improvement | Full mock tests, score prediction, study plans |
| **Student (International)** | IELTS for university admission | All 4 IELTS skills with band-locked scoring |
| **Student (AP)** | AP exam scores 4-5 | Subject-specific AP practice with rubric scoring |
| **Teacher** | Track student test readiness | Class test prep analytics, assign practice |
| **Parent** | Monitor college readiness | See test prep progress in parent dashboard |

---

## 3. Features and Sub-Features

### 3.6.1 Test Prep Infrastructure — P0
- **Pluggable Test Profile System**: JSON descriptors for each test type
  ```json
  {
    "id": "ielts_academic",
    "name": "IELTS Academic",
    "sections": ["listening", "reading", "writing", "speaking"],
    "scoringType": "band",
    "scoreRange": { "min": 0, "max": 9, "step": 0.5 },
    "totalDuration": 170,
    "sectionTimers": { "listening": 30, "reading": 60, "writing": 60, "speaking": 15 }
  }
  ```
- **Student Enrollment**: Student selects test → sets target score + target date
- **Scoring Engine**: Locked to official descriptors (not AI opinions)
  - IELTS: Band descriptors 1-9 for each criterion
  - SAT: Scaled score mapping (200-800 per section)
  - ACT: Composite 1-36
  - AP: Rubric-based 1-5
- **Acceptance Criteria**: Test profiles accurately reflect official format; enrollment persists; scoring matches official band/score ranges

### 3.6.2 Mock Test Generator — P0
- Full-length timed practice tests matching official format
- **Question Generation**: AI generates test-format questions with appropriate difficulty
- **Timer System**:
  - Section-level timers with countdown
  - Warning at 5-min and 1-min remaining
  - Auto-submit when time expires
  - Pause allowed (but tracked in analytics)
  - Break timer between sections (IELTS: no breaks; SAT: 10-min break after section 2)
- **Test Conditions Mode**: Strict mode — no pausing, no leaving tab (optional)
- **Acceptance Criteria**: Mock tests match official question count and timing; auto-submit works; strict mode detects tab switch

### 3.6.3 Score Prediction Model — P1
- Running weighted average of mock test scores
- Trend analysis: improving, stable, declining
- Confidence interval: "Your predicted score is 6.5-7.0 (75% confidence)"
- Factors: recent performance, practice volume, time to test date
- College readiness benchmarks (SAT: by school, ACT: by major)
- **Acceptance Criteria**: Prediction updates after each mock; trend direction correct; confidence interval reasonable

### 3.6.4 Gap Analysis — P0
- Per-section weakness identification:
  - Which question types are weakest
  - Which topics need work
  - Comparison: current vs. target score
- Visual: heatmap of strengths/weaknesses by section/topic
- Actionable: "To reach Band 7 in Writing, focus on Task 2 paragraph cohesion"
- **Acceptance Criteria**: Gap analysis accurate to last 5 mock tests; recommendations specific and actionable

### 3.6.5 Personalized Study Plan — P1
- AI generates week-by-week roadmap to target score by target date
- Plan adapts based on mock performance
- Daily recommended activities: "Today: 30 min IELTS Reading practice (True/False/Not Given)"
- Integrates with: flashcards (vocabulary), quiz (question practice), audio (listening), roleplay (speaking)
- Calendar view with study schedule
- **Acceptance Criteria**: Plan adjusts after each mock; daily recommendations relevant to gaps; calendar renders correctly

### 3.6.6 IELTS Speaking Module — P0
- **AI Examiner**: Simulates all 3 parts of IELTS speaking test
  - Part 1: Introduction questions (4-5 min)
  - Part 2: Cue card long turn (2 min + 1 min prep)
  - Part 3: Two-way discussion (4-5 min)
- **Speech-to-Text**: OpenAI Whisper API for student speech recognition
- **Band Scoring Per Criterion**:
  | Criterion | Band Descriptors |
  |-----------|-----------------|
  | Fluency & Coherence (FC) | Speed, hesitation, connectors, topic development |
  | Lexical Resource (LR) | Vocabulary range, collocations, paraphrase |
  | Grammatical Range & Accuracy (GRA) | Structures, error frequency, complex sentences |
  | Pronunciation (P) | Sound features, stress, intonation, intelligibility |
- **Dynamic Follow-ups**: AI generates follow-up questions based on student's responses
- **Pronunciation Feedback**: Word-level pronunciation scoring where possible
- **Session Recording**: Audio saved for student review
- **Acceptance Criteria**: AI examiner follows official IELTS format; band scores use official descriptors; Whisper transcription accurate; follow-ups natural

### 3.6.7 IELTS Writing Module — P0
- **Task Types**:
  - Task 1 Academic: Describe a graph/chart/diagram (150+ words, 20 min)
  - Task 1 General: Write a letter (150+ words, 20 min)
  - Task 2: Essay (250+ words, 40 min)
- **Band-Descriptor Scoring**:
  | Criterion | What It Assesses |
  |-----------|-----------------|
  | Task Achievement/Response | Addressing the prompt, position, main ideas |
  | Coherence & Cohesion | Paragraphing, linking, logical flow |
  | Lexical Resource | Vocabulary range, accuracy, word choice |
  | Grammatical Range & Accuracy | Structures, error frequency |
- **Paragraph-Level Feedback**: Each paragraph gets specific feedback
- **Iterative Improvement**: Student revises → resubmits → AI shows score change
- **Model Answers**: AI generates a Band 8+ model answer for comparison (after student submits)
- **Graph/Chart Generation**: AI generates realistic IELTS-style graphs for Task 1
- **Acceptance Criteria**: Scoring aligns with IELTS band descriptors; feedback paragraph-specific; word count enforced; timer accurate

### 3.6.8 IELTS Reading Module — P1
- **AI-Generated Passages**: IELTS-style academic passages (700-900 words)
- **Question Types**:
  | Type | Description |
  |------|-------------|
  | True/False/Not Given | Statement evaluation against passage |
  | Matching Headings | Match headings to paragraphs |
  | Sentence Completion | Fill gaps with words from passage |
  | Multiple Choice | Standard 4-option MCQ |
  | Summary Completion | Complete a summary with given words |
  | Matching Information | Match statements to paragraphs |
- **Timed Mode**: 20 minutes per passage (3 passages = 60 min)
- **Strategy Coaching**: AI teaches question-type strategies (skim, scan, keyword match)
- **Acceptance Criteria**: Passages at appropriate reading level; all 6 question types working; timer enforced; strategy tips contextual

### 3.6.9 IELTS Listening Module — P1
- **AI-Generated Audio**: TTS with accent variety
  | Section | Format | Accent |
  |---------|--------|--------|
  | 1 | Social conversation | British + Australian |
  | 2 | Social monologue | American |
  | 3 | Academic discussion | British + Indian |
  | 4 | Academic lecture | Canadian |
- **Question Types**: Form completion, MCQ, map labeling, sentence completion, matching
- **Playback Controls**: Play once (authentic) or unlimited (practice mode)
- **Audio Generation**: Celery task generates audio via TTS API
- **Acceptance Criteria**: Audio quality clear; accent variety authentic; questions match section format; play-once mode enforced in mock test

### 3.6.10 SAT Module — P1
- **Sections**:
  | Section | Time | Questions |
  |---------|------|-----------|
  | Reading & Writing (Module 1) | 32 min | 27 questions |
  | Reading & Writing (Module 2) | 32 min | 27 questions (adaptive) |
  | Math (Module 1) | 35 min | 22 questions |
  | Math (Module 2) | 35 min | 22 questions (adaptive) |
- **Adaptive Module**: Module 2 difficulty adjusts based on Module 1 performance (like real digital SAT)
- **Score Scaling**: Raw → scaled score (200-800 per section, 400-1600 total)
- **College Readiness Benchmarks**: Per-college score expectations (curated dataset)
- **Acceptance Criteria**: Adaptive module selection works; score scaling matches College Board; section timing correct

### 3.6.11 ACT Module — P1
- **Sections**: English (75 questions/45 min), Math (60/60 min), Reading (40/35 min), Science (40/35 min), Writing (optional, 1 essay/40 min)
- **Composite Score**: Average of 4 sections, scaled 1-36
- **Acceptance Criteria**: All 4 sections generated correctly; composite calculated; timing enforced

### 3.6.12 AP Module — P2
- **Subject Support** (initial 10 subjects):
  - AP Calculus AB/BC, AP Biology, AP Chemistry, AP Physics 1
  - AP US History, AP World History, AP English Language, AP English Literature
  - AP Computer Science A, AP Statistics
- **Score Calibration**: Questions weighted to produce 1-5 scale
- **Free Response**: AI evaluates written/calculated free responses against rubric
- **Acceptance Criteria**: Questions match AP format per subject; scoring 1-5 consistent; free response evaluation reasonable

---

## 4. Pages, Views, and UI Components

### 4.1 Page Inventory

| Page | Route | Access Role | Description |
|------|-------|-------------|-------------|
| Test Prep Hub | `/test-prep` | student | All enrolled tests + browse |
| Test Profile Detail | `/test-prep/{profile_id}` | student | Test overview + sections |
| Enrollment | `/test-prep/{profile_id}/enroll` | student | Set target + date |
| Study Plan | `/test-prep/study-plan` | student | Week-by-week plan |
| Mock Test Launcher | `/test-prep/mock/start` | student | Configure + start mock |
| Mock Test | `/test-prep/mock/{attempt_id}` | student | Active mock test |
| Mock Test Results | `/test-prep/mock/{attempt_id}/results` | student | Score breakdown |
| Gap Analysis | `/test-prep/gap-analysis` | student | Strengths/weaknesses heatmap |
| Score Tracker | `/test-prep/progress` | student | Score prediction + history |
| IELTS Speaking | `/test-prep/ielts/speaking` | student | AI examiner session |
| IELTS Writing | `/test-prep/ielts/writing` | student | Writing practice |
| IELTS Reading | `/test-prep/ielts/reading` | student | Reading passages + questions |
| IELTS Listening | `/test-prep/ielts/listening` | student | Listening practice |
| Section Practice | `/test-prep/{profile_id}/practice/{section}` | student | Practice specific section |

### 4.2 Layout Mockup Descriptions

#### Test Prep Hub (`/test-prep`)
**Desktop**: Enrolled tests as large cards (score progress ring, target score badge, next study action). Below: browse more tests (grid of test logos). Right sidebar: study plan snapshot (next 3 days), score prediction summary.
**Mobile**: Enrolled tests as full-width cards. Browse as horizontal scroll. Study plan as collapsible section.

#### Mock Test (`/test-prep/mock/{attempt_id}`)
**Desktop**: Mimics real test interface. Top: timer bar (section name, time remaining, question X of Y). Left: question text/passage (60%). Right: answer area (40%). Navigation: "Previous", "Next", "Flag for review", question grid overlay. Clean, distraction-free — no sidebar, no header.
**Mobile**: Full-screen test. Question text above, answer below. Swipe left/right for prev/next. Timer as thin persistent bar at very top.

#### IELTS Speaking (`/test-prep/ielts/speaking`)
**Desktop**: Two-column. Left: AI examiner avatar + current question text + cue card (Part 2). Right: Recording controls (mic button, waveform, timer) + transcript of student's speech. Bottom: Band score breakdown (updated after each part).
**Mobile**: Full-screen. Examiner question at top. Large mic button center. Transcript scrolls below. Band scores as bottom sheet.

#### Gap Analysis (`/test-prep/gap-analysis`)
**Desktop**: Heatmap grid — rows are sections/topics, columns are skills. Color: green (strong), yellow (moderate), red (weak). Click a cell → detailed breakdown + recommended practice. Target score line overlaid.
**Mobile**: Simplified list of weaknesses sorted by impact on score. Each item: section, current score, target, gap, "Practice Now" button.

### 4.3 Component Hierarchy

```
components/test-prep/
├── TestPrepHub.tsx               (main hub page)
├── TestProfileCard.tsx           (enrolled test card)
├── TestBrowseGrid.tsx            (browse available tests)
├── EnrollmentForm.tsx            (target score + date form)
├── StudyPlanCalendar.tsx         (week-by-week study plan)
├── StudyPlanDayCard.tsx          (daily recommendation card)
├── ScoreTracker.tsx              (score prediction + history chart)
├── ScorePrediction.tsx           (confidence interval display)
├── GapAnalysisHeatmap.tsx        (strengths/weaknesses grid)
├── GapDetailPanel.tsx            (click-through gap detail)
│
├── mock/
│   ├── MockTestLauncher.tsx      (configure mock test)
│   ├── MockTestShell.tsx         (test-taking interface)
│   ├── MockTestTimer.tsx         (section timer bar)
│   ├── MockTestQuestion.tsx      (question display)
│   ├── MockTestNavigation.tsx    (prev/next/flag/grid)
│   ├── MockTestResults.tsx       (score breakdown page)
│   └── MockTestReview.tsx        (review answers post-test)
│
├── ielts/
│   ├── IELTSSpeaking.tsx         (AI examiner interface)
│   ├── IELTSSpeakingRecorder.tsx (mic + waveform + timer)
│   ├── IELTSSpeakingTranscript.tsx (real-time transcript)
│   ├── IELTSSpeakingBandScore.tsx (per-criterion scores)
│   ├── IELTSWriting.tsx          (writing practice interface)
│   ├── IELTSWritingEditor.tsx    (rich text editor with word count)
│   ├── IELTSWritingFeedback.tsx  (paragraph-level feedback)
│   ├── IELTSWritingModelAnswer.tsx (band 8+ comparison)
│   ├── IELTSReading.tsx          (passage + questions layout)
│   ├── IELTSReadingPassage.tsx   (scrollable passage display)
│   ├── IELTSListening.tsx        (audio player + questions)
│   └── IELTSListeningPlayer.tsx  (play-once/unlimited toggle)
│
├── sat/
│   ├── SATModule.tsx             (adaptive module interface)
│   └── SATScoreScale.tsx         (scaled score display)
│
├── act/
│   ├── ACTModule.tsx             (section interface)
│   └── ACTCompositeScore.tsx     (composite calculation display)
│
└── ap/
    ├── APSubjectSelector.tsx     (subject picker)
    ├── APFreeResponse.tsx        (free response editor)
    └── APRubricScore.tsx         (1-5 rubric display)
```

---

## 5. Backend API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/api/test-prep/profiles` | List available test profiles | student |
| GET | `/api/test-prep/profiles/{id}` | Get test profile details | student |
| POST | `/api/test-prep/enroll` | Enroll in a test (target + date) | student |
| GET | `/api/test-prep/enrollment` | Get student's enrollments | student |
| PUT | `/api/test-prep/enrollment/{id}` | Update target/date | student |
| GET | `/api/test-prep/study-plan` | Get personalized study plan | student |
| POST | `/api/test-prep/study-plan/regenerate` | Regenerate study plan | student |
| POST | `/api/test-prep/mock/start` | Start a mock test | student |
| GET | `/api/test-prep/mock/{id}` | Get mock test state | student |
| POST | `/api/test-prep/mock/{id}/answer` | Submit answer | student |
| POST | `/api/test-prep/mock/{id}/section/complete` | Complete a section | student |
| POST | `/api/test-prep/mock/{id}/complete` | Complete entire mock | student |
| GET | `/api/test-prep/mock/{id}/results` | Get mock results + score | student |
| GET | `/api/test-prep/score-prediction` | Get score prediction | student |
| GET | `/api/test-prep/gap-analysis` | Get gap analysis | student |
| GET | `/api/test-prep/history` | Mock test history | student |
| POST | `/api/test-prep/ielts/speaking/start` | Start IELTS speaking session | student |
| POST | `/api/test-prep/ielts/speaking/{id}/audio` | Upload speech audio | student |
| GET | `/api/test-prep/ielts/speaking/{id}/score` | Get speaking band scores | student |
| POST | `/api/test-prep/ielts/writing/submit` | Submit writing task | student |
| GET | `/api/test-prep/ielts/writing/{id}/feedback` | Get writing feedback | student |
| POST | `/api/test-prep/ielts/listening/generate` | Generate listening test | student |
| GET | `/api/test-prep/ielts/listening/{id}/audio` | Get listening audio URL | student |
| POST | `/api/test-prep/practice/{section}/start` | Start section practice | student |

---

## 6. Database Schema Additions

```sql
CREATE TABLE IF NOT EXISTS test_profiles (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT,
    scoring_type    VARCHAR(20) NOT NULL,
    score_min       REAL NOT NULL,
    score_max       REAL NOT NULL,
    score_step      REAL DEFAULT 1,
    sections_json   JSONB NOT NULL,
    total_duration_minutes INTEGER,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS student_test_prep (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    profile_id      INTEGER NOT NULL REFERENCES test_profiles(id),
    target_score    REAL NOT NULL,
    target_date     DATE NOT NULL,
    predicted_score REAL,
    prediction_confidence REAL,
    study_plan_json JSONB,
    status          VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused')),
    enrolled_at     TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_id, profile_id)
);
CREATE INDEX idx_student_test_prep_student ON student_test_prep(student_id);

CREATE TABLE IF NOT EXISTS mock_test_attempts (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    profile_id      INTEGER NOT NULL REFERENCES test_profiles(id),
    sections_json   JSONB NOT NULL DEFAULT '[]',
    answers_json    JSONB DEFAULT '[]',
    scores_json     JSONB DEFAULT '{}',
    total_score     REAL,
    section_scores  JSONB DEFAULT '{}',
    gap_analysis_json JSONB,
    time_taken_seconds INTEGER,
    is_practice     BOOLEAN DEFAULT FALSE,
    strict_mode     BOOLEAN DEFAULT FALSE,
    completed       BOOLEAN DEFAULT FALSE,
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);
CREATE INDEX idx_mock_attempts_student ON mock_test_attempts(student_id, profile_id, completed_at DESC);

CREATE TABLE IF NOT EXISTS speaking_attempts (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    profile_id      INTEGER NOT NULL REFERENCES test_profiles(id),
    mock_attempt_id INTEGER REFERENCES mock_test_attempts(id),
    part            SMALLINT NOT NULL CHECK (part BETWEEN 1 AND 3),
    question_text   TEXT NOT NULL,
    audio_url       VARCHAR(1000),
    transcript      TEXT,
    duration_seconds INTEGER,
    scores_json     JSONB DEFAULT '{}',
    band_score      REAL,
    feedback_json   JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS writing_attempts (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    profile_id      INTEGER NOT NULL REFERENCES test_profiles(id),
    mock_attempt_id INTEGER REFERENCES mock_test_attempts(id),
    task_type       VARCHAR(20) NOT NULL,
    prompt_text     TEXT NOT NULL,
    prompt_image_url VARCHAR(1000),
    student_text    TEXT NOT NULL,
    word_count      INTEGER,
    scores_json     JSONB DEFAULT '{}',
    band_score      REAL,
    feedback_json   JSONB DEFAULT '{}',
    model_answer    TEXT,
    revision_of     INTEGER REFERENCES writing_attempts(id),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_writing_attempts_student ON writing_attempts(student_id, created_at DESC);

CREATE TABLE IF NOT EXISTS listening_tests (
    id              SERIAL PRIMARY KEY,
    profile_id      INTEGER NOT NULL REFERENCES test_profiles(id),
    sections_json   JSONB NOT NULL,
    audio_urls_json JSONB DEFAULT '{}',
    status          VARCHAR(20) DEFAULT 'generating',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 7. Service Layer Architecture

### New Files:
- `backend/app/services/test_prep.py` — Enrollment, mock management, scoring engine
- `backend/app/services/test_content.py` — AI question generation per test format
- `backend/app/services/score_prediction.py` — Prediction model, gap analysis, study plan
- `backend/app/services/ielts_speaking.py` — Whisper transcription, band scoring, examiner flow
- `backend/app/services/ielts_writing.py` — Band-locked scoring, paragraph feedback, model answers
- `backend/app/services/ielts_listening.py` — Audio generation, accent management

### New Routers:
- `backend/app/routers/test_prep.py` — All test prep endpoints

### Third-Party APIs:
- **OpenAI Whisper** — Speech-to-text for IELTS speaking ($0.006/min)
- **OpenAI TTS** — Audio generation for listening tests ($15/1M chars)
- **OpenAI GPT-4o** — Question generation, scoring, feedback (existing provider)

---

## 8. Celery Task Definitions

| Task | Trigger | Description |
|------|---------|-------------|
| `generate_listening_audio` | API call | Generate TTS audio for listening test sections |
| `score_speaking_attempt` | After upload | Transcribe audio + generate band scores |
| `score_writing_attempt` | After submit | Generate band scores + paragraph feedback |
| `update_score_prediction` | After mock complete | Recompute score prediction |
| `regenerate_study_plan` | After mock complete | Adjust study plan based on new results |
| `pregenerate_mock_questions` | Daily 04:00 UTC | Pre-generate questions for popular test formats |

---

## 9. State Management (Frontend)

### New Store: `frontend/stores/test-prep-store.ts`

```typescript
interface TestPrepState {
  profiles: TestProfile[];
  enrollments: StudentEnrollment[];
  studyPlan: StudyPlan | null;

  // Mock test
  activeMock: MockTestState | null;
  currentSection: number;
  currentQuestion: number;
  timeRemaining: number;
  flaggedQuestions: Set<number>;

  // IELTS specific
  speakingSession: SpeakingSession | null;
  isRecording: boolean;
  writingDraft: string;

  // Results
  scorePrediction: ScorePrediction | null;
  gapAnalysis: GapAnalysis | null;
  mockHistory: MockAttempt[];

  // Actions
  enroll: (profileId: number, target: number, date: string) => Promise<void>;
  startMock: (profileId: number, config: MockConfig) => Promise<void>;
  submitAnswer: (questionId: number, answer: any) => void;
  completeSection: () => Promise<void>;
  completeMock: () => Promise<MockResults>;
  startSpeaking: (part: number) => Promise<void>;
  uploadSpeechAudio: (audio: Blob) => Promise<void>;
  submitWriting: (text: string) => Promise<void>;
}
```

---

## 10. Testing Strategy

### Backend Tests
- Scoring engine: verify band scores match official descriptors (use known scored samples)
- Mock test lifecycle: start → answer → section → complete → results
- Score prediction: verify trend calculation
- Study plan generation: verify it adapts to gaps

### Frontend E2E
- Enroll in IELTS, set target Band 7
- Start mock test, complete one section
- IELTS writing: submit essay, view feedback
- View gap analysis and study plan
- Score tracker shows prediction

---

## 11. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Scoring accuracy vs official | Students misled about readiness | Use official band descriptors as system prompts; disclaimer: "AI estimate, not official score" |
| Whisper transcription errors | Wrong speaking score | Show transcript for student verification; human review option |
| TTS accent quality | Unrealistic listening practice | Use high-quality voices; disclaimer about real exam accents |
| AP content breadth (38 subjects) | Scope explosion | Start with 10 most popular subjects; expand iteratively |
| Test format changes | Outdated practice | Pluggable test profiles; easy to update JSON descriptors |

---

## 12. Implementation Checklist

- [ ] `3.6.1` Infrastructure — test profile system + enrollment + scoring engine
- [ ] `3.6.2` Mock test generator — question generation + timer + auto-submit
- [ ] `3.6.3` Score prediction — prediction model + confidence interval + trend
- [ ] `3.6.4` Gap analysis — per-section weakness identification + heatmap
- [ ] `3.6.5` Study plan — AI week-by-week roadmap + daily recommendations + calendar
- [ ] `3.6.6` IELTS Speaking — AI examiner (Parts 1-3) + Whisper STT + band scoring
- [ ] `3.6.7` IELTS Writing — Task 1/2 + band scoring + paragraph feedback + model answers
- [ ] `3.6.8` IELTS Reading — passage generation + 6 question types + timed mode
- [ ] `3.6.9` IELTS Listening — TTS audio with accents + question types + play-once mode
- [ ] `3.6.10` SAT Module — adaptive modules + scaled scoring + college benchmarks
- [ ] `3.6.11` ACT Module — 4 sections + composite score + writing optional
- [ ] `3.6.12` AP Module — initial 10 subjects + free response + rubric scoring
- [ ] `3.6.UI` Test Prep Hub + Mock Test Shell + Results + Gap Analysis pages
- [ ] `3.6.UI` IELTS-specific pages (speaking, writing, reading, listening)
- [ ] `3.6.INT` Integration — XP awards, mastery tracking, flashcard vocabulary
- [ ] `3.6.E2E` Playwright E2E tests for test prep flows
