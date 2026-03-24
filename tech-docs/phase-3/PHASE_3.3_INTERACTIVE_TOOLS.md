# Functional Phase 3.3: Whiteboard, Code Sandbox, Math Editor

> **Status**: Not Started
> **Estimated Duration**: 2 weeks
> **Dependencies**: Phase 1.5 (chat UI complete), Docker sandbox service (exists in docker-compose.yml)
> **Sprint Reference**: Sprint 3.3 in AI_TUTOR_MODULE.md (Section 22.3)
> **Priority**: P1 — Medium (high-impact for STEM subjects)

---

## 1. Executive Summary

Interactive tools transform the AI tutor from a text-only chatbot into a multimodal learning environment. Students can draw on a whiteboard and have the AI interpret their work, write and execute code in a sandboxed environment, and input complex math expressions with real-time rendering. These tools are embedded directly in the chat interface as expandable panels, creating a seamless flow between conversation and hands-on work. The AI actively participates — drawing diagrams, reviewing code, and guiding step-by-step math solutions.

---

## 2. Target Users and Personas

| User Type | Goals | How This Phase Serves Them |
|-----------|-------|---------------------------|
| **Student (K-2)** | Draw, visual learning | Whiteboard for drawing shapes, counting, simple diagrams |
| **Student (3-5)** | Visual math, simple code | Whiteboard for geometry, math editor for fractions, Scratch-like code |
| **Student (6-8)** | Code learning, algebra | Code sandbox (Python/JS), math editor for equations, whiteboard for science |
| **Student (9-12)** | Advanced code, calculus | Full code sandbox, advanced math editor, whiteboard for physics diagrams |
| **Teacher** | Create exercises, review work | Code challenges, whiteboard templates, annotated materials |

---

## 3. Features and Sub-Features

### 3.3.1 Digital Whiteboard — tldraw Integration — P0
- **Embedded Panel**: Expandable panel within chat interface (not a separate page)
- **Drawing Tools**: Pen, shapes (rectangle, circle, triangle, arrow, line), text, eraser, undo/redo
- **AI Interpretation (Draw-to-Solve)**:
  - Student draws → AI interprets handwriting/diagrams via vision API
  - Supports: handwritten math, geometric figures, flowcharts, circuit diagrams
  - AI responds in chat with interpretation + solution/feedback
  - Example: Student draws "2x + 3 = 7" → AI: "I see the equation 2x + 3 = 7. Let's solve it step by step..."
- **AI Drawing**:
  - Tutor renders SVG diagrams, graphs, geometric figures onto whiteboard
  - Triggered by chat context (e.g., "Can you draw a right triangle?")
  - AI inserts shapes with labels and annotations
- **Shared State**: Whiteboard state shared between student and AI during session
- **Snapshots**: Save whiteboard state as JSON + PNG thumbnail to session history
- **Templates**: Pre-made whiteboard templates (graph paper, number line, coordinate plane, Venn diagram)
- **Age Adaptations**:
  - K-2: Large brush, bright colors, sticker stamps, simplified toolbar
  - 3-5: Grid background, shape snapping, ruler tool
  - 6-8: Coordinate system, protractor, compass tools
  - 9-12: Full tool suite, layer support
- **Acceptance Criteria**: Whiteboard loads <2s; drawing is responsive at 60fps; AI interpretation returns in <5s; snapshots persist in session; templates load correctly

### 3.3.2 Code Sandbox — Docker-Based Execution — P0
- **Monaco Editor**: Full-featured code editor embedded in chat panel
  - Syntax highlighting for Python, JavaScript, HTML/CSS
  - Auto-indentation, bracket matching, line numbers
  - Configurable font size (age-adaptive: larger for K-5)
  - Theme: matches app light/dark mode
- **Code Execution**:
  - Languages: Python 3.12, JavaScript (Node.js 20)
  - Isolated Docker container per execution (using existing `tutor-sandbox` service)
  - Resource limits: 30s timeout, 128MB memory, 0.5 CPU, network disabled
  - Returns: stdout, stderr, exit code, execution time
  - Max output: 10KB (truncated with warning)
- **AI Code Review**:
  - Student submits code → AI reviews for correctness, style, efficiency
  - Inline suggestions (like a code review)
  - "What does this code do?" → AI explains line by line
  - "Help me debug" → AI identifies issue and guides fix (doesn't give answer directly)
- **Step-by-Step Debugging Guidance**:
  - AI guides student through debugging process
  - "Add a print statement on line 5 to check the value of x"
  - Socratic approach: asks questions before revealing the bug
- **Code Challenges**:
  - AI generates exercises with description + starter code + hidden test cases
  - Auto-grading: run student code against test cases
  - Difficulty levels: Easy (K-5), Medium (6-8), Hard (9-12)
  - Subject integration: math problems via code, science simulations, data analysis
  - Challenge history with pass/fail tracking
- **Acceptance Criteria**: Editor renders with syntax highlighting; code executes in <5s; sandbox isolation verified (no network, no filesystem escape); AI review is contextual; challenges grade correctly

### 3.3.3 Math Editor — MathLive Integration — P0
- **Interactive Math Input**:
  - Replaces plain text input when math context detected
  - Students type naturally (e.g., "2/3" renders as fraction, "sqrt" renders √)
  - Virtual keyboard for math symbols (useful on tablet/mobile)
  - Real-time rendering as student types
- **MathJSON Export**:
  - Internal representation as MathJSON for AI parsing
  - More accurate than text: AI sees structured math, not ambiguous strings
  - Example: `["Divide", 2, 3]` instead of "2/3" which could be "2 divided by 3" or "February 3rd"
- **Step-by-Step Equation Solving**:
  - AI presents equation → student inputs next step → AI validates → continues
  - Visual: each step appears as a new line with the operation labeled
  - Wrong step: AI hints at the error, doesn't give the answer
  - Supports: algebra, calculus derivatives/integrals, trigonometry, linear algebra
- **Graphing**:
  - Student inputs function → renders graph on whiteboard
  - Interactive: zoom, pan, trace points
  - Multiple functions on same graph for comparison
- **Age Adaptations**:
  - K-2: Number pad, basic operations (+, -, ×, ÷), visual fraction bars
  - 3-5: Fractions, decimals, basic exponents, parentheses
  - 6-8: Variables, square roots, basic algebra symbols
  - 9-12: Full math palette (integrals, summations, matrices, Greek letters)
- **Acceptance Criteria**: Math input renders in real-time; MathJSON export is correct; step-by-step validates accurately; graphing renders in <1s; virtual keyboard works on touch

### 3.3.4 Annotation Tools — P2
- Highlight, underline, and add sticky notes to uploaded materials (PDFs, images)
- Annotations persisted per session
- Teacher can pre-annotate materials for student review
- Shared annotations in co-learning mode (Phase 3.2)
- **Acceptance Criteria**: Annotations persist; render on top of materials; teacher annotations visible to students

### 3.3.5 Unified Tool Panel Architecture — P0
- Single expandable panel in chat interface with tab navigation:
  - Whiteboard | Code | Math (tabs at top of panel)
- Panel states: collapsed (icon bar), half-screen, full-screen
- Keyboard shortcut: `Ctrl+Shift+W` (whiteboard), `Ctrl+Shift+C` (code), `Ctrl+Shift+M` (math)
- Tool context persists when switching tabs (whiteboard doesn't reset when you switch to code)
- AI awareness: when tool panel is active, AI adjusts responses to include tool-relevant content
- **Acceptance Criteria**: Tab switching instant; state preserved across tabs; keyboard shortcuts work; panel resizes smoothly

---

## 4. Pages, Views, and UI Components

### 4.1 Page Inventory

| Page | Route | Access Role | Description |
|------|-------|-------------|-------------|
| Chat with Tools | `/chat` (existing, enhanced) | student, teacher | Chat interface with tool panel |
| Code Challenge Hub | `/challenges/code` | student | Browse/attempt code challenges |
| Code Challenge Detail | `/challenges/code/{id}` | student | Specific challenge with editor |
| Teacher Challenge Manager | `/teacher/code-challenges` | teacher | Create/manage code challenges |

### 4.2 Layout Mockup Descriptions

#### Chat with Tool Panel (Desktop >1024px)
- Left (60%): Chat interface (existing) — message list, input bar
- Right (40%): Tool panel with header tabs (Whiteboard | Code | Math)
  - Whiteboard tab: tldraw canvas + toolbar (top: tools, bottom: color/size)
  - Code tab: Monaco editor (top 70%) + output terminal (bottom 30%) + Run/Review buttons
  - Math tab: MathLive input field + step history + graph area
- Divider: draggable to resize split (min 30% chat, min 30% tool)
- Collapse button: hides tool panel, chat goes full width

#### Chat with Tool Panel (Tablet 640-1024px)
- Chat: full width
- Tool panel: slides up from bottom as bottom sheet (70% height)
- Drag handle to resize (50% to 90% height)
- Swipe down to minimize (shows mini toolbar at bottom)

#### Chat with Tool Panel (Mobile <640px)
- Chat: full screen (default)
- Tool panel: full screen overlay (swipe up or tap tool icon)
- Floating chat toggle button (bottom-right) to switch back
- Mini-view: tool collapses to 30% bottom strip showing last output

#### Code Challenge Hub (`/challenges/code`)
- Desktop: Grid of challenge cards (3 columns). Each card: title, difficulty badge, language icon, completion status. Filter bar: language, difficulty, subject, completion status.
- Mobile: Single column list of challenge cards. Sticky filter bar at top.

### 4.3 Component Hierarchy

```
components/tools/
├── ToolPanel.tsx                 (main panel with tab navigation)
├── ToolPanelTabs.tsx             (tab header: Whiteboard | Code | Math)
├── ToolPanelResizer.tsx          (draggable divider)
│
├── whiteboard/
│   ├── WhiteboardCanvas.tsx      (tldraw wrapper)
│   ├── WhiteboardToolbar.tsx     (drawing tools, templates)
│   ├── WhiteboardSnapshot.tsx    (save/load snapshots)
│   ├── WhiteboardAIOverlay.tsx   (AI-drawn SVG shapes)
│   └── DrawToSolveButton.tsx     (trigger AI interpretation)
│
├── code/
│   ├── CodeEditor.tsx            (Monaco editor wrapper)
│   ├── CodeOutput.tsx            (stdout/stderr terminal)
│   ├── CodeToolbar.tsx           (Run, Review, Clear, Language selector)
│   ├── CodeChallenge.tsx         (challenge description + test results)
│   ├── CodeChallengeHub.tsx      (browse challenges page)
│   ├── CodeChallengeCard.tsx     (individual challenge card)
│   └── CodeReviewPanel.tsx       (AI review suggestions)
│
├── math/
│   ├── MathInput.tsx             (MathLive input wrapper)
│   ├── MathVirtualKeyboard.tsx   (on-screen math keyboard)
│   ├── MathStepHistory.tsx       (step-by-step equation display)
│   ├── MathGraph.tsx             (function graphing)
│   └── MathStepValidator.tsx     (validates student's step)
│
└── annotations/
    ├── AnnotationLayer.tsx       (overlay on uploaded materials)
    ├── AnnotationToolbar.tsx     (highlight, underline, note)
    └── AnnotationNote.tsx        (sticky note component)
```

---

## 5. Backend API Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/api/tools/whiteboard/snapshot` | Save whiteboard state (JSON + PNG) | student |
| GET | `/api/tools/whiteboard/{session_id}` | Load whiteboard states for session | student |
| POST | `/api/tools/whiteboard/interpret` | AI interprets drawing (send image) | student |
| POST | `/api/tools/whiteboard/ai-draw` | AI generates SVG for whiteboard | student |
| POST | `/api/tools/code/execute` | Execute code in sandbox | student |
| POST | `/api/tools/code/review` | AI reviews submitted code | student |
| GET | `/api/tools/code/challenges` | List code challenges (filtered) | student |
| GET | `/api/tools/code/challenges/{id}` | Get challenge detail + starter code | student |
| POST | `/api/tools/code/challenges/{id}/submit` | Submit solution + run tests | student |
| GET | `/api/tools/code/challenges/{id}/history` | Student's attempts for challenge | student |
| POST | `/api/tools/math/parse` | Parse MathLive output to MathJSON | student |
| POST | `/api/tools/math/validate-step` | Validate student's equation step | student |
| POST | `/api/tools/math/graph` | Generate graph data from expression | student |
| POST | `/api/tools/math/next-hint` | Get hint for current math problem | student |
| POST | `/api/teacher/code-challenges` | Create a code challenge | teacher |
| PUT | `/api/teacher/code-challenges/{id}` | Update a code challenge | teacher |
| DELETE | `/api/teacher/code-challenges/{id}` | Delete a code challenge | teacher |

---

## 6. Database Schema Additions

```sql
CREATE TABLE IF NOT EXISTS whiteboard_states (
    id              SERIAL PRIMARY KEY,
    session_id      INTEGER NOT NULL REFERENCES tutor_sessions(id) ON DELETE CASCADE,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    state_json      JSONB NOT NULL,
    thumbnail_url   VARCHAR(1000),
    snapshot_index  INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_whiteboard_session ON whiteboard_states(session_id, snapshot_index);

CREATE TABLE IF NOT EXISTS code_executions (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    session_id      INTEGER REFERENCES tutor_sessions(id),
    challenge_id    INTEGER REFERENCES code_challenges(id),
    language        VARCHAR(20) NOT NULL CHECK (language IN ('python', 'javascript', 'html')),
    source_code     TEXT NOT NULL,
    stdout          TEXT,
    stderr          TEXT,
    exit_code       INTEGER,
    duration_ms     INTEGER,
    memory_kb       INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_code_exec_student ON code_executions(student_id, created_at DESC);

CREATE TABLE IF NOT EXISTS code_challenges (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    description     TEXT NOT NULL,
    language        VARCHAR(20) NOT NULL,
    difficulty      SMALLINT NOT NULL CHECK (difficulty BETWEEN 1 AND 5),
    starter_code    TEXT DEFAULT '',
    solution_code   TEXT,
    test_cases_json JSONB NOT NULL DEFAULT '[]',
    hints_json      JSONB DEFAULT '[]',
    subject         VARCHAR(255),
    topic           VARCHAR(255),
    age_band        VARCHAR(10),
    xp_reward       INTEGER DEFAULT 20,
    created_by      INTEGER REFERENCES tutor_users(id),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_code_challenges_filter ON code_challenges(language, difficulty, is_active);

CREATE TABLE IF NOT EXISTS code_challenge_attempts (
    id              SERIAL PRIMARY KEY,
    challenge_id    INTEGER NOT NULL REFERENCES code_challenges(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    source_code     TEXT NOT NULL,
    tests_passed    INTEGER DEFAULT 0,
    tests_total     INTEGER DEFAULT 0,
    passed          BOOLEAN DEFAULT FALSE,
    execution_id    INTEGER REFERENCES code_executions(id),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_challenge_attempts_student ON code_challenge_attempts(student_id, challenge_id);

CREATE TABLE IF NOT EXISTS math_step_sessions (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    session_id      INTEGER REFERENCES tutor_sessions(id),
    original_expression TEXT NOT NULL,
    steps_json      JSONB DEFAULT '[]',
    completed       BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 7. Service Layer Architecture

### New Files:
- `backend/app/services/whiteboard.py` — Snapshot storage, AI interpretation (vision API), AI drawing (SVG generation)
- `backend/app/services/code_sandbox.py` — Docker API communication, execution orchestration, resource limit enforcement
- `backend/app/services/code_challenges.py` — Challenge CRUD, test case execution, auto-grading
- `backend/app/services/math_tools.py` — MathJSON parsing, step validation, graph data generation

### New Routers:
- `backend/app/routers/tools.py` — Tool endpoints (whiteboard, code, math)
- `backend/app/routers/teacher_challenges.py` — Teacher code challenge management

### Docker Sandbox Integration:
The existing `tutor-sandbox` service in `docker-compose.yml` provides Docker-in-Docker. The `code_sandbox.py` service:
1. Creates ephemeral container from language-specific image
2. Mounts student code as read-only volume
3. Runs with resource limits (CPU, memory, network=none)
4. Captures stdout/stderr
5. Destroys container after execution
6. Timeout enforcement: kills container after 30s

---

## 8. Frontend Package Additions

```json
{
  "tldraw": "^4.3.0",
  "@monaco-editor/react": "^4.7.0",
  "mathlive": "^0.108.3"
}
```

**Bundle size considerations**:
- tldraw: ~500KB gzipped — lazy-load on tool panel open
- Monaco: ~2MB gzipped — lazy-load via `next/dynamic` with loading skeleton
- MathLive: ~300KB gzipped — lazy-load on math tab activation

---

## 9. State Management (Frontend)

### New Store: `frontend/stores/tools-store.ts`

```typescript
interface ToolsState {
  // Panel
  activeTab: 'whiteboard' | 'code' | 'math' | null;
  panelSize: 'collapsed' | 'half' | 'full';

  // Whiteboard
  whiteboardStateJSON: object | null;
  snapshots: WhiteboardSnapshot[];

  // Code
  codeLanguage: 'python' | 'javascript';
  sourceCode: string;
  codeOutput: { stdout: string; stderr: string; exitCode: number } | null;
  isExecuting: boolean;

  // Math
  mathExpression: string;
  mathSteps: MathStep[];
  graphData: GraphPoint[] | null;

  // Actions
  setActiveTab: (tab: string | null) => void;
  setPanelSize: (size: string) => void;
  executeCode: () => Promise<void>;
  saveWhiteboardSnapshot: () => Promise<void>;
  validateMathStep: (step: string) => Promise<void>;
}
```

---

## 10. Integration Points

| System | Integration |
|--------|------------|
| Chat Interface | Tool panel embedded in chat layout; AI responses reference tool state |
| Gamification (3.1) | Code challenge completion awards XP; whiteboard interpretation earns XP |
| Session History | Whiteboard snapshots + code executions saved to session |
| Mastery Tracker | Math step completion + code challenge passes feed mastery |
| Age-Adaptive UI | Tool complexity adapts to grade band |
| Parent Dashboard (3.2) | Parent sees code/math activity in activity feed |
| Gaming Engine (3.5) | Code challenges can be presented as games |

---

## 11. Testing Strategy

### Backend Tests
- Code execution: verify sandbox isolation (no network, no filesystem escape, timeout enforcement)
- Code challenge auto-grading: correct code passes, incorrect fails, partial credit
- Whiteboard snapshot CRUD
- Math step validation (correct step, wrong step, edge cases)

### Frontend E2E
- Open tool panel, switch between tabs
- Draw on whiteboard, trigger AI interpretation
- Write code, execute, see output
- Input math expression, step through equation
- Complete a code challenge

---

## 12. Deployment Considerations

- **Docker sandbox**: Already exists in `docker-compose.yml` — ensure Python/JS base images are pre-pulled
- **Vision API**: Whiteboard interpretation requires OpenAI GPT-4V or similar — add `VISION_API_KEY` env var
- **File storage**: Whiteboard PNG thumbnails need S3 or local file storage
- **Security**: Code sandbox is a critical security surface — container escape is the primary threat
  - Network: disabled
  - Filesystem: read-only mounts + tmpfs for /tmp
  - User: non-root inside container
  - Seccomp profile: restrict syscalls
  - No container capabilities

---

## 13. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Container escape | Server compromise | Strict Docker security (no capabilities, seccomp, non-root, network disabled) |
| Resource exhaustion | DoS | Per-user execution rate limit; container resource limits; queue depth limit |
| Large whiteboard state | Slow saves | Compress JSON; limit canvas size; debounce saves |
| MathLive bundle size | Slow page load | Lazy-load on tab activation; loading skeleton |
| Vision API latency | Poor draw-to-solve UX | Show loading state; debounce interpretation requests; cache similar drawings |

---

## 14. Implementation Checklist

- [ ] `3.3.1` Whiteboard — tldraw integration + drawing tools + snapshot save/load
- [ ] `3.3.1` Whiteboard — AI interpretation (draw-to-solve via vision API)
- [ ] `3.3.1` Whiteboard — AI drawing (SVG generation to canvas)
- [ ] `3.3.1` Whiteboard — templates (graph paper, coordinate plane, etc.)
- [ ] `3.3.2` Code sandbox — Monaco editor integration + language selector
- [ ] `3.3.2` Code sandbox — Docker execution service + resource limits
- [ ] `3.3.2` Code sandbox — AI code review integration
- [ ] `3.3.2` Code sandbox — debugging guidance mode
- [ ] `3.3.2` Code challenges — CRUD + auto-grading + test cases
- [ ] `3.3.3` Math editor — MathLive integration + MathJSON export
- [ ] `3.3.3` Math editor — step-by-step equation solving with validation
- [ ] `3.3.3` Math editor — function graphing
- [ ] `3.3.3` Math editor — virtual keyboard (mobile/tablet)
- [ ] `3.3.4` Annotation tools — highlight, underline, sticky notes on materials
- [ ] `3.3.5` Unified tool panel — tab navigation + resize + keyboard shortcuts
- [ ] `3.3.5` Responsive layouts — desktop split, tablet bottom-sheet, mobile overlay
- [ ] `3.3.T` Teacher code challenge management page
- [ ] `3.3.E2E` Playwright E2E tests for all tool interactions
