# AI Tutor Module — Complete Design Specification v3.1

> **Stack**: Python FastAPI · Next.js / React / TypeScript · PostgreSQL + pgvector · Redis · Celery  
> **Architecture**: Fully independent application · Docker containerized · Root site API integration  
> **Status**: Design / Pre-Implementation  
> **Document version**: 2.0 | Last updated: March 2026

---

## Table of Contents

1. [Vision & Philosophy](#1-vision--philosophy)
2. [Ecosystem Architecture](#2-ecosystem-architecture)
3. [Technology Stack](#3-technology-stack)
4. [System Architecture](#4-system-architecture)
5. [Authentication & Root Site Integration](#5-authentication--root-site-integration)
6. [Feature Overview](#6-feature-overview)
7. [User Roles & Access Control](#7-user-roles--access-control)
8. [User Journey](#8-user-journey)
9. [Tutor Roster & Personas](#9-tutor-roster--personas)
10. [Interaction Modes (6 Modes)](#10-interaction-modes-6-modes)
11. [Chat Interface Design](#11-chat-interface-design)
12. [Age-Adaptive UI](#12-age-adaptive-ui)
13. [Adaptive Learning Engine](#13-adaptive-learning-engine)
14. [RAG Pipeline — Custom Training](#14-rag-pipeline--custom-training)
15. [AI Engine Architecture](#15-ai-engine-architecture)
16. [Tutoring Session Workflow](#16-tutoring-session-workflow)
17. [Standards Alignment Engine](#17-standards-alignment-engine)
18. [Teacher Portal](#18-teacher-portal)
19. [Parent Dashboard](#19-parent-dashboard)
20. [Innovations — Outside the Box](#20-innovations--outside-the-box)
21. [Interactive Learning Tools](#21-interactive-learning-tools)
22. [Gamification & Motivation](#22-gamification--motivation)
23. [Safety, Compliance & Privacy](#23-safety-compliance--privacy)
24. [Database Schema](#24-database-schema)
25. [API Endpoints](#25-api-endpoints)
26. [Backend Architecture](#26-backend-architecture)
27. [Frontend Architecture](#27-frontend-architecture)
28. [AI Prompt Engineering](#28-ai-prompt-engineering)
29. [Deployment Architecture](#29-deployment-architecture)
30. [Multi-Language & Localization](#30-multi-language--localization)
31. [Implementation Roadmap](#31-implementation-roadmap)
32. [Key Design Decisions](#32-key-design-decisions)

---

## 1. Vision & Philosophy

### Core Principle
> "A great tutor doesn't give you the answer — they make you capable of finding it yourself."

The AI Tutor blends five teaching philosophies proven to maximize learning outcomes:

| Philosophy | Source Inspiration | Implementation |
|---|---|---|
| **Socratic Coaching** | Khanmigo (Khan Academy) | Hint progression; guiding questions before answers |
| **Mastery Learning** | Coursera Coach | Advance only after demonstrated understanding |
| **Contextual Roleplay** | Duolingo Max | Scenario simulations for language & soft skills |
| **Metacognitive Training** | Educational research | "Show Your Thinking" mode — students explain reasoning |
| **Differentiated Instruction** | Universal Design for Learning | Visual, auditory, kinesthetic, reading/writing approaches |

### What Makes This Different
- **7 interaction modes** the user explicitly chooses (not a blank chat box)
- **Tutor selection with distinct personalities** — not one generic chatbot
- **Layered hint system** — 3 levels before full explanation (server-enforced)
- **Session memory** — tutor remembers past struggles and celebrates growth
- **Teacher-trainable** — teachers upload materials to customize their tutor via RAG
- **Age-adaptive UI** — K-2 gets a completely different experience than Grade 11
- **Misconception detection** — diagnoses WHY students are wrong, not just THAT they're wrong
- **Emotional intelligence** — detects frustration and adapts approach without cameras/mics
- **Standards-aligned** — every topic mapped to Common Core, NGSS, state standards
- **Parent co-learning** — parents and children learn together
- **AI Study Tools** — auto-generated study guides, flashcards, audio lessons, mind maps from any source
- **Test prep framework** — IELTS, SAT, ACT, AP with band/score prediction and descriptor-locked evaluation
- **URL + multimedia ingestion** — paste a URL, YouTube video, or upload audio lecture and learn from it

---

## 2. Ecosystem Architecture

The AI Tutor is a **fully independent application** with its own Docker containers, codebase, and database. It connects to the Clever Creator root site via API for shared services (auth, billing, credits). ChatterMate/Forge serve as architectural reference and optional integrations, not runtime dependencies.

```mermaid
graph TB
    subgraph rootSite [Root Site - clevercreator.ai]
        Auth[OAuth2 + JWT Auth]
        Billing[Subscriptions + Stripe]
        Credits[Token + Credit Management]
        Catalog[Model Catalog + Plan Access]
        UserData[User Profiles]
    end

    subgraph tutorApp [AI Tutor - tutor.clevercreator.ai - INDEPENDENT APP]
        TutorFE[Next.js Frontend]
        TutorBE[FastAPI Backend]
        TutorDB[(PostgreSQL + pgvector)]
        TutorRedis[(Redis)]
        TutorCelery[Celery Workers]
        TutorStorage[(S3/Azure Blob)]
    end

    subgraph chattermate [ChatterMate - OPTIONAL INTEGRATION]
        ForgeAPI[Forge IDE API]
        CMCodeExec[Code Execution Sandbox]
    end

    subgraph llmProviders [LLM Providers]
        OpenAI[OpenAI]
        Anthropic[Anthropic]
        Gemini[Google Gemini]
        Grok[xAI Grok]
    end

    tutorApp -->|"OAuth + JWT + Credits API"| rootSite
    tutorApp -->|"Direct API calls"| llmProviders
    tutorApp -.->|"Optional: CS education"| chattermate
```

### What the Root Site Provides (via API, NOT duplicated):
- User authentication (OAuth 2.0 flow, JWT tokens)
- Subscription/plan management and billing (Stripe)
- Token/credit balance and deduction (`POST /api/user/credits/deduct`)
- Model catalog with plan-based access (`GET /api/catalog`)
- User profile data (`GET /api/user/details`)

### What the AI Tutor Builds Independently:
- Its own AI provider layer (OpenAI, Anthropic, Gemini, Grok — direct API calls via httpx)
- Its own RAG pipeline (document ingestion, chunking, embedding, retrieval)
- Its own streaming infrastructure (SSE for AI, WebSocket for collaborative features)
- Its own token management (estimate, reserve, reconcile with root site)
- Its own code execution sandbox (Docker-based, for CS education)
- All education-specific logic (personas, modes, mastery, standards, gamification)

### Optional ChatterMate/Forge Integration:
- For advanced CS education, can redirect students to Forge IDE via deep link
- Not a runtime dependency — tutor works 100% without ChatterMate

---

## 3. Technology Stack (Pinned Versions — March 2026)

| Layer | Technology | Version | Why |
|---|---|---|---|
| **Frontend** | Next.js (App Router) | **16.1.6** | Turbopack default, React Compiler stable, Cache Components |
| **React** | React + React DOM | **19.2.4** | Server Components stable, `use()` hook, View Transitions |
| **TypeScript** | TypeScript | **5.7.x** (upgrade to 6.0 when GA) | Strict mode, ES2025 target; TS 7 will be Go rewrite |
| **UI Framework** | Tailwind CSS + shadcn/ui | **Tailwind 4.x** + **shadcn 4.0.2** | 3.5x faster builds, OKLCH colors, WCAG, `data-slot` attrs |
| **State Management** | Zustand | **5.0.11** | SSR-safe middleware, persist fixes, 24M+ weekly downloads |
| **Backend API** | Python FastAPI + uvicorn | **FastAPI 0.135.1** | **Native SSE support** (0.135.0), 2x JSON perf via Pydantic Rust |
| **Python** | Python runtime | **3.13.x** | Stable; Celery 5.6 supports up to 3.13; 3.14 available but newer |
| **Validation** | Pydantic | **2.12.5** | Rust-core serialization, TypedDict support |
| **Database** | PostgreSQL + pgvector | **PG 17.9** + **pgvector 0.8.2** | HNSW filtered queries, critical CVE-2026-3172 fix in 0.8.2 |
| **DB Driver** | asyncpg | **0.31.0** | PG 9.5-18 support, Python 3.9+ |
| **Cache / Queue** | Redis + Celery | **Redis 8.6.0** + **Celery 5.6** | Hot keys detection, memory leak fixes for Python 3.11+ |
| **HTTP Client** | httpx | **0.28.1** | Stable; monitor for aiohttp fallback if maintenance stalls |
| **AI Providers** | Direct httpx calls (OpenAI, Anthropic, Gemini, Grok) | latest API versions | No abstraction layer lock-in, full control |
| **Embeddings** | OpenAI text-embedding-3-small | 1536 dims | Best price/performance, swappable |
| **RAG** | Custom pipeline (pypdf, python-docx, python-pptx, pgvector) | latest | Semantic chunking + cosine similarity |
| **Real-time** | SSE (AI streaming), WebSocket (collaborative) | FastAPI native SSE | SSE for AI streaming, WS for collaborative features |
| **File Storage** | S3-compatible (AWS S3 / Azure Blob / MinIO) | latest | Documents, media, audio, exports |
| **Math** | KaTeX + MathLive | **KaTeX 0.16.x** + **MathLive 0.108.3** | 800+ LaTeX commands, MathJSON export |
| **Whiteboard** | tldraw | **4.3.0** | SQLite sync, WCAG 2.2 AA, TipTap v3 integration |
| **Code Editor** | Monaco Editor | **0.55.1** | VS Code engine, IntelliSense, syntax highlighting |
| **Code Execution** | Built-in Docker sandbox | Docker 27.x | Isolated, resource-limited, network disabled |
| **Knowledge Graph** | react-flow | latest | Interactive concept visualization |
| **OCR** | Tesseract.js (client) or cloud OCR | latest | Homework scanning |
| **TTS/STT** | OpenAI Whisper API + TTS API | latest | Audio lessons, voice input, pronunciation |
| **Auth** | OAuth 2.0 via root site, JWT verification | — | Delegated auth, no duplication |
| **Containerization** | Docker + Docker Compose | **Docker 27.x** | Consistent dev/prod environments |
| **Monitoring** | OpenTelemetry, structured logging | latest | Distributed tracing, metrics |

---

## 4. System Architecture

```mermaid
graph TB
    subgraph clients [Client Applications]
        StudentUI[Student Interface - age-adaptive]
        TeacherUI[Teacher Dashboard + AI Co-Pilot]
        ParentUI[Parent Dashboard + Co-Learning]
        MobileUI[Mobile PWA]
    end

    subgraph apiGateway [API Gateway - FastAPI]
        JWTVerify[JWT Verification - root site]
        RateLimiter[Rate Limiter]
        CreditGate[Credit Gate - balance check]
        AgeRouter[Age-Appropriate Router]
    end

    subgraph tutorEngine [Tutor Engine]
        PersonaEngine[Persona Engine - base + custom]
        ModeEngine["Mode Engine (6 modes)"]
        HintEngine[3-Level Hint Progression]
        SessionManager[Session Manager + Memory]
        InterleaveEngine[Interleaving Engine]
    end

    subgraph aiEngine [AI Engine - Independent]
        PromptBuilder[Prompt Builder - 8 layers]
        ProviderLayer[Provider Layer - OpenAI/Claude/Gemini/Grok]
        ModelRouter[Intelligent Model Router]
        SafetyLayer[Safety + Age Filter + Anti-Cheat]
        StreamManager[SSE Stream Manager]
        EmotionDetector[Emotional Intelligence Detector]
    end

    subgraph ragEngine [RAG Engine - Independent]
        DocIngestion[Document Ingestion Pipeline]
        ChunkEngine[Semantic Chunker]
        EmbeddingEngine[Embedding Generator]
        VectorSearch[Vector Similarity Search]
        ScopeFilter[KB Scope Filter - teacher/class/grade]
        RerankerEngine[Cross-Encoder Reranker]
    end

    subgraph learningEngine [Learning Intelligence]
        MasteryTracker[Mastery Tracker - 5 levels]
        MisconceptionEngine[Misconception Detection Engine]
        StandardsEngine[Standards Alignment Engine]
        DiagnosticEngine[Diagnostic Assessment Engine]
        PathGenerator[Learning Path Generator]
        KnowledgeGraphEngine[Knowledge Graph Engine]
        MistakeJournal[Mistake Journal + Pattern Analysis]
    end

    subgraph engagementEngine [Engagement Engine]
        GamificationEngine[XP + Streaks + Badges + Levels]
        PortfolioEngine[Digital Portfolio Builder]
        WellnessGuard[Wellness Guardian]
        WhyEngine[Why Am I Learning This Engine]
        FreshnessEngine[Content Freshness Engine]
    end

    subgraph studyTools [AI Study Tools]
        AudioLesson[Audio Lesson Generator + TTS]
        StudyGuide[Study Guide + Quick Summary]
        MindMap[Mind Map Generator]
        MagicNotes[Magic Notes - notes to flashcards]
        BrainBeats[Brain Beats - flashcards to songs]
        MemoryScore[Memory Score + Retention Prediction]
        URLIngest[URL + YouTube + Lecture Ingestion]
    end

    subgraph testPrep [Test Prep Engine]
        MockTestGen[Mock Test Generator]
        ScoringEngine[Descriptor-Locked Scoring]
        GapAnalysis[Gap Analysis + Score Prediction]
        IELTSModule[IELTS Speaking + Writing + Reading + Listening]
        SATModule[SAT + ACT + PSAT + 25 more profiles]
    end

    subgraph gamingEngine [Educational Gaming Engine - Optional Pathway]
        GameSelector[Game Selector - age + subject + learning style]
        AdaptiveDiff[Adaptive Difficulty - ZPD]
        GameTemplates[Game Templates - RPG, Escape Room, Simulation, etc.]
        MultiplayerEng[Multiplayer + Class Challenges]
    end

    subgraph interactiveTools [Interactive Tools - Built-in]
        Whiteboard[Digital Whiteboard - tldraw]
        CodeSandbox[Code Sandbox - Docker]
        MathEditor[Math Editor - MathLive]
        HomeworkScanner[Homework Scanner - OCR]
    end

    subgraph dataLayer [Data Layer]
        PG[(PostgreSQL 17 + pgvector)]
        RedisCache[(Redis)]
        BlobStorage[(S3 / Azure Blob)]
    end

    subgraph asyncWorkers [Async Workers - Celery]
        DocWorker[Document Processing Worker]
        EmbedWorker[Embedding Generation Worker]
        AudioWorker[Audio Lesson TTS Worker]
        URLWorker[URL + Lecture Ingestion Worker]
        AnalyticsWorker[Analytics Aggregation Worker]
        ReportWorker[Report Generation Worker]
        NotificationWorker[Notification Worker]
    end

    subgraph external [External - API Only]
        RootSite[Root Site API - auth/credits/catalog]
        LLMs[LLM Provider APIs]
        WhisperAPI[OpenAI Whisper + TTS APIs]
        ForgeOptional[ChatterMate Forge - optional deep link]
    end

    clients --> apiGateway
    apiGateway --> tutorEngine
    apiGateway --> aiEngine
    apiGateway --> ragEngine
    apiGateway --> learningEngine
    apiGateway --> engagementEngine
    apiGateway --> studyTools
    apiGateway --> testPrep
    apiGateway --> gamingEngine
    apiGateway --> interactiveTools
    tutorEngine --> dataLayer
    aiEngine --> dataLayer
    aiEngine --> LLMs
    ragEngine --> dataLayer
    learningEngine --> dataLayer
    engagementEngine --> dataLayer
    studyTools --> dataLayer
    studyTools --> LLMs
    studyTools --> WhisperAPI
    testPrep --> dataLayer
    testPrep --> LLMs
    testPrep --> WhisperAPI
    gamingEngine --> dataLayer
    gamingEngine --> LLMs
    interactiveTools --> dataLayer
    asyncWorkers --> dataLayer
    asyncWorkers --> WhisperAPI
    apiGateway --> RootSite
    aiEngine --> RootSite
    interactiveTools -.-> ForgeOptional
```

---

## 5. Authentication & Root Site Integration

```mermaid
sequenceDiagram
    participant User
    participant TutorFE as Tutor Frontend
    participant RootSite as Root Site API
    participant TutorAPI as Tutor Backend
    participant Redis

    User->>TutorFE: Visit tutor.clevercreator.ai
    TutorFE->>RootSite: Redirect to OAuth authorize
    User->>RootSite: Login + authorize
    RootSite->>TutorFE: Callback with auth code
    TutorFE->>TutorAPI: POST /auth/callback (code)
    TutorAPI->>RootSite: POST /api/oauth/token (exchange code)
    RootSite-->>TutorAPI: access_token + JWT
    TutorAPI->>Redis: Cache access_token:{user_id}
    TutorAPI->>RootSite: GET /api/user/details
    RootSite-->>TutorAPI: Profile + plan + credits
    TutorAPI->>TutorAPI: Upsert local tutor_users record
    TutorAPI-->>TutorFE: Set JWT cookie + user data

    Note over TutorAPI,RootSite: On every AI request
    TutorAPI->>TutorAPI: Estimate token cost
    TutorAPI->>RootSite: POST /api/user/credits/deduct (reserve)
    TutorAPI->>TutorAPI: Stream AI response
    TutorAPI->>RootSite: POST /api/user/credits/deduct (reconcile actual)
```

### Root Site API Integration Details:
- **`RootSiteClient`**: Service class in tutor backend for all root site API calls
- **OAuth 2.0**: Code exchange for authentication (`POST /api/oauth/token`)
- **`X-Auth-Hex`**: Header for service-to-service calls (internal API key)
- **Bearer Token**: For user-scoped API calls
- **Model Catalog**: Fetched with ETag caching (`GET /api/catalog`)
- **Credit Flow**: estimate -> reserve -> execute -> reconcile with `POST /api/user/credits/deduct`
- **Token Storage**: Sanctum access tokens cached in Redis (`access_token:{user_id}`)

---

## 6. Feature Overview (by Phase)

### Phase 1 — Foundation (8-10 weeks)
- [ ] FastAPI + Next.js 16 project scaffolding with Docker Compose
- [ ] Root site integration (OAuth, JWT, credits estimate/reserve/reconcile, catalog sync)
- [ ] 6 base tutor personas with system prompts
- [ ] Subject & topic browser (hierarchical, grade-level aware)
- [ ] Chat interface with 7 interaction modes (Teach Me, Quiz Me, Practice, Explore, Show Your Thinking, Writing Workshop, Debate/Roleplay)
- [ ] SSE streaming responses with real-time token output
- [ ] 8-layer prompt builder (persona + custom + mode + RAG + mastery + interests + standards + history)
- [ ] AI provider layer (OpenAI, Anthropic, Gemini, Grok) with fallback
- [ ] Safety layer (input/output moderation, age filter, anti-cheat, PII redaction)
- [ ] Basic RAG pipeline (teacher document upload, chunking, embedding, retrieval)
- [ ] Basic teacher dashboard (class management, student monitoring, KB upload, preview)
- [ ] Age-adaptive UI (4 grade-band layouts: K-2, 3-5, 6-8, 9-12)
- [ ] Student onboarding (role, grade, interests, learning style)
- [ ] Math rendering (KaTeX), code highlighting, Markdown
- [ ] Session history, continuity, and resume
- [ ] Quick action chips and conversation starters
- [ ] Mobile responsive layout
- [ ] Rate limiting + error handling

### Phase 2 — Intelligence & Study Tools (8-10 weeks)
- [ ] 3-level hint engine (server-enforced, prompt-controlled)
- [ ] Quiz mode with adaptive AI-generated questions + Explain My Answer
- [ ] Flashcard system with SM-2 spaced repetition
- [ ] **Magic Notes**: upload notes → auto-generate flashcards + quiz + study guide
- [ ] **URL-based learning**: paste URL or YouTube → learn from content
- [ ] **Auto-generated study guides** from topics, KB, or URLs
- [ ] **Quick Summary**: one-click summary of any document, URL, or video
- [ ] Multi-model AI routing (complexity-based, cost-optimized, auto-fallback)
- [ ] Teacher knowledge bases (full CRUD, class assignment, preview/test, standards tagging)
- [ ] Standards alignment engine (Common Core, NGSS import)
- [ ] Diagnostic assessment (placement testing, gap identification)
- [ ] Adaptive learning paths (auto-generated from mastery + standards)
- [ ] Misconception detection engine
- [ ] Interleaving engine (automatic old-topic review)
- [ ] Mastery tracking (5-level, per-topic and per-standard, with decay)
- [ ] Session summaries (AI-generated recap + next steps + email)

### Phase 3 — Engagement & Interactive Tools (8-10 weeks)
- [ ] Gamification (XP, age-themed levels, streaks, badges, class leaderboard)
- [ ] Parent dashboard (progress, reports, content controls, consent flow)
- [ ] Parent co-learning mode
- [ ] Interactive whiteboard (tldraw — draw-to-solve, AI draws)
- [ ] Built-in code sandbox (Docker-based Python/JS with Monaco Editor)
- [ ] Math editor (MathLive interactive input + MathJSON)
- [ ] **Audio Lesson Generator**: AI-scripted podcast-style lessons via TTS
- [ ] **Mind Map Generation**: visual topic organization with mastery overlay
- [ ] **Memory Score**: retention prediction + optimal review scheduling
- [ ] **Roleplay Scenarios**: subject-appropriate roleplay (history, science, language)
- [ ] Emotional intelligence layer (frustration/disengagement/boredom detection)
- [ ] Knowledge graph visualization with mastery overlay
- [ ] Mistake journal with pattern analysis
- [ ] "Why Am I Learning This?" engine
- [ ] **Lecture Recording Ingestion**: upload audio → Whisper transcription → study materials
- [ ] **Photo-Based Problem Solving**: enhanced OCR with animated step-by-step walkthrough
- [ ] Notification system (in-app, email)
- [ ] **Educational Gaming Engine**: game framework + adaptive difficulty + learning style adaptation
- [ ] **K-2 games**: Story Adventure, Matching, Virtual Pet, Treasure Hunt
- [ ] **3-5 games**: RPG Quest, Building Game, Mystery Detective, Fraction Pizza Shop
- [ ] **6-8 games**: Escape Room, Civilization Builder, Coding Maze, Speed Challenge
- [ ] **9-12 games**: Business Simulation, Debate Tournament, Case Study, Stock Market
- [ ] **Learning pathway selector**: onboarding preference + AI recommendation engine
- [ ] Game-to-mastery integration (games update same mastery tracker as chat)
- [ ] Teacher game assignments + game analytics

### Phase 4 — Scale, Test Prep & Compliance (10-12 weeks)
- [ ] **IELTS test prep**: speaking (AI examiner, Whisper), writing (band descriptors), reading, listening
- [ ] **SAT/ACT/PSAT test prep**: reading+writing, math sections, score prediction, NMSQT qualifier
- [ ] **AP Exam profiles**: per-subject rubrics, FRQ + MCQ practice
- [ ] **Test prep framework**: pluggable test profiles, mock tests, gap analysis, study plans
- [ ] LMS integrations (Google Classroom, Canvas via LTI 1.3)
- [ ] Content marketplace (teacher sharing, ratings, KB cloning)
- [ ] Advanced analytics (at-risk prediction, learning patterns, engagement metrics)
- [ ] Teacher AI co-pilot (lesson plans, assessments, class misconception reports)
- [ ] Homework scanner (OCR + guided solving, Photomath-style visual walkthrough)
- [ ] **Brain Beats**: convert flashcards to songs for memorization
- [ ] Compliance audit (COPPA, FERPA, GDPR)
- [ ] Accessibility audit (WCAG 2.1 AA, keyboard nav, screen reader)
- [ ] Multi-language support (i18n, RTL, AI content in preferred language, ESL mode)
- [ ] Micro-tutoring (5-minute quick review, daily concept, bus-stop audio)
- [ ] Wellness guardian (session limits, break reminders, quiet hours)

### Phase 5 — Beyond (ongoing)
- [ ] Mobile app (PWA with offline + optional React Native)
- [ ] Voice-first mode (STT + TTS — critical for K-2)
- [ ] **AI Video Call**: spontaneous video conversation with tutor character (language subjects)
- [ ] Digital learning portfolio (auto-compiled, exportable for college apps)
- [ ] Collaborative study rooms (2-5 students + AI moderator)
- [ ] Study group matching (complementary strengths)
- [ ] **SHSAT, ISEE, SSAT, HSPT** test prep profiles (high school admissions)
- [ ] **GED** test prep profile
- [ ] **TOEFL, GRE, Cambridge** test prep profiles (international English + graduate)
- [ ] Science simulations (PhET, Desmos embeds)
- [ ] Content freshness engine (current events, age-filtered)
- [ ] Study scheduling intelligence (optimal times, spaced sessions)
- [ ] University extension (course-level, professor tools, TA mode)
- [ ] **GMAT, LSAT, MCAT** test prep profiles (graduate/professional)
- [ ] **STEAM, AMC/AIME, Science Olympiad** prep modules
- [ ] **STAAR, Regents, MAP, SBAC** state assessment profiles
- [ ] **ASVAB, CLEP, CLT** additional test profiles
- [ ] Expanded game library: new templates quarterly, community game configs
- [ ] Multiplayer tournament system: school-wide and inter-school competitions
- [ ] Lecture recording ingestion (large-scale, multi-hour lectures)
- [ ] Edge AI (Phi, Gemma for offline on-device)
- [ ] AR/VR-ready APIs
- [ ] Optional Forge deep link for advanced CS projects

---

## 7. User Roles & Access Control

Auth lives in the root site. Roles are extended via the tutor module's own tables.

```mermaid
graph TB
    subgraph rootManaged [Managed by Root Site]
        UserAccount[User Account]
        SubPlan[Subscription Plan]
        CreditBalance[Token + Credit Balance]
    end

    subgraph tutorManaged [Managed by AI Tutor]
        subgraph teacherRole [Teacher Role]
            ManageClasses[Manage Classes]
            UploadMaterials[Upload Training Materials]
            CreatePersonas[Create Custom Tutors]
            MonitorStudents[Monitor Student Progress]
            CreateAssessments[Create Assessments]
            ShareContent[Share to Marketplace]
            AICoPilot[AI Co-Pilot for Teaching]
        end
        subgraph parentRole [Parent Role]
            ViewProgress[View Child Progress]
            SetRestrictions[Set Content Controls]
            ReceiveReports[Receive Reports]
            CoLearn[Co-Learning Mode]
            CommTeacher[Communicate with Teacher]
        end
        subgraph studentRole [Student Role]
            AccessTutors[Access Tutors]
            TakeSessions[Take Tutoring Sessions]
            EarnRewards[Earn XP and Badges]
            ViewOwnProgress[View Own Progress]
            UseTools[Use Interactive Tools]
        end
    end

    UserAccount --> teacherRole
    UserAccount --> parentRole
    UserAccount --> studentRole
    SubPlan --> CreditBalance
    CreditBalance --> TakeSessions
```

### Role Assignment:
- Users register on the root site with a base account
- When they access the tutor module, they choose/are assigned a role (teacher, parent, student)
- A single user can have multiple roles (e.g., a teacher who is also a parent)
- Role-specific data lives in the tutor module's database
- Parent-student links require consent flow (COPPA for under-13)

---

## 8. User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRY POINTS                             │
│  Root Site Dashboard  │  Direct URL  │  LMS Deep Link (Phase 4) │
└────────────────────────────┬────────────────────────────────────┘
                             │  OAuth authentication via root site
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               ONBOARDING (First-Time Users)                     │
│                                                                 │
│  What's your role?  [ Student ]  [ Teacher ]  [ Parent ]        │
│                                                                 │
│  Grade level?  [K] [1] [2] ... [12]                             │
│                                                                 │
│  What are your interests?                                       │
│  [ Basketball ] [ Gaming ] [ Music ] [ Art ] [ Cooking ] ...    │
│                                                                 │
│  How do you learn best?                                         │
│  [ Step-by-step ] [ Visual ] [ Stories ] [ Direct ] [ Hands-on ]│
│                                                                 │
│  Optional: Diagnostic placement test                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   TUTOR SELECTION SCREEN                        │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Sofia   │  │  Marcus  │  │   Aiko   │  │  Reza    │       │
│  │  Patient │  │ Socratic │  │ Creative │  │ Rigorous │       │
│  │  & Warm  │  │ & Deep   │  │ & Fun    │  │ & Direct │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐     │
│  │ Dr. Chen │  │  Alex    │  │  + Teacher's Custom Tutor │     │
│  │ Academic │  │ Peer-like│  │  (if assigned by teacher) │     │
│  └──────────┘  └──────────┘  └──────────────────────────┘     │
│                                                                 │
│  [Your last tutor: Sofia → Continue] [Browse All Tutors]        │
└────────────────────────────┬────────────────────────────────────┘
                             │  User selects tutor
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SUBJECT SELECTOR                              │
│                                                                 │
│  What do you want to study today?                               │
│                                                                 │
│  [Search: "quadratic equations..."                        ]     │
│                                                                 │
│  Browse:  Math  │  Science  │  ELA  │  History  │  CS  │ ...   │
│                                                                 │
│  [Upload a problem / PDF]    [Speak your question]              │
│  [View Knowledge Graph]     [Scan homework photo]               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TUTOR CHAT SESSION                          │
│  ┌──────────────────────────────┐  ┌────────────────────────┐  │
│  │         CHAT AREA            │  │     SESSION PANEL      │  │
│  │                              │  │                        │  │
│  │  Sofia: "Hi! I see you want  │  │  Topic:                │  │
│  │  to study quadratic          │  │  Quadratic Equations   │  │
│  │  equations. Let's start      │  │  Standard: CCSS.A.REI  │  │
│  │  with what you already       │  │                        │  │
│  │  know. What is a quadratic   │  │  Session Progress      │  │
│  │  expression to you?"         │  │  ████░░░░  3/8 goals   │  │
│  │                              │  │                        │  │
│  │  ─────────────────────────── │  │  Hints used: 1/3       │  │
│  │  [ Teach Me ][ Quiz Me ]     │  │  Cards saved: 2        │  │
│  │  [ Hint ][ Apply It ]        │  │  Quiz score: —         │  │
│  │  [ Show Thinking ]           │  │  Mastery: Level 2      │  │
│  │  [ Writing Workshop ]        │  │                        │  │
│  │                              │  │  ─────────────────────  │
│  │  ┌─────────────────────────┐ │  │  Saved Flashcards      │  │
│  │  │ Type your message...    │ │  │  • FOIL method          │  │
│  │  │                     ▶   │ │  │  • Discriminant         │  │
│  │  └─────────────────────────┘ │  │                        │  │
│  └──────────────────────────────┘  └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SESSION END SUMMARY                           │
│                                                                 │
│  Great work today with Sofia! Here's what you covered:          │
│  ✅ Mastered: FOIL method, factoring basics                     │
│  ⚠️  Needs review: Completing the square                        │
│  📊 Misconception detected: Sign errors in step 3              │
│  📚 3 flashcards saved  │  🎯 Quiz: 7/10 (70%)                 │
│  ⭐ +50 XP earned  │  🔥 5-day streak!                         │
│                                                                 │
│  [Review Mistakes] [Retake Quiz] [View Knowledge Graph]         │
│  [New Topic] [Daily Review] [Share with Parent]                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Tutor Roster & Personas

Each tutor has a distinct personality, teaching style, strength subjects, and a unique system prompt. Users feel like they're choosing a real tutor, not a toggle.

### Default Tutor Roster

| # | Name | Personality | Best For | Teaching Method |
|---|------|-------------|----------|----------------|
| 1 | **Sofia** | Patient, encouraging, nurturing | Beginners, math, science | Step-by-step with warmth; celebrates small wins |
| 2 | **Marcus** | Socratic, deep, challenging | Philosophy, history, literature | Asks questions back; never gives direct answers |
| 3 | **Aiko** | Playful, creative, energetic | Languages, arts, beginners | Stories, analogies, humor; makes abstract fun |
| 4 | **Reza** | Direct, rigorous, no-nonsense | Advanced STEM, coding | Worked examples; expects precision |
| 5 | **Dr. Chen** | Methodical, thorough, formal | College-level science, research | First principles; formal notation |
| 6 | **Alex** | Peer-like, collaborative, casual | All subjects, casual learners | Study buddy style; admits uncertainty |

### Custom Tutor Personas (Teacher-Created)
Teachers can create custom tutors that layer on top of base personas:
- Custom name, avatar, tone, teaching style
- Custom system prompt additions ("Always relate math to soccer for my students")
- Subject expertise tags
- Assigned to specific classes
- "Test Your Tutor" preview before deploying to students

### Tutor Card Design
Each selection card shows:
- Illustrated avatar (not a photo — illustrated feels safer + more unique)
- Name + one-line tagline ("The patient explainer")
- Teaching style badge: `Socratic` / `Step-by-Step` / `Direct` / `Peer`
- Subject strength tags: `Math` `Science` `Languages` `Coding`
- "Most popular" / "Best for beginners" labels

### Returning User Flow
- "Welcome back! Continue with **Sofia** on Quadratic Equations?" → one-click resume
- Tutor greets with context: "Last time we worked on factoring. You saved the discriminant rule as a flashcard — want to review that before we continue?"

---

## 10. Interaction Modes (7 Modes)

This is the single most important UX differentiator. Instead of a blank chat box, users explicitly choose **how** they want to learn.

### The Seven Mode Buttons

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│ [ Teach Me ] [ Quiz Me ] [ Hint ] [ Apply It ] [ Show Thinking ] [ Writing ] [ Roleplay ] │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

| Mode | Purpose | AI Behavior | Phase |
|------|---------|-------------|-------|
| **Teach Me** | Full explanation | Structured explanation with examples; uses student's interests for analogies; offers to rephrase | 1 |
| **Quiz Me** | Test knowledge | Asks one question, waits for answer, gives detailed feedback, escalates difficulty | 1 |
| **Hint** | Progressive hints (3 levels) | Level 1: vague nudge. Level 2: direction. Level 3: approach (no answer) | 1 |
| **Apply It** | Real-world application | Presents a real-world scenario that uses the concept | 1 |
| **Show Your Thinking** | Metacognition training | Student explains reasoning step-by-step; AI evaluates the PROCESS, not just the answer | 1 |
| **Writing Workshop** | Iterative writing feedback | Coach through drafts with rubric-based feedback; never writes for the student | 1 |
| **Debate/Roleplay** | Applied learning through conversation | Debate historical events, roleplay as scientists, practice language conversations in real-world scenarios | 3 |

### Hint Progression System (Server-Enforced)
```
User clicks [Hint] first time:
  → "Think about what changes when we multiply both sides..." (Level 1: nudge)

User clicks [Hint] again (2nd):
  → "Remember the zero-product property — if A × B = 0, what does that
     tell us about A and B?" (Level 2: relevant concept)

User clicks [Hint] again (3rd):
  → "Try factoring the left side. Look for two numbers that multiply
     to give +6 and add to give +5." (Level 3: approach without solution)

After 3rd hint:
  → [Show Full Solution] button appears (with: "You got this next time!")
```

Server tracks hint level per question — cannot be bypassed by client.

### "Show Your Thinking" Mode Detail
1. Tutor presents a problem
2. Student types their reasoning step-by-step (not just the answer)
3. AI evaluates each step for logical correctness, identifies where reasoning breaks
4. Feedback targets the PROCESS: "Your approach was right, but you skipped justifying why X equals Y"
5. Builds metacognitive skills that transfer across all subjects
6. Tracked separately in mastery: "reasoning quality" metric alongside "content accuracy"
7. Higher XP reward (15 XP vs 10) to incentivize deeper thinking

### Mode Persistence
- Selected mode persists until user changes it
- Visual indicator shows active mode (highlighted button)
- Natural language can override mode (typing "quiz me on this" auto-switches to Quiz)

---

## 11. Chat Interface Design

### Message Bubbles

**Tutor message:**
```
┌─────────────────────────────────────────────────────┐
│  [Avatar 32px]  Sofia  •  Just now                  │
│                                                     │
│  Let's break this down step by step.               │
│                                                     │
│  The quadratic formula is:                         │
│                                                     │
│  [KaTeX rendered: x = (-b ± √(b²-4ac)) / 2a]       │
│                                                     │
│  Where a, b, and c are the coefficients...          │
│                                                     │
│  [Source: Mrs. Johnson's Algebra Notes [1]]          │
│                                                     │
│  ─────────────────────────────────────────────────  │
│  [Save as Flashcard]  [Explain Differently]          │
│  [Copy]  [👍]  [👎]                                  │
└─────────────────────────────────────────────────────┘
```

**User message:**
```
                ┌──────────────────────────────────────┐
                │  what if b is negative?          You │
                │                          10:42 AM ✓  │
                └──────────────────────────────────────┘
```

### Streaming Indicator
- Show tutor avatar with pulsing `●●●` typing indicator
- Once tokens start: text appearing character by character
- Subtle "Thinking..." label during any reasoning/tool calls

### Rich Content Rendering
| Content Type | Renderer | Example |
|---|---|---|
| Math expressions | KaTeX | `$x = \frac{-b \pm \sqrt{b^2-4ac}}{2a}$` |
| Code blocks | Highlight.js / Prism | Python, JS, SQL with syntax colors |
| Markdown | react-markdown | Headers, lists, bold, italic |
| Tables | Rendered HTML | Comparison tables |
| Diagrams | Mermaid.js | Flowcharts, concept maps |
| Interactive math | MathLive | Student LaTeX input with live preview |
| Whiteboard | tldraw embed | Draw, diagram, graph |

### Quick Action Chips
After each tutor message, show contextual chips:
```
[Quiz me on this]  [Another example]  [I still don't get it]  [Move on →]
[Why do I need this?]  [Show on whiteboard]  [Save to flashcards]
```

### Conversation Starters
When a new session starts:
```
Sofia is ready to help! Try asking:

  "Explain the quadratic formula to me"
  "Quiz me on factoring"
  "I don't understand the discriminant"
  "Give me a practice problem"
  "Why do I need to learn this?"
```

---

## 12. Age-Adaptive UI

A 6-year-old and a 16-year-old should NOT see the same interface.

```mermaid
graph LR
    subgraph k2 [Grades K-2 - Ages 5-7]
        BigButtons[Large Colorful Buttons]
        VoiceFirst[Voice-First Input]
        AnimatedTutor[Animated Tutor Character]
        MinimalText[Minimal Text - Icons + Audio]
        SimpleRewards[Stickers + Stars + Sounds]
    end

    subgraph g35 [Grades 3-5 - Ages 8-10]
        GuidedUI[Guided Navigation]
        MoreText[Text + Visual Mix]
        DragDrop[Drag-and-Drop Interactions]
        StoryMode[Story-Based Learning]
        AvatarCustom[Customizable Avatar]
    end

    subgraph g68 [Grades 6-8 - Ages 11-13]
        FullChat[Full Chat Interface]
        SocialFeatures[Class Leaderboard]
        InteractiveTools[Whiteboard + Code]
        ChallengeMode[Challenge Mode]
        PeerElements[Study Buddy Features]
    end

    subgraph g912 [Grades 9-12 - Ages 14-18]
        ProUI[Professional Interface]
        AdvancedTools[Advanced STEM Tools]
        ExamPrep[Exam Prep Dashboard]
        CollegePrep[College Readiness]
        ResearchMode[Research + Writing Tools]
    end
```

### Implementation Details:
- Grade level set during onboarding, stored in user profile
- UI components conditionally render based on grade band
- Vocabulary in AI prompts calibrated per grade level
- Complexity of explanations automatically adjusted
- Gamification style changes:
  - **K-2**: Stickers, stars, celebration sounds, animated characters
  - **3-5**: Points, story progression, avatar customization
  - **6-8**: XP, levels, leaderboards, challenge modes
  - **9-12**: Achievement portfolio, college readiness metrics, professional badges

---

## 13. Adaptive Learning Engine

### Knowledge State Tracking

Each student maintains per-topic mastery stored in the database:

```
mastery_level: 0 (unknown) → 1 (introduced) → 2 (practicing) → 3 (mastered) → 4 (applying)
```

Updates based on:
- Correct quiz answers → +1 level
- 3 failed quiz attempts → -1 level, offer simpler explanation
- "I understand" signals → +0.5
- Hint requests on same topic → flag for review
- "Show Your Thinking" quality → reasoning_quality metric (0-100)

### Difficulty Scaling in Quiz Mode
```
mastery 0-1 → recall questions ("What is X?")
mastery 2   → application questions ("Use X to solve...")
mastery 3   → analysis questions ("Why does X work?")
mastery 4   → synthesis questions ("Design a system using X")
```

### Interest Personalization
At onboarding, users declare interests: "basketball / gaming / cooking / music"

Injected into system prompt so examples are always contextual:
> Instead of: "If you have 3 apples and add 5..."
> With interest=basketball: "If Steph Curry makes 3 three-pointers in the first half and 5 in the second..."

### Session Continuity
Every session stores: topics covered, hints needed, quiz scores, flashcards saved, misconceptions detected, emotional states.

On return: "Welcome back! Last time we worked on quadratic equations. You saved the discriminant rule as a flashcard — want to review that before we continue?"

### Interleaving Engine
Cognitive science shows interleaved practice produces 43% better retention:
- AI automatically weaves review of old topics into new sessions
- "Before we start trigonometry, let's do a quick check on the Pythagorean theorem"
- Spacing algorithm determines which old topics are due for review
- Students don't choose — the AI manages this seamlessly

### Misconception Detection
When a student makes an error, AI identifies the specific misconception:
- Example: Student says 1/3 + 1/4 = 2/7
- Tutor: "You added numerators and denominators separately. This is a common fraction misconception. Fractions need a common denominator first."
- Tracks patterns over time: "This student consistently makes sign errors in algebra"
- Teachers see class-wide misconception reports

---

## 14. RAG Pipeline — Custom Training

This is how teachers and parents "train" their tutors with custom materials.

```mermaid
flowchart TB
    subgraph teacherActions [Teacher Actions]
        Upload[Upload Materials - PDF/DOCX/PPTX/TXT/Images]
        CreateKB[Create Knowledge Base]
        TagStandards[Tag with Standards - AI-assisted]
        AssignClasses[Assign to Classes]
        PreviewTutor[Test Trained Tutor]
    end

    subgraph ingestion [Ingestion Pipeline - Celery Workers]
        FileStore[Store Raw File in S3]
        Extract["Extract Text (pypdf/python-docx/python-pptx/tesseract)"]
        Chunk["Semantic Chunking (section-aware, 400w, 50 overlap)"]
        Embed["Generate Embeddings (text-embedding-3-small)"]
        Index[Index in pgvector with HNSW]
    end

    subgraph queryTime [Student Query Time]
        Question[Student Asks Question]
        Scope[Scope Filter - enrolled classes + assigned KBs]
        QueryEmbed[Embed Query]
        Search["Cosine Similarity Search (pgvector)"]
        Rerank[Cross-Encoder Rerank Top-K]
        BuildContext["Build Context with [1][2] Citations"]
    end

    subgraph promptAssembly [Prompt Assembly - 8 Layers]
        L1[1. Base Persona System Prompt]
        L2[2. Custom Persona Overlay]
        L3[3. Mode Rules]
        L4[4. RAG Retrieved Context]
        L5[5. Student Mastery + Misconception History]
        L6[6. Student Interests + Learning Style]
        L7[7. Standards Context]
        L8[8. Session History - first2 + last15 + summary]
        FinalPrompt[Assembled Prompt]
    end

    Upload --> FileStore
    Upload --> Extract
    CreateKB --> TagStandards
    Extract --> Chunk
    Chunk --> Embed
    Embed --> Index
    AssignClasses --> Scope

    Question --> Scope
    Scope --> QueryEmbed
    QueryEmbed --> Search
    Search --> Rerank
    Rerank --> BuildContext

    L1 --> FinalPrompt
    L2 --> FinalPrompt
    L3 --> FinalPrompt
    BuildContext --> L4
    L4 --> FinalPrompt
    L5 --> FinalPrompt
    L6 --> FinalPrompt
    L7 --> FinalPrompt
    L8 --> FinalPrompt
```

### Knowledge Base Scoping Rules:
- Each KB belongs to a teacher
- Teacher assigns KB to specific classes + subjects + grade levels
- During retrieval, ONLY KBs assigned to the student's enrolled classes are searched
- Platform-wide KBs can be created by admins (Common Core aligned content)
- Teachers can share KBs to a marketplace for others to clone
- Students never see raw uploaded materials — only AI-mediated responses with citations

### RAG Configuration (tunable per knowledge base):
| Parameter | Default | Description |
|---|---|---|
| `CHUNK_SIZE` | 400 words | Semantic boundaries respected |
| `CHUNK_OVERLAP` | 50 words | Context preservation between chunks |
| `MIN_SIMILARITY` | 0.65 | Minimum cosine similarity threshold |
| `MAX_CHUNKS` | 10 | Maximum chunks injected into prompt |
| `EMBEDDING_MODEL` | text-embedding-3-small | Swappable |
| `EMBEDDING_DIMS` | 1536 | Vector dimensions |

---

## 15. AI Engine Architecture

```mermaid
flowchart TB
    subgraph safety [Safety Layer - Education Specific]
        InputMod[Input Moderation API]
        AgeVocab["Age-Calibrated Vocabulary (K-2 vs Grade 11)"]
        AntiCheat[Anti-Cheating Guard - no homework solving]
        ContentBounds[Content Boundaries - redirect inappropriate]
        OutputMod[Output Moderation]
    end

    subgraph prompt [Prompt Engine - 8 Layers]
        BasePersona[Base Persona Prompt]
        CustomOverlay[Teacher Custom Overlay]
        ModeRules["Mode Rules (6 modes)"]
        RAGContext[RAG Retrieved Context]
        StudentContext[Mastery + Misconceptions + Learning Style]
        InterestContext[Interest Personalization]
        StandardsCtx[Standards Alignment Context]
        HistoryCtx["History (first2 + last15 + summary)"]
    end

    subgraph router [Model Router]
        ComplexityEst[Query Complexity Estimator]
        CostOpt[Cost Optimizer - user credit budget]
        PlanAccess[Plan-Based Model Access - from catalog]
        Fallback[Auto-Fallback on Provider Error]
    end

    subgraph providers [LLM Providers - Direct httpx Calls]
        OpenAI[OpenAI - GPT-4o + 4o-mini]
        Claude[Anthropic - Claude Sonnet + Haiku]
        Gemini[Google - Gemini Pro + Flash]
        Grok[xAI - Grok]
    end

    subgraph streaming [Streaming]
        SSEManager[SSE Stream Manager]
        TokenCounter[Token Counter + Cost Tracker]
        CreditReconcile[Credit Reconciliation with Root Site]
    end

    Request[Student Message] --> safety
    safety --> prompt
    prompt --> router
    router --> providers
    providers --> streaming
    streaming --> SSEManager
    TokenCounter --> CreditReconcile
```

### Model Routing Strategy:
| Use Case | Recommended Model | Why |
|---|---|---|
| K-2 simple explanations | GPT-4o-mini, Gemini Flash | Cost-efficient, simple language |
| Complex STEM reasoning | GPT-4o, Claude Sonnet | Accuracy critical |
| Creative storytelling/analogies | Claude Sonnet | Empathetic, creative |
| Code tutoring | GPT-4o, Claude Sonnet | Strong code explanation |
| Show Your Thinking evaluation | Claude Sonnet | Strong reasoning analysis |
| Writing Workshop feedback | Claude Sonnet | Nuanced writing critique |

- **Model availability**: Filtered by user's subscription plan via root site catalog
- **Auto-fallback**: If primary provider fails, seamlessly route to secondary
- **Cost optimization**: Auto-downgrade when approaching credit limits

### Education-Specific Safety:
- Age-appropriate vocabulary enforcement via system prompt calibration
- Anti-cheating: Refuses to write essays, complete homework, solve take-home tests
- Content boundaries: Redirects inappropriate topics; rejects medical/legal/dangerous
- Mandatory source attribution when using RAG content
- Input moderation before LLM; output moderation before display
- All safety decisions logged for audit

---

## 16. Tutoring Session Workflow

```mermaid
sequenceDiagram
    participant S as Student
    participant FE as Tutor Frontend
    participant API as Tutor Backend
    participant Root as Root Site API
    participant RAG as RAG Engine
    participant AI as AI Engine
    participant DB as PostgreSQL
    participant LLM as LLM Provider

    Note over S,FE: Session Start
    S->>FE: Select tutor + subject + grade
    FE->>API: POST /api/sessions
    API->>DB: Load student mastery, interests, misconceptions, learning style
    API->>DB: Load persona system prompt + teacher custom overlay
    API->>Root: GET /api/user/credits
    Root-->>API: Balance confirmed
    API-->>FE: Session context + suggested conversation starters

    Note over S,FE: During Session
    S->>FE: Ask question (mode: Teach Me)
    FE->>API: POST /api/sessions/{id}/chat (SSE)

    API->>API: Safety check (input moderation + age filter)
    API->>API: Estimate token cost
    API->>Root: POST /api/user/credits/deduct (reserve)

    API->>RAG: Search teacher knowledge bases (scoped to student classes)
    RAG->>DB: pgvector cosine similarity search
    DB-->>RAG: Top-K chunks with citations
    RAG-->>API: Retrieved context

    API->>AI: Build 8-layer prompt
    API->>AI: Route to optimal model
    AI->>LLM: Stream completion
    LLM-->>AI: Token stream
    AI-->>API: Safety check output
    API-->>FE: SSE stream tokens

    API->>Root: Reconcile actual token cost
    API->>DB: Save message + update mastery + log misconceptions + update analytics
    API-->>FE: Quick action chips + balance update

    Note over S,FE: Interleaving Check
    API->>API: Interleaving engine checks if old topic review is due
    API-->>FE: Optional interleaved review question

    Note over S,FE: Emotional Check
    API->>API: Analyze interaction patterns for frustration/disengagement
    API-->>FE: Adjust tone if needed

    Note over S,FE: Session End
    S->>FE: End session
    FE->>API: POST /api/sessions/{id}/end
    API->>LLM: Generate session summary
    API->>DB: Save summary + update mastery + mistake journal + portfolio
    API-->>FE: Session summary + XP earned + badges
```

### Context Window Management:
- Sessions < 20 messages: keep full history
- Longer sessions: first 2 messages (setup) + last 15 messages + rolling summary of earlier
- Track `tokens_used` per session; warn at 80% of model context limit

---

## 17. Standards Alignment Engine

K-12 tutoring without standards alignment is a toy, not a tool.

### Standards Supported:
- **Common Core State Standards (CCSS)** — Math, ELA
- **Next Generation Science Standards (NGSS)**
- **State-specific standards** (all 50 US states have variations)
- **International**: IB, Cambridge, national curricula
- **Test prep**: AP, SAT, ACT

### Implementation:
- Standards stored as hierarchical tree: Framework → Domain → Cluster → Standard → Sub-standard
- Every topic, assessment question, and learning objective tagged with standard codes
- Teachers can map uploaded materials to standards (AI-assisted auto-tagging)
- Progress reports show mastery per standard (required by many school districts)
- Diagnostic assessments identify which standards have gaps
- AI uses standards context in prompts for grade-appropriate explanations
- Knowledge graph nodes linked to standards codes

---

## 18. Teacher Portal

### Knowledge Base Management
- Upload materials (PDF, DOCX, PPTX, images, video links, TXT, MD)
- Organize by subject, grade, unit, topic
- Tag with standards codes (AI auto-suggests tags)
- Set visibility: private (my classes), school-wide, marketplace
- Processing status indicators (queued, processing, ready, failed)
- Version history — update without losing old embeddings
- "Test Your Tutor" — chat with the trained tutor before deploying

### Custom Tutor Personas
- Create personality layered on base personas (name, avatar, tone, teaching style)
- Add custom system prompt instructions
- Preview before assigning to classes

### Class Management
- Create classes with invite codes
- Bulk import students via CSV
- LMS sync (Google Classroom, Canvas — Phase 4)
- Assign personas, knowledge bases, and learning paths per class

### Student Monitoring
- Real-time active session view
- Mastery heatmap per student per standard
- Misconception pattern reports
- Time-on-task and engagement metrics
- Struggle detection alerts
- Session replay (read-only view of student-tutor conversation)

### AI Co-Pilot for Teachers
- "How should I teach X to my class?" — AI analyzes class data and suggests strategies
- Auto-generate differentiated worksheets (3 difficulty levels)
- Draft parent communications based on student progress
- Meeting prep: auto-generated progress summaries for parent-teacher conferences
- Identify which students need in-person attention

### Assessment Creator
- AI-generate quizzes from uploaded knowledge base materials
- Manual question creation (MCQ, free response, fill-in-blank, matching)
- Rubric builder for subjective assessments
- Import from QTI format (LMS interoperability)
- Standards-tagged questions

---

## 19. Parent Dashboard

### Progress Overview
- Per-subject mastery radar chart
- Time spent per subject per week
- Sessions completed, questions asked, hints used
- Standards mastery vs. grade-level expectations

### Activity Feed
- Daily log: topics studied, performance, time
- Streak and XP updates
- Milestone celebrations

### Reports
- Auto-generated weekly/monthly PDF reports
- Standards-aligned progress
- Comparison to grade-level expectations (not peers)
- Emailed on schedule or downloadable

### Content Controls
- Approve/restrict subjects or topics
- Daily/weekly time limits
- Age-appropriate content level override
- Block specific interaction modes
- Quiet hours (no late-night sessions)

### Parent Co-Learning
- Join child's session in guided mode
- Tutor coaches both parent and child
- "Homework Help" mode — parent doesn't need subject expertise
- Weekly family challenge

### Communication
- In-app messaging with teachers
- Alert preferences (email, push, in-app)
- Alerts: struggling, inactive, milestone achieved

---

## 20. Innovations — Outside the Box

These features separate a great tutor from a chatbot. No competitor does all of these well.

### 20.1 Misconception Detection Engine
Most tutors say "wrong." Great tutors diagnose WHY.
- Database of common misconceptions per subject per grade per topic
- When a student errs, AI identifies the specific misconception
- Tracks patterns over time: "This student consistently makes sign errors in algebra"
- Teachers see class-wide reports: "73% of your class has the fraction addition misconception"

### 20.2 Knowledge Graph Visualization
Students see subjects as disconnected topics. Great tutors show connections.
- Interactive visual graph showing concept relationships (react-flow/D3.js)
- Student's mastery level overlaid as color intensity on each node
- Click any node to start a tutoring session on that concept
- Cross-subject connections: "The ratio concept in math = proportions in chemistry"

### 20.3 Emotional Intelligence Layer
Frustration is the #1 reason students give up. Detection from interaction patterns alone:
- Response time + accuracy dropping = frustration
- Multiple wrong answers on same concept = confusion
- Long pauses then single-word responses = disengagement
- Typing then deleting repeatedly = uncertainty

Interventions: shift tone, auto-simplify, suggest a break, offer easier confidence-building problem.

### 20.4 "Why Am I Learning This?" Engine
Every topic has mapped real-world career connections, personalized to student interests:
- "You want to be a game developer? Here's how trigonometry powers game physics."
- "You love cooking? Ratios and proportions determine every recipe."

### 20.5 Mistake Journal + Pattern Analysis
Auto-compiled log of every mistake: original question, student answer, correct answer, misconception, explanation that finally worked. Reviewable before tests.

### 20.6 Teacher AI Co-Pilot
The tutor helps teachers, not just students:
- Suggests teaching strategies based on class data
- Generates differentiated worksheets (3 difficulty levels)
- Drafts parent communications
- Auto-generates parent-teacher conference summaries

### 20.7 Micro-Tutoring (5-Minute Sessions)
- "Quick Quiz": 3-5 targeted questions in 5 minutes
- "Daily Review": spaced repetition review
- "Concept Refresh": 2-minute re-explanation
- 5 min/day × 365 = 30+ hours additional learning per year

### 20.8 Parent Co-Learning Mode
Parent and child in the same session. Tutor adjusts for two audiences. Weekly family challenge.

### 20.9 Digital Learning Portfolio
Auto-compiled: mastery timeline, best work, standards mastered, badges, self-reflections. Useful for parent-teacher conferences and college applications.

### 20.10 Homework Scanner with Guided Solving
Photo of a problem → OCR → identify concept → guide through solving (never solve it). Anti-cheat: logs all interactions for teacher review.

### 20.11 Content Freshness Engine
Current events as examples (age-filtered, teacher-approvable):
- "The Mars rover landing is a great example of the physics you're studying"
- Fallback to curated database when web search is off

### 20.12 Wellness Guardian
- Grade-appropriate session limits: K-2 max 20 min, 3-5 max 30 min, 6-8 max 45 min, 9-12 max 60 min
- Late-night detection: "It's 11 PM on a school night. Let's save this for tomorrow."
- Parent-configurable quiet hours
- Eye strain reminders (20-20-20 rule)
- Post-session cooldown: breathing exercise or fun fact

---

## 21. AI-Powered Study Tools (NotebookLM / Quizlet / Duolingo Inspired)

Features inspired by [Google NotebookLM](https://notebooklm.google/), [Quizlet](https://quizlet.com), [Duolingo Max](https://blog.duolingo.com/video-call), and [Khanmigo](https://www.khanmigo.ai/).

### 21.1 Audio Lesson Generator ("Deep Dive")
Turn any topic or KB material into a podcast-style audio lesson:
- **Formats**: Brief (2 min overview), Deep Dive (10 min detailed), Debate (two perspectives), Story Mode (narrative for K-5)
- **How**: AI scripts a two-host conversational dialogue, rendered via TTS (OpenAI TTS API or ElevenLabs)
- **Use cases**: Auditory learners, students with dyslexia, bus/commute time, K-2 pre-readers
- **Teacher control**: Generate from uploaded KB materials; review before publishing to class
- **Phase**: 3

### 21.2 URL-Based Learning
Paste a URL and learn from it:
- **Article/webpage**: Scrape content, add to session or KB, teach from it, generate flashcards/quiz/study guide
- **YouTube video**: Extract transcript via YouTube API, create study materials from lecture content, answer questions about the video
- **Wikipedia**: Structured extraction with section awareness
- **Ingested as**: Temporary session context or permanent KB document
- **Phase**: 2

### 21.3 Auto-Generated Study Guides
Structured study documents generated from any source:
- **From a topic**: Key concepts, definitions, formulas, common mistakes (from misconception engine), practice problems (graduated difficulty), quick-reference summary card
- **From teacher KB**: Study guide following the structure of uploaded materials
- **Pre-test study guide**: Based on student's mistake journal + weak mastery areas
- **Export**: PDF, printable, shareable link
- **Phase**: 2

### 21.4 Mind Map Generation
Visual topic organization:
- Main concept at center, sub-topics branching out, key facts on each branch
- Color-coded by mastery level (merges with Knowledge Graph)
- Interactive: click any branch to start a tutoring session
- Export: Image, PDF, interactive web view
- **Phase**: 3

### 21.5 Magic Notes (Quizlet-Inspired)
Convert any notes into study materials:
- Upload handwritten notes (image + OCR) or typed notes
- AI auto-generates: flashcards, quiz questions, study guide outline, essay topics
- **Phase**: 2

### 21.6 Brain Beats (Quizlet-Inspired)
Convert flashcards into songs for memorization:
- AI generates catchy lyrics from flashcard content
- Rendered via TTS with rhythm/beat
- Especially effective for K-5 learners (multiplication tables, vocabulary, historical dates)
- **Phase**: 4

### 21.7 Memory Score (Quizlet-Inspired)
Predict retention and optimize review:
- Track personal memory performance per topic
- Predict retention at different time intervals
- Recommend optimal review timing ("You'll forget 40% of fractions by Thursday — review Wednesday")
- Feeds into the Interleaving Engine and spaced repetition scheduler
- **Phase**: 3

### 21.8 Quick Summary
Extract key concepts from dense content:
- One-click summary of any uploaded document, URL, or YouTube video
- Adjustable length: 1-paragraph, 1-page, detailed
- Highlight key terms with definitions
- **Phase**: 2

### 21.9 AI Video Call (Duolingo-Inspired — Language Learning)
Spontaneous video conversation with tutor character:
- For language subjects: practice speaking with the AI tutor in target language
- Tutor adjusts to skill level, maintains persona personality
- Remembers personal details from previous sessions
- Pronunciation feedback with phonetic highlighting
- 1-3 minutes per session based on proficiency
- **Phase**: 5

### 21.10 Roleplay Scenarios (Duolingo-Inspired)
Practice real-world conversations:
- Language: Ordering food, asking for directions, job interview
- History: Debate as historical figures
- Science: Role-play as scientists defending theories
- Builds applied knowledge and communication skills
- **Phase**: 3

### 21.11 Explain My Answer (Duolingo-Inspired)
After any quiz or assessment:
- One-click detailed explanation of WHY the answer is correct/incorrect
- Highlights specific grammar, vocabulary, or conceptual errors
- Links to relevant tutoring sessions for deeper learning
- Already partially in our quiz system — formalize as a dedicated feature
- **Phase**: 2

### 21.12 Lecture Recording Ingestion
Students upload lecture recordings:
- Supported: MP3, WAV, M4A, MP4 (audio track)
- AI transcribes via Whisper API
- Generates: summary, flashcards, study guide, quiz from the lecture
- Chat: "What did the professor say about mitosis?"
- **Phase**: 3

### 21.13 Photo-Based Problem Solving (Photomath/Socratic-Inspired)
Enhanced homework scanner:
- Camera capture or image upload of any problem (math, science, text)
- AI identifies the problem type and subject
- For math: animated step-by-step visual solution walkthrough (not just text)
- For text: identify key concepts and guide understanding
- Links to related educational videos when available
- **Phase**: 3

---

## 22. Educational Gaming Engine (Optional Learning Pathway)

> **Key principle**: The Gaming Engine is an **additional** learning pathway — not a replacement for chat-based tutoring, quizzes, flashcards, or study tools. Students who are motivated by game-based learning can opt into this pathway. All game activities feed into the **same mastery tracker, misconception engine, and standards alignment** as every other learning mode. Same learning outcomes, different engagement vehicle.

### 22.1 How Games Fit Into the Platform

```mermaid
flowchart TB
    subgraph learningPathways [Student Learning Pathways - Student Chooses]
        ChatTutor[Chat-Based Tutoring - 7 modes]
        QuizFlash[Quizzes + Flashcards]
        StudyTools[Study Tools - guides, audio, mind maps]
        GamePath[Educational Games]
        TestPrep[Test Prep]
    end

    subgraph gameEngine [Educational Gaming Engine]
        GameSelector[Game Selector - by age, subject, style]
        AdaptiveDifficulty[Adaptive Difficulty - zone of proximal development]
        GameTemplates[Subject Game Templates]
        MultiplayerEngine[Multiplayer + Class Challenges]
        GameRewards[Game Rewards - XP, unlocks, cosmetics]
    end

    subgraph sharedEngines [Shared Learning Engines - Same for All Pathways]
        MasteryTracker2[Mastery Tracker]
        MisconceptionEngine2[Misconception Detection]
        StandardsEngine2[Standards Alignment]
        ProgressReports[Progress Reports - teacher + parent]
    end

    learningPathways --> sharedEngines
    GamePath --> gameEngine
    gameEngine --> sharedEngines
    GameSelector -->|"detects or asks"| AdaptiveDifficulty
    AdaptiveDifficulty --> GameTemplates
```

### 22.2 Onboarding & Pathway Detection
- During onboarding, students indicate learning preference: "How do you like to learn?" (talk to a tutor, practice questions, play games, listen/watch, mix of everything)
- System tracks engagement metrics per pathway over time
- AI recommends pathway switches: "You seem to learn fractions faster through games — want to try Fraction Pizza Shop?"
- Students can switch pathways at any time — they are never locked in
- Teachers can assign specific games for targeted remediation
- Parents see unified progress regardless of pathway used

### 22.3 Game Types by Age Band

#### K-2 (Ages 5-7) — Exploration & Discovery
| Game Type | Example | Subject | Learning Objective |
|---|---|---|---|
| Story Adventure | "Help the Dragon Count" — solve counting puzzles to help a dragon collect treasure | Math | Counting, addition, number sense |
| Drag-and-Drop Match | Match shapes to their names, match letters to sounds | Math, ELA | Shape recognition, phonics |
| Coloring Challenge | Color the picture by solving: "Color the triangle blue, the circle red" | Math | Shape + color identification |
| Treasure Hunt | "Find 3 things that start with the letter B" — interactive room exploration | ELA | Phonics, vocabulary |
| Rhythm Game | Tap along to counting songs, phonics beats | Math, ELA | Number sequences, letter sounds |
| Virtual Pet | Feed your pet by answering questions correctly — pet grows and evolves | Any | Motivation through nurturing |
| Storytime Builder | Choose-your-own-adventure where choices require reading comprehension | ELA | Reading comprehension |

#### 3-5 (Ages 8-10) — Quest & Construction
| Game Type | Example | Subject | Learning Objective |
|---|---|---|---|
| RPG Quest | Battle monsters by solving math problems (Prodigy-style) — earn gear and abilities | Math | Operations, fractions, geometry |
| Building Game | Build a bridge using geometric shapes — bridge must support weight | Math, Science | Geometry, physics basics |
| Mystery Detective | "The Water Cycle Mystery" — gather clues about evaporation, condensation, precipitation to solve the case | Science | Water cycle, scientific method |
| Team Challenge | Class-based collaborative puzzle — each student solves a piece | Any | Collaboration + subject mastery |
| Experiment Lab | Mix virtual chemicals, observe reactions, record observations | Science | Scientific method, chemistry basics |
| Word Factory | Build words from prefixes, roots, suffixes — manufacture as many as possible | ELA | Vocabulary, word structure |
| Timeline Builder | Arrange historical events on a timeline — unlock story segments | History | Chronological thinking |
| Fraction Pizza Shop | Run a pizza shop — customers order fractions of pizza, make correct slices | Math | Fractions, division |

#### 6-8 (Ages 11-13) — Strategy & Competition
| Game Type | Example | Subject | Learning Objective |
|---|---|---|---|
| Escape Room | Solve 5 subject problems to unlock each room — 30-minute timed challenge | Any | Applied problem solving |
| Civilization Builder | Manage resources, population, economy — decisions require math and history | Math, History | Economics, ratios, historical context |
| Speed Challenge | Timed individual or class competition — solve equations fastest with accuracy bonus | Math | Fluency, accuracy |
| Virtual Science Lab | Design experiments, control variables, analyze data, draw conclusions | Science | Scientific method, data analysis |
| Coding Maze | Program a robot to navigate a maze — block-based or text coding | CS | Algorithms, logic, sequencing |
| Debate Arena | AI-moderated debate on historical/scientific topics — scored on evidence and reasoning | History, Science | Argumentation, critical thinking |
| Grammar Quest | RPG where spells are grammar rules — cast "Past Tense" to defeat the Verb Monster | ELA | Grammar, sentence structure |
| Ecosystem Simulator | Build and maintain an ecosystem — species interactions, food chains, balance | Science | Ecology, systems thinking |

#### 9-12 (Ages 14-18) — Simulation & Real-World
| Game Type | Example | Subject | Learning Objective |
|---|---|---|---|
| Business Simulation | Launch a startup — budgeting, revenue projections, market analysis with real math | Math, Economics | Financial literacy, algebra, statistics |
| Debate Tournament | Formal AI-scored debates on complex topics — multiple rounds, evidence required | History, Science, ELA | Argumentation, research, rhetoric |
| Case Study Mystery | Analyze real data sets, form hypotheses, present findings — detective format | Science, Math | Data analysis, critical thinking |
| Entrepreneurship | Design a product, calculate manufacturing costs, create marketing plan, pitch to AI investors | Math, ELA | Applied math, persuasive writing |
| Mock Trial | Role-play lawyer/witness/judge — build arguments using historical/legal facts | History, ELA | Logic, evidence, public speaking |
| Model UN | Represent a country, negotiate resolutions, draft policy documents | History, Geography | Geopolitics, diplomacy, writing |
| Stock Market Sim | Invest virtual money, track real-time data, analyze trends, calculate returns | Math | Statistics, percentages, finance |
| Research Lab | Design and run multi-step experiments with realistic data — publish findings | Science | Research methodology, statistical analysis |

### 22.4 Learning Style Adaptations in Games

The same game adapts its presentation based on the student's learning style preference:

| Learning Style | How Games Adapt | Example |
|---|---|---|
| **Visual** | Diagrams, color-coded feedback, visual pattern matching, infographic rewards | Math problems shown as visual bar models, not just equations |
| **Auditory** | Voice narration, sound effects for correct/incorrect, audio clues, rhythm elements | Game narrator reads problems aloud, success sounds, verbal hints |
| **Kinesthetic** | Drag-and-drop, building mechanics, swipe gestures, interactive manipulation | Physically drag fraction pieces onto a pizza, arrange timeline events |
| **Reading/Writing** | Text-based clues, written challenges, journaling components, essay integration | Mystery clues are written passages, bonus XP for written explanations |

### 22.5 Game-to-Mastery Integration

Every game interaction maps back to the learning engine:
- **Correct answer in game** → mastery score increase for that topic
- **Incorrect answer in game** → logged in mistake journal with game context
- **Pattern of errors** → misconception detection triggers (same engine as chat)
- **Game completion** → standards alignment check (which standards were addressed)
- **Difficulty progression** → zone of proximal development maintained (adaptive)
- **Time spent** → included in session analytics and wellness guardian limits

### 22.6 Multiplayer & Social

- **Class challenges**: Teacher creates a challenge, whole class competes/collaborates
- **Paired learning**: Two students work together on a game (complementary strengths)
- **Leaderboards**: Opt-in, class-level, weekly reset (never global to avoid toxic competition)
- **Friend challenges**: "Challenge a friend to Equation Race"
- **AI opponents**: For students who want competition but no classmates are available

### 22.7 Teacher Controls for Games

- Assign specific games to specific students/classes for targeted remediation
- Lock/unlock game types per class (e.g., no competition games for a sensitive class)
- Set time limits on game play per day
- View game analytics: which games are most effective for which topics
- Create custom game parameters: "Only fractions, difficulty 3-5, 15 minutes"

### 22.8 Game Database Schema

```sql
CREATE TABLE game_templates (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    game_type       VARCHAR(50) NOT NULL,              -- rpg, escape_room, simulation, etc.
    age_band        VARCHAR(10) NOT NULL,              -- K-2, 3-5, 6-8, 9-12
    subjects        TEXT[] NOT NULL,                    -- {math, science, ela}
    topics          TEXT[],                             -- specific topics covered
    standards       TEXT[],                             -- standards addressed
    learning_styles TEXT[] DEFAULT '{visual,auditory,kinesthetic,reading}',
    min_players     SMALLINT DEFAULT 1,
    max_players     SMALLINT DEFAULT 1,
    duration_min    SMALLINT DEFAULT 10,
    difficulty_range INT4RANGE DEFAULT '[1,10]',
    config_json     JSONB,                             -- game-specific configuration
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE game_sessions (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    template_id     INTEGER NOT NULL REFERENCES game_templates(id),
    difficulty      SMALLINT DEFAULT 1,
    score           INTEGER DEFAULT 0,
    questions_total INTEGER DEFAULT 0,
    questions_correct INTEGER DEFAULT 0,
    topics_covered  TEXT[],
    mastery_updates JSONB,                             -- {topic: delta} applied to mastery tracker
    mistakes_logged JSONB,                             -- fed to mistake journal
    duration_seconds INTEGER,
    completed       BOOLEAN DEFAULT FALSE,
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

CREATE TABLE game_assignments (
    id              SERIAL PRIMARY KEY,
    teacher_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    class_id        INTEGER NOT NULL REFERENCES classes(id),
    template_id     INTEGER NOT NULL REFERENCES game_templates(id),
    config_override JSONB,                             -- teacher customization
    due_date        DATE,
    assigned_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE game_leaderboard (
    id              SERIAL PRIMARY KEY,
    class_id        INTEGER NOT NULL REFERENCES classes(id),
    template_id     INTEGER NOT NULL REFERENCES game_templates(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    score           INTEGER NOT NULL,
    week_start      DATE NOT NULL,
    UNIQUE(class_id, template_id, student_id, week_start)
);
```

### 22.9 Game API Endpoints

```
GET    /api/games/templates                     → List available games (filtered by age, subject, style)
GET    /api/games/templates/{id}                → Get game configuration
POST   /api/games/sessions                      → Start a game session
POST   /api/games/sessions/{id}/answer          → Submit an answer within a game
POST   /api/games/sessions/{id}/complete        → Complete game session (triggers mastery update)
GET    /api/games/sessions/{id}/results         → Get game results + mastery impact
GET    /api/games/history                       → Student's game history
GET    /api/games/leaderboard/{class_id}        → Class leaderboard for a game
POST   /api/games/assignments                   → Teacher assigns game to class
GET    /api/games/recommendations               → AI-recommended games based on learning gaps + style
```

---

## 23. Test Prep Framework (IELTS, SAT, ACT, AP, and International)

A modular test prep system that plugs into the existing tutoring engine. Each test type is a "test profile" with its own scoring rubric, question formats, timing rules, and band/score descriptors.

### 23.1 Supported Tests (Complete Roadmap)

| Test | Type | Sections | Scoring | Phase |
|---|---|---|---|---|
| **IELTS Academic** | International English | Listening, Reading, Writing, Speaking | Band 0-9 (0.5 increments) | 4 |
| **IELTS General** | International English | Listening, Reading, Writing, Speaking | Band 0-9 | 4 |
| **SAT** | US College Admission | Reading+Writing, Math | 400-1600 | 4 |
| **PSAT/NMSQT** | US College Admission (Preliminary) | Reading+Writing, Math | 320-1520 | 4 |
| **ACT** | US College Admission | English, Math, Reading, Science, Writing | 1-36 composite | 4 |
| **AP Exams** | US Advanced Placement | Per-subject (38+ subjects) | 1-5 | 4 |
| **SHSAT** | NYC Specialized High Schools | ELA, Math | Composite (raw score) | 5 |
| **ISEE** | Independent School Entrance | Verbal, Quantitative, Reading, Math, Essay | Stanine 1-9 | 5 |
| **SSAT** | Secondary School Admission | Verbal, Quantitative, Reading, Writing | 1500-2400 (Upper) | 5 |
| **HSPT** | High School Placement | Verbal, Quantitative, Reading, Math, Language | Percentile | 5 |
| **GED** | General Educational Development | Math, Science, Social Studies, Language Arts | 100-200 per section | 5 |
| **TOEFL iBT** | International English | Reading, Listening, Speaking, Writing | 0-120 total | 5 |
| **GRE** | Graduate Admission | Verbal, Quantitative, Analytical Writing | 130-170 per section | 5 |
| **GMAT** | Business Graduate Admission | Quantitative, Verbal, Data Insights, Analytical Writing | 205-805 | 5+ |
| **LSAT** | Law School Admission | Logical Reasoning, Analytical Reasoning, Reading | 120-180 | 5+ |
| **MCAT** | Medical School Admission | Bio/Biochem, Chem/Physics, CARS, Psych/Soc | 472-528 | 5+ |
| **Cambridge (FCE/CAE/CPE)** | International English | Reading, Writing, Listening, Speaking | A-C / Fail | 5 |
| **STEAM Assessments** | STEM + Arts Aptitude | Science, Technology, Engineering, Arts, Math | Varies | 5 |
| **AMC/AIME** | Math Competition | Math problem solving | Score-based ranking | 5+ |
| **Science Olympiad** | Science Competition | 23 events across life/earth/physical science | Event-based scoring | 5+ |
| **STAAR** | Texas State Assessment | Math, Reading, Science, Social Studies, Writing | Approaches/Meets/Masters | 5+ |
| **Regents** | New York State Exams | Per-subject (Math, Science, History, ELA) | 0-100 | 5+ |
| **MAP** | Measures of Academic Progress | Math, Reading, Language, Science (adaptive) | RIT score | 5+ |
| **SBAC** | Smarter Balanced Assessment | ELA, Math | 4 performance levels | 5+ |
| **ASVAB** | Armed Services Vocational | General Science, Arithmetic, Word Knowledge, + 7 more | AFQT percentile | 5+ |
| **CLEP** | College Level Examination | 34 subjects | 20-80 (pass: 50+) | 5+ |
| **CLT** | Classic Learning Test | Verbal Reasoning, Grammar, Quantitative | 0-120 | 5+ |
| **National curriculum exams** | Country-specific | Varies | Varies | 5+ |

### 22.2 IELTS Framework (Detailed)

#### Speaking Assessment
- **AI Examiner**: Simulates all 3 parts of the IELTS speaking test
  - Part 1: Introduction + familiar topics (4-5 min)
  - Part 2: Cue card long turn (1 min prep, 2 min speak)
  - Part 3: Abstract discussion (4-5 min)
- **Evaluation criteria** (locked to official band descriptors):
  - Fluency and Coherence (FC)
  - Lexical Resource (LR)
  - Grammatical Range and Accuracy (GRA)
  - Pronunciation (P)
- **Real-time pronunciation feedback**: Phonetic highlighting, stress patterns, intonation
- **Dynamic follow-ups**: AI responds to actual answers, not scripted
- **Band prediction**: Per-criterion and overall with confidence interval
- **Improvement tips**: "To move from Band 6 to Band 7 in FC, you need to..."

#### Writing Assessment
- **Task 1**: Academic (graph/chart/diagram description) or General (letter writing)
- **Task 2**: Essay (250+ words)
- **Evaluation criteria** (locked to official band descriptors):
  - Task Achievement / Task Response (TA/TR)
  - Coherence and Cohesion (CC)
  - Lexical Resource (LR)
  - Grammatical Range and Accuracy (GRA)
- **Detailed feedback**: Paragraph-level analysis with specific suggestions
- **Band prediction**: Per-criterion and overall
- **Sample band 9 comparisons**: Show how a band 9 response differs from the student's
- **Iterative improvement**: Student revises, tutor re-evaluates, tracks improvement over drafts

#### Reading Practice
- **Passage generation**: AI generates IELTS-style passages with question sets
- **Question types**: Multiple choice, True/False/Not Given, matching headings, sentence completion, summary completion, short answer
- **Timed mode**: 20 minutes per passage (matching real test)
- **Strategy coaching**: Skimming, scanning, keyword identification techniques
- **Difficulty scaling**: Bands 5-6, 6-7, 7-8, 8-9

#### Listening Practice
- **AI-generated audio passages** with IELTS-style scenarios:
  - Section 1: Social conversation
  - Section 2: Monologue (social context)
  - Section 3: Academic discussion
  - Section 4: Academic monologue
- **Question types**: Form completion, multiple choice, map labelling, matching
- **Playback controls**: Speed adjustment, repeat (limited like real test)
- **Accent variety**: British, American, Australian, Canadian, Indian

#### Score Prediction and Tracking
- **Mock test engine**: Full-length timed practice tests
- **Band prediction model**: Trained on official IELTS descriptors
- **Progress tracking**: Band score over time per section
- **Target score gap analysis**: "You need +0.5 in Writing and +1.0 in Speaking to reach your target of 7.0"
- **Study plan generation**: Personalized roadmap to reach target band within timeframe

### 22.3 General Test Prep Architecture

```mermaid
flowchart TB
    subgraph testProfiles [Test Profiles - Pluggable]
        IELTS[IELTS Profile]
        SAT[SAT Profile]
        ACT[ACT Profile]
        AP[AP Profile]
        Custom[Custom Test Profile]
    end

    subgraph testEngine [Test Prep Engine]
        MockTest[Mock Test Generator]
        TimedMode[Timed Test Mode]
        ScoringEngine[Scoring Engine - descriptor-locked]
        GapAnalysis[Gap Analysis]
        StudyPlanGen[Study Plan Generator]
        PredictionModel[Score Prediction Model]
    end

    subgraph existingEngines [Existing Tutor Engines - Reused]
        QuizEngine[Quiz Engine]
        MasteryTracker[Mastery Tracker]
        FlashcardEngine[Flashcard Engine]
        WritingWorkshop[Writing Workshop Mode]
        RAGEngine[RAG Engine]
        InterleaveEngine[Interleaving Engine]
    end

    testProfiles --> testEngine
    testEngine --> existingEngines
    MockTest --> TimedMode
    TimedMode --> ScoringEngine
    ScoringEngine --> GapAnalysis
    GapAnalysis --> StudyPlanGen
    GapAnalysis --> PredictionModel
```

### 22.4 Test Prep Database Tables

```sql
-- Test profiles (pluggable for any test type)
CREATE TABLE test_profiles (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,           -- IELTS Academic, SAT, ACT
    test_type       VARCHAR(50),                     -- english_proficiency, college_admission, ap, graduate
    sections_json   JSONB NOT NULL,                  -- [{name, duration_min, question_count, scoring}]
    scoring_rubric  JSONB NOT NULL,                  -- Band descriptors or scoring rules
    total_duration  INTEGER,                         -- Total test duration in minutes
    score_range     VARCHAR(50),                     -- "0-9", "400-1600", "1-36"
    is_active       BOOLEAN DEFAULT TRUE
);

-- Student test prep enrollment
CREATE TABLE student_test_prep (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    test_profile_id INTEGER NOT NULL REFERENCES test_profiles(id),
    target_score    VARCHAR(50),                     -- "7.0", "1400", "32"
    target_date     DATE,                            -- When they take the real test
    current_predicted_score VARCHAR(50),
    study_plan_json JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Mock test attempts
CREATE TABLE mock_test_attempts (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    test_profile_id INTEGER NOT NULL REFERENCES test_profiles(id),
    section_scores  JSONB,                           -- Per-section scores
    overall_score   VARCHAR(50),
    detailed_feedback JSONB,                         -- Per-criterion feedback
    duration_seconds INTEGER,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ
);

-- IELTS-specific: speaking recordings
CREATE TABLE speaking_attempts (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    test_profile_id INTEGER NOT NULL REFERENCES test_profiles(id),
    part            SMALLINT,                        -- 1, 2, or 3
    audio_path      VARCHAR(1000),                   -- S3 path to recording
    transcript      TEXT,
    scores_json     JSONB,                           -- {fluency, lexical, grammar, pronunciation}
    band_score      REAL,
    feedback        TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- IELTS-specific: writing submissions
CREATE TABLE writing_attempts (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    test_profile_id INTEGER NOT NULL REFERENCES test_profiles(id),
    task_type       VARCHAR(10),                     -- task1, task2
    prompt          TEXT,
    student_text    TEXT,
    word_count      INTEGER,
    scores_json     JSONB,                           -- {task_achievement, coherence, lexical, grammar}
    band_score      REAL,
    feedback        TEXT,
    revision_of     INTEGER REFERENCES writing_attempts(id),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### 22.5 Test Prep API Endpoints

```
POST   /api/test-prep/enroll                    → Enroll in test prep (target score, target date)
GET    /api/test-prep/profiles                  → List available test profiles
GET    /api/test-prep/study-plan                → Get personalized study plan
POST   /api/test-prep/mock-test                 → Start a mock test
POST   /api/test-prep/mock-test/{id}/submit     → Submit mock test answers
GET    /api/test-prep/mock-test/{id}/results    → Get detailed results + band prediction

# IELTS-specific
POST   /api/test-prep/ielts/speaking/start      → Start speaking practice (returns prompts)
POST   /api/test-prep/ielts/speaking/submit     → Submit audio recording for evaluation
POST   /api/test-prep/ielts/writing/submit      → Submit writing for band scoring
GET    /api/test-prep/ielts/writing/{id}/feedback → Get detailed writing feedback
POST   /api/test-prep/ielts/listening/start     → Start listening practice with audio
POST   /api/test-prep/ielts/reading/start       → Start reading passage with questions

# Score tracking
GET    /api/test-prep/progress                  → Score progression over time
GET    /api/test-prep/gap-analysis              → Gap analysis vs target score
```

---

## 24. Interactive Learning Tools

### Digital Whiteboard
- Canvas-based drawing using tldraw (open-source, React-native)
- Math problem-solving workspace, diagram creation
- Tutor can annotate (AI generates SVG annotations)
- Save whiteboard state per session

### Code Sandbox (Built-In)
- Docker-based isolated sandbox (Python, JavaScript, HTML/CSS)
- Monaco Editor with syntax highlighting
- Resource limits: 64MB memory, 0.5 CPU, network disabled
- Tutor guides coding exercises step-by-step
- Auto-grading of code output against expected results

### Math Editor
- MathLive for interactive LaTeX input with live preview
- Students type math naturally, rendered in real-time
- KaTeX for rendering tutor's math responses

### Annotation Tools
- Highlight, underline, add notes to uploaded materials
- Shared annotations between student and tutor session
- Annotations saved and reviewable

---

## 25. Gamification & Motivation

### XP System
| Action | XP |
|---|---|
| Session completion | +10 |
| Quiz correct answer | +5 |
| Flashcard review | +2 |
| Daily login | +5 |
| Mastery level-up | +25 |
| Streak milestone | +10/day |
| "Show Your Thinking" completion | +15 |
| Helping peer (collaborative mode) | +10 |

### Levels (Age-Appropriate Theming)
| Grade Band | Levels |
|---|---|
| K-2 | Seedling → Sprout → Bloom → Blossom → Garden |
| 3-5 | Learner → Explorer → Scholar → Expert → Master |
| 6-8 | Rookie → Challenger → Champion → Legend → GOAT |
| 9-12 | Apprentice → Analyst → Innovator → Visionary → Polymath |

### Streaks
- Daily learning streak counter
- Streak freeze tokens (earned via XP)
- Calendar heatmap visualization

### Badges
- Achievement-based: First Step, On Fire (7-day streak), Deep Thinker, Sharpshooter
- Subject-specific: Master of Math, Science Sage, Word Wizard
- Effort-based: Persistence (tried 5 times before getting it right)

### Leaderboards
- Opt-in only (privacy consideration for K-12)
- Class-level only, no cross-school comparison (FERPA)

### Progress Dashboard
```
┌─────────────────────────────────────────────────────────────────┐
│  Your Learning Progress                                         │
├─────────────────────────────────────────────────────────────────┤
│  🔥 Streak: 7 days    ⭐ XP: 1,240    📚 Level: Explorer        │
├───────────────────┬─────────────────────────────────────────────┤
│  SUBJECTS         │  RECENT ACTIVITY                            │
│                   │                                             │
│  Mathematics      │  ✅ Quadratic Equations  (Sofia)  Yesterday │
│  ████████░░  80%  │  ✅ Python Functions      (Reza)  2 days ago│
│                   │  ⚠️  Calculus Limits      (Sofia)  1 wk ago │
│  Python           │                                             │
│  ████████████ 100%│  KNOWLEDGE GRAPH         [View →]           │
│                   │                                             │
│  History          │  FLASHCARDS DUE           3 due today       │
│  ███░░░░░░░  30%  │  [Start Review →]                           │
│                   │                                             │
│  STANDARDS        │  MISTAKES TO REVIEW       5 patterns        │
│  CCSS.A.REI ████  │  [Review Before Test →]                     │
│  CCSS.F.IF  ██░░  │                                             │
│  NGSS.PS2  █░░░░  │  QUIZ PERFORMANCE                          │
│                   │  Last 10 quizzes: 7/10 avg (70%)            │
└───────────────────┴─────────────────────────────────────────────┘
```

---

## 26. Safety, Compliance & Privacy

### Anti-Cheating by Design
- Tutors are instructed never to write essays, complete assignments, or solve homework verbatim
- In QUIZ mode, AI checks for suspicious patterns (copy-paste detection via length/timing)
- System prompt: *"If a student asks you to write their assignment, gently redirect to teaching the skill instead."*
- Homework Scanner mode: guides through solving, never provides complete solutions
- All interactions logged — teachers can review session replays

### Content Safety
- Inappropriate topic requests return a kind redirect
- Medical, legal, or dangerous content requests rejected
- Input moderation on all messages before sending to LLM
- Output moderation before displaying to student
- Age-calibrated vocabulary enforcement

### Compliance Framework
| Regulation | Implementation |
|---|---|
| **COPPA** | Verifiable parental consent for under-13; data minimization; no behavioral advertising; parent can delete all child data; no PII in analytics |
| **FERPA** | Student records protected; authorized access only; parents can review/amend; no sharing without consent; audit logging |
| **GDPR** | Consent management; right to erasure; data portability; for international users |
| **WCAG 2.1 AA** | Screen reader support; keyboard navigation; high contrast mode; dyslexia font (OpenDyslexic); closed captions; focus indicators |

### Data Security
- AES-256 encryption at rest
- TLS 1.3 in transit
- Encrypted backups
- No PII in logs or error reports
- Audit logging: every access, modification, deletion with actor + timestamp

### Data Retention
- Configurable policies per organization
- Auto-purge inactive accounts
- Export before deletion

### Wellness (Integrated into Product)
- Session time limits by age
- Quiet hours (parent-configurable)
- Break reminders with scientific backing
- Late-night detection and gentle nudge

---

## 27. Database Schema

The tutor has its own PostgreSQL 17 + pgvector database. Users linked via `root_user_id`.

### Core Tables

```sql
-- Users (local profile, linked to root site)
CREATE TABLE tutor_users (
    id              SERIAL PRIMARY KEY,
    root_user_id    INTEGER NOT NULL UNIQUE,
    role            VARCHAR(20) NOT NULL DEFAULT 'student',  -- student, teacher, parent
    display_name    VARCHAR(255),
    grade_level     SMALLINT,                                -- K=0, 1-12
    learning_style  VARCHAR(50),                             -- visual, step-by-step, story, direct, hands-on
    preferred_language VARCHAR(10) DEFAULT 'en',
    interests_json  JSONB,                                   -- ["basketball","gaming","cooking"]
    onboarded_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Tutor Personas (base + teacher custom)
CREATE TABLE tutor_personas (
    id              SERIAL PRIMARY KEY,
    slug            VARCHAR(100) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    tagline         VARCHAR(255),
    avatar_url      VARCHAR(500),
    personality     TEXT NOT NULL,
    system_prompt   TEXT NOT NULL,
    teaching_style  VARCHAR(50) NOT NULL,                    -- socratic, step-by-step, direct, peer
    subject_expertise JSONB,                                 -- ["math","science","coding"]
    is_custom       BOOLEAN DEFAULT FALSE,
    created_by_teacher_id INTEGER REFERENCES tutor_users(id),
    is_active       BOOLEAN DEFAULT TRUE,
    sort_order      INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Tutoring Sessions
CREATE TABLE tutor_sessions (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES tutor_users(id),
    persona_id      INTEGER NOT NULL REFERENCES tutor_personas(id),
    subject         VARCHAR(255),
    topic           VARCHAR(255),
    subtopic        VARCHAR(255),
    grade_level     SMALLINT,
    mode            VARCHAR(20) DEFAULT 'teach',             -- teach, quiz, hint, apply, thinking, writing
    status          VARCHAR(20) DEFAULT 'active',            -- active, ended, abandoned
    summary         TEXT,
    tokens_used     INTEGER DEFAULT 0,
    model_used      VARCHAR(100),
    emotional_state_log JSONB,
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    ended_at        TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Messages
CREATE TABLE tutor_messages (
    id              SERIAL PRIMARY KEY,
    session_id      INTEGER NOT NULL REFERENCES tutor_sessions(id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL,                    -- user, assistant, system
    content         TEXT NOT NULL,
    mode            VARCHAR(20) DEFAULT 'chat',              -- teach, quiz, hint, apply, thinking, writing, chat
    hint_level      SMALLINT,                                -- 1, 2, or 3
    tokens_used     INTEGER DEFAULT 0,
    model_used      VARCHAR(100),
    feedback        VARCHAR(10),                             -- up, down
    reasoning_quality_score SMALLINT,                        -- 0-100 for Show Your Thinking
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_messages_session ON tutor_messages(session_id);
```

### RAG / Knowledge Base Tables

```sql
-- Knowledge Bases (teacher-owned)
CREATE TABLE knowledge_bases (
    id              SERIAL PRIMARY KEY,
    owner_id        INTEGER NOT NULL REFERENCES tutor_users(id),
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    subject         VARCHAR(255),
    grade_level     SMALLINT,
    visibility      VARCHAR(20) DEFAULT 'private',           -- private, school, marketplace
    status          VARCHAR(20) DEFAULT 'active',
    standards_json  JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Uploaded Documents
CREATE TABLE kb_documents (
    id              SERIAL PRIMARY KEY,
    kb_id           INTEGER NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    filename        VARCHAR(500) NOT NULL,
    file_path       VARCHAR(1000) NOT NULL,                  -- S3/blob path
    file_type       VARCHAR(50),                             -- pdf, docx, pptx, txt, image
    file_size       BIGINT,
    status          VARCHAR(20) DEFAULT 'queued',            -- queued, processing, ready, failed
    page_count      INTEGER,
    extracted_text_preview TEXT,
    error_message   TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Document Chunks with Embeddings
CREATE TABLE kb_chunks (
    id              SERIAL PRIMARY KEY,
    document_id     INTEGER NOT NULL REFERENCES kb_documents(id) ON DELETE CASCADE,
    kb_id           INTEGER NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    chunk_index     INTEGER NOT NULL,
    content         TEXT NOT NULL,
    embedding       vector(1536),                            -- pgvector
    metadata_json   JSONB,                                   -- section, page, headers
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_chunks_embedding ON kb_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_chunks_kb ON kb_chunks(kb_id);

-- KB-to-Class Assignment
CREATE TABLE kb_class_assignments (
    id              SERIAL PRIMARY KEY,
    kb_id           INTEGER NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    class_id        INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    assigned_at     TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(kb_id, class_id)
);
```

### Class Tables

```sql
CREATE TABLE classes (
    id              SERIAL PRIMARY KEY,
    teacher_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    name            VARCHAR(255) NOT NULL,
    subject         VARCHAR(255),
    grade_level     SMALLINT,
    invite_code     VARCHAR(20) UNIQUE,
    persona_id      INTEGER REFERENCES tutor_personas(id),
    settings_json   JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE class_enrollments (
    id              SERIAL PRIMARY KEY,
    class_id        INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    enrolled_at     TIMESTAMPTZ DEFAULT NOW(),
    status          VARCHAR(20) DEFAULT 'active',
    UNIQUE(class_id, student_id)
);

CREATE TABLE parent_student_links (
    id              SERIAL PRIMARY KEY,
    parent_id       INTEGER NOT NULL REFERENCES tutor_users(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    consent_status  VARCHAR(20) DEFAULT 'pending',           -- pending, granted, revoked
    consent_date    TIMESTAMPTZ,
    restrictions_json JSONB,                                 -- subjects, time limits, quiet hours
    UNIQUE(parent_id, student_id)
);
```

### Learning Intelligence Tables

```sql
CREATE TABLE student_mastery (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    subject         VARCHAR(255) NOT NULL,
    topic           VARCHAR(255) NOT NULL,
    standard_code   VARCHAR(50),
    mastery_level   SMALLINT DEFAULT 0,                      -- 0-4
    reasoning_quality SMALLINT,                              -- 0-100
    last_assessed_at TIMESTAMPTZ,
    UNIQUE(student_id, subject, topic)
);

CREATE TABLE misconception_log (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    subject         VARCHAR(255),
    topic           VARCHAR(255),
    misconception_type VARCHAR(255),
    description     TEXT,
    detected_at     TIMESTAMPTZ DEFAULT NOW(),
    resolved_at     TIMESTAMPTZ
);

CREATE TABLE mistake_journal (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    session_id      INTEGER REFERENCES tutor_sessions(id),
    question        TEXT NOT NULL,
    student_answer  TEXT,
    correct_answer  TEXT,
    misconception_id INTEGER REFERENCES misconception_log(id),
    explanation_that_worked TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE concept_nodes (
    id              SERIAL PRIMARY KEY,
    subject         VARCHAR(255) NOT NULL,
    topic           VARCHAR(255) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    grade_level     SMALLINT,
    prerequisites_json JSONB,
    standard_codes_json JSONB
);

CREATE TABLE concept_edges (
    id              SERIAL PRIMARY KEY,
    from_node_id    INTEGER NOT NULL REFERENCES concept_nodes(id),
    to_node_id      INTEGER NOT NULL REFERENCES concept_nodes(id),
    relationship_type VARCHAR(50),                           -- prerequisite, related, builds_on
    weight          REAL DEFAULT 1.0
);

CREATE TABLE career_topic_mappings (
    id              SERIAL PRIMARY KEY,
    career          VARCHAR(255) NOT NULL,
    interest_tags   JSONB,
    topic_id        INTEGER REFERENCES concept_nodes(id),
    explanation     TEXT
);
```

### Assessment Tables

```sql
CREATE TABLE assessments (
    id              SERIAL PRIMARY KEY,
    teacher_id      INTEGER REFERENCES tutor_users(id),
    title           VARCHAR(255) NOT NULL,
    type            VARCHAR(50),                             -- diagnostic, formative, summative, quiz
    subject         VARCHAR(255),
    grade_level     SMALLINT,
    standards_json  JSONB,
    time_limit_minutes INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE assessment_questions (
    id              SERIAL PRIMARY KEY,
    assessment_id   INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_type   VARCHAR(50),                             -- mcq, free_response, fill_blank, matching
    content         TEXT NOT NULL,
    options_json    JSONB,
    correct_answer  TEXT,
    explanation     TEXT,
    misconceptions_tested_json JSONB,
    sort_order      INTEGER DEFAULT 0
);

CREATE TABLE assessment_attempts (
    id              SERIAL PRIMARY KEY,
    assessment_id   INTEGER NOT NULL REFERENCES assessments(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    score           REAL,
    answers_json    JSONB,
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);
```

### Gamification Tables

```sql
CREATE TABLE student_xp (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id) UNIQUE,
    total_xp        INTEGER DEFAULT 0,
    level           VARCHAR(50) DEFAULT 'Learner',
    current_streak  INTEGER DEFAULT 0,
    longest_streak  INTEGER DEFAULT 0,
    last_activity_date DATE,
    streak_freezes  INTEGER DEFAULT 0
);

CREATE TABLE xp_transactions (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    amount          INTEGER NOT NULL,
    source_type     VARCHAR(50),                             -- session, quiz, flashcard, login, streak, mastery
    source_id       INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE badges (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    icon            VARCHAR(500),
    criteria_json   JSONB,
    category        VARCHAR(50)                              -- achievement, subject, effort
);

CREATE TABLE student_badges (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    badge_id        INTEGER NOT NULL REFERENCES badges(id),
    earned_at       TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_id, badge_id)
);
```

### Flashcard Tables

```sql
CREATE TABLE flashcard_decks (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    title           VARCHAR(255),
    subject         VARCHAR(255),
    topic           VARCHAR(255),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE flashcards (
    id              SERIAL PRIMARY KEY,
    deck_id         INTEGER NOT NULL REFERENCES flashcard_decks(id) ON DELETE CASCADE,
    front           TEXT NOT NULL,
    back            TEXT NOT NULL,
    source_session_id INTEGER REFERENCES tutor_sessions(id),
    next_review_at  TIMESTAMPTZ,
    ease_factor     REAL DEFAULT 2.5,                        -- SM-2 algorithm
    interval        INTEGER DEFAULT 1,                       -- days
    review_count    INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

### Standards Tables

```sql
CREATE TABLE standards_frameworks (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,                   -- Common Core, NGSS, etc.
    version         VARCHAR(50),
    country         VARCHAR(10) DEFAULT 'US',
    grades_range    VARCHAR(20)                              -- K-12, 9-12, etc.
);

CREATE TABLE standards (
    id              SERIAL PRIMARY KEY,
    framework_id    INTEGER NOT NULL REFERENCES standards_frameworks(id),
    parent_id       INTEGER REFERENCES standards(id),
    code            VARCHAR(100) NOT NULL,                   -- CCSS.MATH.CONTENT.8.EE.A.1
    description     TEXT NOT NULL,
    grade_level     SMALLINT,
    subject         VARCHAR(255)
);

CREATE TABLE content_standard_mappings (
    id              SERIAL PRIMARY KEY,
    content_type    VARCHAR(50),                             -- topic, question, kb_document, learning_path
    content_id      INTEGER NOT NULL,
    standard_id     INTEGER NOT NULL REFERENCES standards(id)
);
```

### Portfolio, Analytics, Notifications, Restrictions

```sql
CREATE TABLE portfolio_items (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    item_type       VARCHAR(50),                             -- session_highlight, achievement, reflection, work_sample
    title           VARCHAR(255),
    content_json    JSONB,
    standards_json  JSONB,
    is_highlighted  BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE self_reflections (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    session_id      INTEGER REFERENCES tutor_sessions(id),
    prompt          TEXT,
    response        TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE session_analytics (
    id              SERIAL PRIMARY KEY,
    session_id      INTEGER NOT NULL REFERENCES tutor_sessions(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    duration_seconds INTEGER,
    messages_count  INTEGER,
    hints_used      SMALLINT,
    mode_switches   SMALLINT,
    mastery_before  SMALLINT,
    mastery_after   SMALLINT,
    emotional_states_json JSONB
);

CREATE TABLE daily_analytics (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    date            DATE NOT NULL,
    sessions_count  INTEGER DEFAULT 0,
    total_duration  INTEGER DEFAULT 0,
    xp_earned       INTEGER DEFAULT 0,
    subjects_json   JSONB,
    interleaved_reviews INTEGER DEFAULT 0,
    UNIQUE(student_id, date)
);

CREATE TABLE notifications (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES tutor_users(id),
    type            VARCHAR(50),
    title           VARCHAR(255),
    body            TEXT,
    data_json       JSONB,
    read_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE content_restrictions (
    id              SERIAL PRIMARY KEY,
    parent_id       INTEGER NOT NULL REFERENCES tutor_users(id),
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    restriction_type VARCHAR(50),                            -- subject, topic, mode, time_limit
    restriction_value JSONB,
    quiet_hours_json JSONB                                   -- {"start": "21:00", "end": "07:00"}
);

-- Learning paths
CREATE TABLE learning_paths (
    id              SERIAL PRIMARY KEY,
    teacher_id      INTEGER REFERENCES tutor_users(id),
    title           VARCHAR(255) NOT NULL,
    subject         VARCHAR(255),
    grade_level     SMALLINT,
    standards_json  JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE learning_path_items (
    id              SERIAL PRIMARY KEY,
    path_id         INTEGER NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,
    item_type       VARCHAR(50),                             -- topic, assessment, resource
    item_id         INTEGER,
    sort_order      INTEGER DEFAULT 0,
    prerequisite_item_id INTEGER REFERENCES learning_path_items(id)
);

-- Student interests (separate from JSON for query performance)
CREATE TABLE student_interests (
    id              SERIAL PRIMARY KEY,
    student_id      INTEGER NOT NULL REFERENCES tutor_users(id),
    interest        VARCHAR(255) NOT NULL,
    used_for_analogies BOOLEAN DEFAULT TRUE
);
```

---

## 28. API Endpoints

### Auth (via root site)
```
GET    /api/auth/login              → Redirect to root site OAuth
POST   /api/auth/callback           → Exchange code for JWT
POST   /api/auth/refresh            → Refresh token
GET    /api/auth/me                 → Current user + tutor profile
```

### Onboarding
```
POST   /api/onboard                 → Set role, grade, interests, learning style
GET    /api/onboard/assessment/{subject} → Diagnostic placement test
```

### Tutors
```
GET    /api/tutors                  → List all personas (base + custom)
GET    /api/tutors/{slug}           → Persona detail
POST   /api/tutors/custom           → Create custom persona (teacher only)
GET    /api/subjects                → Subject/topic/grade tree + knowledge graph
GET    /api/subjects/{subject}/standards → Standards for subject
```

### Sessions
```
POST   /api/sessions                → Create tutoring session
  body: { persona_id, subject, topic, grade_level }

GET    /api/sessions                → List sessions (filters, pagination)
GET    /api/sessions/{id}           → Session detail + messages

POST   /api/sessions/{id}/chat      → Send message, stream response (SSE)
  body: { message, mode }
  response: Server-Sent Events stream

POST   /api/sessions/{id}/end       → End session, generate summary
POST   /api/sessions/{id}/hint      → Request next hint level
POST   /api/sessions/{id}/mode      → Switch interaction mode
POST   /api/messages/{id}/feedback   → Rate message (up/down)
```

### Knowledge Bases (Teacher)
```
POST   /api/kb                      → Create knowledge base
GET    /api/kb                      → List my knowledge bases
POST   /api/kb/{id}/upload          → Upload document(s)
GET    /api/kb/{id}/documents       → List documents + processing status
DELETE /api/kb/{id}/documents/{doc_id} → Remove document
POST   /api/kb/{id}/assign          → Assign to class(es)
POST   /api/kb/{id}/preview         → Test chat with KB context
POST   /api/kb/{id}/publish         → Publish to marketplace
```

### Classes (Teacher)
```
POST   /api/classes                 → Create class
GET    /api/classes                 → List my classes
GET    /api/classes/{id}/students   → Student roster + progress
POST   /api/classes/{id}/invite     → Generate invite code
POST   /api/classes/join            → Student joins via invite code
```

### Assessments
```
POST   /api/assessments             → Create assessment
POST   /api/assessments/{id}/generate → AI-generate questions from KB
POST   /api/assessments/{id}/attempt → Start attempt
POST   /api/assessments/{id}/submit  → Submit answers
```

### Progress & Mastery
```
GET    /api/progress                → Overall progress
GET    /api/progress/{subject}      → Per-subject mastery detail
GET    /api/progress/standards      → Per-standard mastery
GET    /api/progress/mistakes       → Mistake journal
GET    /api/progress/report         → Generate PDF report
GET    /api/progress/knowledge-graph/{subject} → Knowledge graph + mastery overlay
```

### Flashcards
```
POST   /api/flashcards              → Save flashcard from session
GET    /api/flashcards/due          → Cards due for review (spaced repetition)
POST   /api/flashcards/{id}/review  → Submit review result
GET    /api/flashcards/decks        → List decks
```

### Gamification
```
GET    /api/gamification/profile    → XP, level, streak, badges
GET    /api/gamification/leaderboard/{class_id} → Class leaderboard
```

### Parent
```
GET    /api/parent/children         → Linked children
POST   /api/parent/link             → Link to child (triggers consent flow)
GET    /api/parent/children/{id}/progress → Child's progress
GET    /api/parent/children/{id}/activity → Activity feed
POST   /api/parent/children/{id}/restrictions → Set content controls
GET    /api/parent/children/{id}/report → Download PDF report
POST   /api/parent/children/{id}/co-learn → Join co-learning session
```

### Teacher Analytics
```
GET    /api/teacher/analytics/class/{id} → Class-level analytics
GET    /api/teacher/analytics/students/{id} → Per-student deep dive
GET    /api/teacher/analytics/struggling → At-risk students
GET    /api/teacher/analytics/misconceptions/{class_id} → Class misconception report
GET    /api/teacher/copilot/suggest  → AI teaching suggestions
POST   /api/teacher/copilot/worksheet → Generate differentiated worksheet
```

### Portfolio
```
GET    /api/portfolio               → Student portfolio
POST   /api/portfolio/highlight     → Highlight an item
POST   /api/portfolio/reflect       → Add self-reflection
GET    /api/portfolio/export        → Export as PDF
```

### Micro-Tutoring
```
POST   /api/micro/quick-quiz        → 5-minute targeted quiz
POST   /api/micro/daily-review      → Spaced repetition review
POST   /api/micro/concept-refresh/{topic} → 2-minute concept refresh
```

### Homework Scanner
```
POST   /api/homework/scan           → Upload image, OCR, identify concept
POST   /api/homework/guide/{scan_id} → Start guided solving session
```

### AI Study Tools
```
POST   /api/study-tools/audio-lesson         → Generate audio lesson from topic or KB
GET    /api/study-tools/audio-lesson/{id}     → Get audio lesson (status, URL, transcript)
POST   /api/study-tools/study-guide           → Generate study guide from topic, KB, or URL
POST   /api/study-tools/mind-map              → Generate mind map from topic
POST   /api/study-tools/quick-summary         → Summarize document, URL, or video
POST   /api/study-tools/magic-notes           → Upload notes → generate flashcards + quiz + study guide
POST   /api/study-tools/brain-beats/{deck_id} → Convert flashcard deck to song
GET    /api/study-tools/memory-score          → Get memory predictions per topic/card
POST   /api/study-tools/url-ingest            → Ingest URL or YouTube video for learning
POST   /api/study-tools/lecture-ingest        → Upload audio recording for transcription + study materials
POST   /api/study-tools/roleplay/start        → Start roleplay scenario
POST   /api/study-tools/explain-my-answer     → Get detailed explanation of quiz answer
```

### Educational Games (see Section 22 for full detail)
```
GET    /api/games/templates                     → List available games (filtered by age, subject, style)
GET    /api/games/templates/{id}                → Get game configuration
POST   /api/games/sessions                      → Start a game session
POST   /api/games/sessions/{id}/answer          → Submit an answer within a game
POST   /api/games/sessions/{id}/complete        → Complete game (triggers mastery update)
GET    /api/games/sessions/{id}/results         → Get results + mastery impact
GET    /api/games/history                       → Student's game history
GET    /api/games/leaderboard/{class_id}        → Class leaderboard
POST   /api/games/assignments                   → Teacher assigns game to class
GET    /api/games/recommendations               → AI-recommended games for student
```

### Test Prep (see Section 23 for full detail)
```
POST   /api/test-prep/enroll                    → Enroll in test prep
GET    /api/test-prep/profiles                  → List test profiles
GET    /api/test-prep/study-plan                → Get personalized study plan
POST   /api/test-prep/mock-test                 → Start mock test
POST   /api/test-prep/mock-test/{id}/submit     → Submit mock test
GET    /api/test-prep/mock-test/{id}/results    → Get results + score prediction
POST   /api/test-prep/ielts/speaking/start      → Start IELTS speaking practice
POST   /api/test-prep/ielts/speaking/submit     → Submit audio for evaluation
POST   /api/test-prep/ielts/writing/submit      → Submit writing for band scoring
GET    /api/test-prep/ielts/writing/{id}/feedback → Get writing feedback
POST   /api/test-prep/ielts/listening/start     → Start listening practice
POST   /api/test-prep/ielts/reading/start       → Start reading practice
GET    /api/test-prep/progress                  → Score progression over time
GET    /api/test-prep/gap-analysis              → Gap analysis vs target
```

---

## 29. Backend Architecture

### Project Structure
```
app/
├── api/                            # Route handlers
│   ├── auth.py                     # OAuth + JWT
│   ├── sessions.py                 # Session CRUD + streaming chat
│   ├── tutors.py                   # Persona listing + custom creation
│   ├── knowledge_bases.py          # KB CRUD + upload + preview
│   ├── classes.py                  # Class management
│   ├── assessments.py              # Assessment CRUD + AI generation
│   ├── progress.py                 # Mastery + progress + reports
│   ├── flashcards.py               # Flashcard CRUD + spaced repetition
│   ├── gamification.py             # XP + badges + leaderboard
│   ├── parent.py                   # Parent dashboard + controls
│   ├── teacher_analytics.py        # Teacher analytics + co-pilot
│   ├── portfolio.py                # Digital portfolio
│   ├── micro.py                    # Micro-tutoring endpoints
│   ├── homework.py                 # Homework scanner
│   ├── study_tools.py              # Audio lessons, study guides, mind maps, magic notes, URL ingest
│   ├── test_prep.py                # Test prep enrollment, mock tests, scoring
│   ├── test_prep_ielts.py          # IELTS-specific: speaking, writing, listening, reading
│   ├── games.py                    # Game templates, sessions, assignments, leaderboards
│   └── health.py                   # Health check
├── services/                       # Business logic
│   ├── root_site_client.py         # Root site API integration
│   ├── ai_providers.py             # LLM provider abstraction (OpenAI, Anthropic, Gemini, Grok)
│   ├── prompt_builder.py           # 8-layer prompt assembly
│   ├── model_router.py             # Intelligent model routing
│   ├── stream_service.py           # SSE streaming manager
│   ├── safety_service.py           # Input/output moderation, age filter, anti-cheat
│   ├── rag_service.py              # RAG retrieval + context building
│   ├── embedding_service.py        # Embedding generation
│   ├── document_extractor.py       # PDF/DOCX/PPTX/TXT extraction
│   ├── chunking_service.py         # Semantic document chunking
│   ├── session_service.py          # Session management + context
│   ├── hint_service.py             # 3-level hint progression
│   ├── quiz_service.py             # Quiz generation + grading
│   ├── mastery_service.py          # Mastery level tracking + updates
│   ├── misconception_service.py    # Misconception detection + logging
│   ├── interleaving_service.py     # Topic interleaving engine
│   ├── emotion_service.py          # Emotional intelligence detection
│   ├── standards_service.py        # Standards alignment + tagging
│   ├── gamification_service.py     # XP + streaks + badges
│   ├── flashcard_service.py        # SM-2 spaced repetition scheduling
│   ├── report_service.py           # PDF report generation
│   ├── notification_service.py     # In-app + email notifications
│   ├── portfolio_service.py        # Portfolio compilation
│   ├── wellness_service.py         # Session limits + break reminders
│   ├── catalog_service.py          # Model catalog sync from root site
│   ├── token_service.py            # Credit estimation + reservation + reconciliation
│   ├── file_storage_service.py     # S3/Azure Blob file operations
│   ├── sandbox_service.py          # Docker code execution sandbox
│   ├── audio_lesson_service.py     # AI script generation + TTS rendering
│   ├── study_guide_service.py      # Study guide + quick summary generation
│   ├── mind_map_service.py         # Mind map generation from topics
│   ├── url_ingest_service.py       # URL scraping, YouTube transcript extraction
│   ├── lecture_ingest_service.py   # Audio transcription (Whisper) + study material generation
│   ├── brain_beats_service.py      # Flashcard-to-song conversion via AI + TTS
│   ├── memory_score_service.py     # Retention prediction + review scheduling
│   ├── roleplay_service.py         # Subject-appropriate roleplay scenario management
│   ├── test_prep_service.py        # Mock test engine, scoring, gap analysis, study plan
│   ├── ielts_service.py            # IELTS-specific: band scoring, speaking eval, writing eval
│   ├── game_engine_service.py      # Game session management, adaptive difficulty, template rendering
│   ├── game_recommendation.py      # AI game recommendation based on learning gaps + style
│   └── learning_pathway_service.py # Multi-pathway routing: chat vs quiz vs game vs audio
├── tasks/                          # Celery async tasks
│   ├── document_processing.py      # Document ingestion pipeline
│   ├── embedding_generation.py     # Batch embedding generation
│   ├── audio_generation.py         # Audio lesson TTS rendering (async, heavy)
│   ├── url_ingestion.py            # URL/YouTube transcript extraction (async)
│   ├── lecture_transcription.py    # Whisper transcription of uploaded audio (async)
│   ├── analytics_aggregation.py    # Daily analytics rollup
│   ├── report_generation.py        # PDF report generation
│   ├── notification_dispatch.py    # Email/push notifications
│   └── streak_management.py        # Daily streak reset/freeze
├── config.py                       # App configuration
├── database.py                     # asyncpg connection pool
├── middleware.py                    # Auth, rate limiting, logging
└── main.py                         # FastAPI app entry point
```

### SSE Streaming (Pseudocode)
```python
@router.post("/sessions/{session_id}/chat")
async def chat(session_id: int, request: ChatRequest):
    return StreamingResponse(
        stream_chat(session_id, request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

async def stream_chat(session_id, request):
    # 1. Safety check (input moderation + age filter)
    # 2. Estimate token cost
    # 3. Reserve credits via root site API
    # 4. RAG retrieval (scoped to student's classes)
    # 5. Build 8-layer prompt
    # 6. Route to optimal model
    # 7. Stream tokens via SSE
    # 8. Reconcile actual credits
    # 9. Save message + update mastery + log analytics
    yield f"data: {json.dumps({'type': 'stream_start'})}\n\n"
    async for chunk in provider.stream_chat(messages):
        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
    yield f"data: {json.dumps({'type': 'complete', 'xp_earned': xp})}\n\n"
```

---

## 30. Frontend Architecture

### Project Structure
```
frontend/src/
├── app/                            # Next.js App Router
│   ├── (auth)/                     # Auth pages (login, callback)
│   ├── (student)/                  # Student pages
│   │   ├── tutors/                 # Tutor selection
│   │   ├── subjects/               # Subject browser
│   │   ├── chat/[sessionId]/       # Chat session
│   │   ├── progress/               # Progress dashboard
│   │   ├── flashcards/             # Flashcard review
│   │   ├── portfolio/              # Digital portfolio
│   │   └── knowledge-graph/        # Interactive concept map
│   ├── (teacher)/                  # Teacher pages
│   │   ├── dashboard/              # Teacher overview
│   │   ├── classes/                # Class management
│   │   ├── knowledge-bases/        # KB management + upload
│   │   ├── assessments/            # Assessment creator
│   │   ├── analytics/              # Student analytics
│   │   └── copilot/                # AI co-pilot
│   ├── (parent)/                   # Parent pages
│   │   ├── dashboard/              # Parent overview
│   │   ├── children/[id]/          # Child detail + controls
│   │   └── reports/                # Progress reports
│   └── onboarding/                 # First-time setup
├── components/
│   ├── chat/                       # Chat components
│   │   ├── ChatMessage.tsx
│   │   ├── ModeBar.tsx
│   │   ├── StreamingIndicator.tsx
│   │   ├── QuickActionChips.tsx
│   │   ├── SessionPanel.tsx
│   │   └── ConversationStarters.tsx
│   ├── tutor/                      # Tutor selection
│   │   ├── TutorCard.tsx
│   │   └── TutorGrid.tsx
│   ├── math/                       # Math rendering
│   │   ├── KaTeXRenderer.tsx
│   │   └── MathLiveEditor.tsx
│   ├── whiteboard/                 # tldraw integration
│   │   └── Whiteboard.tsx
│   ├── code/                       # Code sandbox
│   │   ├── CodeEditor.tsx          # Monaco Editor
│   │   └── CodeOutput.tsx
│   ├── knowledge-graph/            # Concept visualization
│   │   └── KnowledgeGraph.tsx
│   ├── progress/                   # Progress visualizations
│   │   ├── MasteryHeatmap.tsx
│   │   ├── RadarChart.tsx
│   │   └── StreakCalendar.tsx
│   └── ui/                         # shadcn/ui components
├── stores/                         # Zustand state management
│   ├── useAuthStore.ts
│   ├── useChatStore.ts
│   ├── useSessionStore.ts
│   └── useGamificationStore.ts
├── hooks/
│   ├── useSSEStream.ts             # SSE streaming hook
│   ├── useCredits.ts               # Credit balance
│   └── useGradeTheme.ts            # Age-adaptive theming
└── lib/
    ├── api.ts                      # API client
    ├── sse.ts                      # SSE utilities
    └── utils.ts                    # Helpers
```

### Key Frontend Libraries
```json
{
  "next": "^15.x",
  "react": "^19.x",
  "typescript": "^5.x",
  "tailwindcss": "^4.x",
  "@shadcn/ui": "latest",
  "zustand": "^5.x",
  "katex": "^0.16.x",
  "mathlive": "^0.100.x",
  "@tldraw/tldraw": "latest",
  "@monaco-editor/react": "latest",
  "react-markdown": "latest",
  "rehype-highlight": "latest",
  "reactflow": "latest",
  "next-intl": "latest",
  "recharts": "latest"
}
```

---

## 31. AI Prompt Engineering

### Base System Prompt Template (8 Layers)
```
[LAYER 1 — BASE PERSONA]
You are {tutor_name}, an AI tutor.
PERSONALITY: {personality_description}
TEACHING STYLE: {teaching_style_description}

[LAYER 2 — CUSTOM OVERLAY (if teacher-customized)]
ADDITIONAL INSTRUCTIONS FROM TEACHER: {custom_instructions}

[LAYER 3 — MODE RULES]
CURRENT MODE: {current_mode}
{mode_specific_rules}

[LAYER 4 — RAG CONTEXT (if available)]
REFERENCE MATERIALS:
The following excerpts are from the student's teacher-provided materials.
Use them to inform your response. Cite sources as [1], [2], etc.
{rag_chunks_with_citations}

[LAYER 5 — STUDENT CONTEXT]
STUDENT PROFILE:
- Grade level: {grade_level}
- Mastery on this topic: {mastery_level}/4
- Known misconceptions: {misconception_history}
- Learning style: {learning_style}
- Previous struggles: {past_struggles_summary}

[LAYER 6 — INTEREST PERSONALIZATION]
STUDENT INTERESTS: {interests_list}
Use these interests to create relevant analogies and examples where natural.

[LAYER 7 — STANDARDS CONTEXT]
This topic maps to standard: {standard_code} — {standard_description}
Ensure explanations align with grade-level expectations for this standard.

[LAYER 8 — SESSION HISTORY]
{first_2_messages}
{rolling_summary_if_long_session}
{last_15_messages}
```

### Per-Persona Prompt Additions

**Sofia (Patient & Warm):**
```
Speak with warmth and encouragement. Start responses by acknowledging effort.
Use: "Great question!", "Let's work through this together", "You're doing well."
Never make the student feel bad for not knowing something.
Break everything into the smallest possible steps.
```

**Marcus (Socratic):**
```
NEVER give direct answers unless the student has been stuck for more than 3 hints.
Every explanation is followed by a probing question back to the student.
Challenge incorrect assumptions politely: "Interesting — but what happens if...?"
Your goal is to make the student discover the answer themselves.
```

**Aiko (Creative & Fun):**
```
Use stories, metaphors, and humor wherever appropriate.
Reference pop culture, games, or the student's interests frequently.
Make learning feel like an adventure. Use energy and excitement.
Invent memorable mnemonics and nicknames for concepts.
```

**Reza (Direct & Rigorous):**
```
Be efficient. Minimal pleasantries. Get straight to the content.
Give worked examples. Expect precise answers.
Correct mistakes immediately and explain exactly why they're wrong.
Assume the student can handle challenge. Don't over-simplify.
```

### Mode-Specific Prompt Injections

**Quiz Mode:**
```
QUIZ MODE ACTIVE. Generate exactly ONE question appropriate for mastery level {level}.
Ask the question clearly. Do NOT provide hints or answers yet.
After the student responds, give detailed feedback: correct/incorrect + why + right approach.
```

**Hint Mode:**
```
HINT MODE ACTIVE. Hint level requested: {hint_level}/3.
DO NOT solve the problem. DO NOT give the answer.
Provide ONLY a Level {hint_level} hint:
  Level 1: A gentle nudge in the right direction (1 sentence)
  Level 2: Point to the relevant concept or rule (2 sentences)
  Level 3: Describe the approach step by step WITHOUT solving it
```

**Show Your Thinking Mode:**
```
METACOGNITION MODE ACTIVE. The student will explain their reasoning step by step.
Evaluate the PROCESS of their thinking, not just the final answer.
Identify exactly where reasoning breaks down.
Provide feedback on logical structure, assumptions, and justification quality.
```

**Writing Workshop Mode:**
```
WRITING WORKSHOP MODE. The student has submitted a draft for feedback.
NEVER rewrite or write for the student.
Provide specific, actionable feedback using the rubric:
  - Thesis clarity
  - Evidence and support
  - Organization and flow
  - Voice and style
  - Grammar and mechanics
Ask guiding questions: "What evidence supports this claim?"
```

### Behavioral Rules (All Modes)
```
UNIVERSAL RULES:
1. Use the student's interests for analogies where natural.
2. Never write essays, complete assignments, or do homework for the student.
3. If a student seems frustrated, acknowledge it and adjust approach.
4. Keep responses appropriately concise. Break long explanations into steps.
5. Use LaTeX notation for math (wrapped in $ or $$).
6. Use markdown formatting for structure.
7. Cite RAG sources as [1], [2] when using teacher-uploaded materials.
8. Adjust vocabulary complexity to grade level {grade_level}.
9. If the topic is outside your expertise, say so honestly.
10. End responses with a natural next step (question, suggestion, encouragement).
```

---

## 32. Deployment Architecture

```mermaid
graph TB
    subgraph dockerCompose [Docker Compose - tutor.clevercreator.ai]
        subgraph frontendContainer [Frontend]
            NextJS[Next.js - SSR + Static]
        end
        subgraph backendContainers [Backend]
            FastAPI[FastAPI - uvicorn - main API]
            CeleryW1[Celery Worker - documents + embeddings]
            CeleryW2[Celery Worker - analytics + reports]
            CeleryBeat[Celery Beat - scheduled tasks]
        end
        subgraph sandboxContainers [Code Execution]
            SandboxPool[Docker-in-Docker Sandbox Pool]
        end
        subgraph dataContainers [Data Stores]
            PG[(PostgreSQL 17 + pgvector)]
            Redis[(Redis)]
        end
        subgraph proxyContainer [Proxy]
            Nginx[Nginx Reverse Proxy]
        end
    end

    subgraph externalStorage [External Storage]
        S3[(S3 / Azure Blob)]
    end

    subgraph externalAPIs [External APIs]
        RootSiteAPI[Root Site API - clevercreator.ai]
        LLMAPIs[LLM Provider APIs]
    end

    Nginx --> NextJS
    Nginx --> FastAPI
    FastAPI --> PG
    FastAPI --> Redis
    FastAPI --> S3
    FastAPI --> RootSiteAPI
    FastAPI --> LLMAPIs
    FastAPI --> SandboxPool
    CeleryW1 --> PG
    CeleryW1 --> S3
    CeleryW1 --> LLMAPIs
    CeleryW2 --> PG
    CeleryBeat --> Redis
```

### Docker Compose Services:
| Service | Purpose | Port |
|---|---|---|
| `tutor-frontend` | Next.js SSR app | 3000 |
| `tutor-backend` | FastAPI + uvicorn | 8000 |
| `tutor-celery-worker-docs` | Document processing + embedding generation | — |
| `tutor-celery-worker-analytics` | Analytics aggregation + report generation | — |
| `tutor-celery-beat` | Scheduled tasks (daily analytics, streak resets, spaced repetition) | — |
| `tutor-postgres` | PostgreSQL 17 + pgvector | 5432 |
| `tutor-redis` | Redis (cache, sessions, Celery broker) | 6379 |
| `tutor-nginx` | Reverse proxy + SSL termination | 80/443 |
| `tutor-sandbox` | Docker-in-Docker for code execution (isolated network) | — |

### Environment Variables:
```env
# Root Site Integration
ROOT_SITE_URL=http://dev_ai:8000
ROOT_SITE_PUBLIC_URL=https://clevercreator.ai
OAUTH_CLIENT_ID=tutor-app
OAUTH_CLIENT_SECRET=...
API_HEX_KEY=...

# LLM Providers
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...
XAI_API_KEY=...

# Database
DATABASE_URL=postgresql://user:pass@tutor-postgres:5432/tutor
REDIS_URL=redis://tutor-redis:6379/0

# Storage
S3_BUCKET=tutor-uploads
S3_ENDPOINT=...
S3_ACCESS_KEY=...
S3_SECRET_KEY=...

# RAG
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
RAG_CHUNK_SIZE=400
RAG_CHUNK_OVERLAP=50
RAG_MIN_SIMILARITY=0.65
RAG_MAX_CHUNKS=10

# App
APP_ENV=development
JWT_SECRET=...
CORS_ORIGINS=https://tutor.clevercreator.ai
```

---

## 33. Multi-Language & Localization

- **Interface**: i18n with `next-intl` — English, Spanish, French, Arabic, Mandarin, Hindi (initial)
- **RTL Support**: Arabic, Hebrew, Urdu layouts
- **Content**: AI generates explanations in student's preferred language
- **ESL/ELL Mode**: Bilingual explanations, simplified vocabulary, pronunciation help
- **Multilingual Code-Switching**: For bilingual students, seamlessly switch languages within explanations when it aids comprehension
- **Teacher materials**: Optional auto-translation of uploaded content

---

## 34. Implementation Roadmap (Detailed)

> Each phase includes week-by-week sub-steps. Dependencies are noted. The total timeline is approximately 40-50 weeks for Phases 1-4, with Phase 5 being ongoing.

---

### Phase 1: Foundation (8-10 weeks)
**Goal**: Working core tutor — students can chat with AI tutors, teachers can upload materials, auth and credits work end-to-end.

#### Sprint 1.1 — Project Scaffolding & DevOps (Week 1-2)
```
Backend:
  1.1.1  Initialize Python project (pyproject.toml, Poetry/uv, Python 3.13)
  1.1.2  FastAPI app skeleton with router structure:
         app/
           main.py
           routers/ (auth, sessions, chat, personas, knowledge_bases, students, teachers)
           services/ (ai_providers, rag, root_site_api, token_service, prompt_builder)
           models/ (pydantic schemas for all API request/response)
           db/ (connection pool, queries)
           tasks/ (celery tasks)
           middleware/ (auth, rate_limit, cors, logging)
  1.1.3  Pydantic v2 settings management (config.py with env validation)
  1.1.4  Structured logging (structlog + OpenTelemetry setup)
  1.1.5  asyncpg connection pool setup with health checks

Frontend:
  1.1.6  Next.js 16 project with App Router + TypeScript strict mode
  1.1.7  Tailwind 4 + shadcn/ui 4 setup and theming (light/dark, OKLCH)
  1.1.8  Zustand 5 store skeleton (auth, session, ui, chat stores)
  1.1.9  API client layer with httpx-style fetch wrapper (interceptors, retry, error handling)
  1.1.10 Layout shell: sidebar, header, main content area

DevOps:
  1.1.11 Docker Compose with all services:
         - tutor-api (FastAPI + uvicorn)
         - tutor-frontend (Next.js)
         - tutor-db (PostgreSQL 17 + pgvector 0.8.2)
         - tutor-redis (Redis 8)
         - tutor-celery (Celery 5.6 worker)
         - tutor-sandbox (Docker-in-Docker for code execution)
  1.1.12 PostgreSQL init.sql — ALL tables from Section 26 (idempotent, with indexes)
  1.1.13 Seed data SQL: personas, subjects, topics, standards (initial)
  1.1.14 Makefile / scripts: dev, test, migrate, seed, lint, format
  1.1.15 CI pipeline skeleton (GitHub Actions: lint, type-check, test)
```

#### Sprint 1.2 — Authentication & Root Site Integration (Week 3)
```
  1.2.1  RootSiteClient service (httpx async client):
         - OAuth 2.0 token exchange (authorization code flow)
         - JWT verification (RS256, JWKS endpoint caching)
         - User profile fetch (GET /api/user/details)
         - Credits balance check (GET /api/user/credits)
         - Credits deduction (POST /api/user/credits/deduct) — estimate, reserve, reconcile pattern
         - Model catalog sync (GET /api/catalog with ETag caching)
         - Plan/subscription check
  1.2.2  Auth middleware: extract JWT from cookie/header → verify → inject user context
  1.2.3  Internal X-Auth-Hex header for service-to-service calls
  1.2.4  Token service: estimate tokens before LLM call, reserve credits, reconcile after
  1.2.5  Frontend: OAuth redirect flow, token storage (httpOnly cookie), session management
  1.2.6  Frontend: protected route HOC, auth context provider
  1.2.7  Frontend: login/logout flow, redirect to root site for sign-up
  1.2.8  Tutor user sync: on first login, create tutor_users record from root site profile
  1.2.9  Role-based access control (student, teacher, parent, admin)
  1.2.10 Rate limiting middleware (per-user, per-endpoint, Redis-backed)
```

#### Sprint 1.3 — Core Tutoring Engine (Week 4-5)
```
AI Provider Layer:
  1.3.1  BaseProvider abstract class with unified interface:
         - stream_chat(messages, model_config) → AsyncGenerator[str]
         - count_tokens(text) → int
  1.3.2  OpenAI provider (GPT-4o, GPT-4o-mini)
  1.3.3  Anthropic provider (Claude 4 Sonnet, Claude 4 Haiku)
  1.3.4  Google Gemini provider (Gemini 2.5 Pro, Flash)
  1.3.5  xAI Grok provider (Grok-3, Grok-3-mini)
  1.3.6  Provider registry with model metadata (context window, cost, capabilities)
  1.3.7  Streaming SSE endpoint: POST /api/sessions/{id}/chat
  1.3.8  Error handling: retry, fallback to next provider, timeout management

Prompt Builder (8-Layer Assembly):
  1.3.9  Layer 1: Base persona system prompt (from personas table)
  1.3.10 Layer 2: Teacher custom overlay (from knowledge_bases teacher instructions)
  1.3.11 Layer 3: Interaction mode instructions (Teach Me, Quiz Me, etc.)
  1.3.12 Layer 4: RAG context injection (from retrieved KB chunks)
  1.3.13 Layer 5: Student mastery context (weak topics, current level)
  1.3.14 Layer 6: Student interests/preferences (for analogies, examples)
  1.3.15 Layer 7: Standards alignment context (current standard being addressed)
  1.3.16 Layer 8: Conversation history (sliding window with summarization)

Session Management:
  1.3.17 Session CRUD endpoints (create, get, list, resume, archive)
  1.3.18 Conversation history storage (messages table with metadata)
  1.3.19 Session state tracking (topic, mastery, mode, hint level)
  1.3.20 Session summary generation (AI-generated recap at session end)

Safety Layer:
  1.3.21 Input moderation (OpenAI moderation API or custom)
  1.3.22 Output moderation (scan AI response before sending)
  1.3.23 Age-appropriate content filter (grade-band rules)
  1.3.24 Anti-cheat detection (direct answer requests, copy-paste detection)
  1.3.25 PII detection and redaction
  1.3.26 Content guardrails injected into system prompt

Interaction Modes:
  1.3.27 Teach Me mode — Socratic dialogue, layered explanations
  1.3.28 Quiz Me mode — AI-generated questions, adaptive difficulty
  1.3.29 Practice mode — exercises with step-by-step hints
  1.3.30 Explore mode — curiosity-driven, tangent-friendly
  1.3.31 Show Your Thinking mode — student explains reasoning, AI evaluates metacognition
  1.3.32 Writing Workshop mode — rubric-based writing feedback (iterative drafts)
```

#### Sprint 1.4 — RAG Pipeline & Teacher Dashboard (Week 6-7)
```
RAG Pipeline:
  1.4.1  Document upload endpoint (POST /api/knowledge-bases/{id}/documents)
  1.4.2  File extraction: PDF (pypdf), DOCX (python-docx), PPTX (python-pptx), TXT, MD
  1.4.3  Semantic chunking with configurable size (400 tokens) and overlap (50 tokens)
  1.4.4  Embedding generation via OpenAI text-embedding-3-small (Celery async task)
  1.4.5  pgvector storage (1536-dim vectors with HNSW index)
  1.4.6  Similarity search with cosine distance + scope filtering (teacher/class/grade)
  1.4.7  Cross-encoder reranker for top-K refinement
  1.4.8  Citation tracking (link back to source document + page)
  1.4.9  Knowledge base CRUD (create, list, update, delete, assign to class)
  1.4.10 Document status tracking (uploading, processing, ready, error)
  1.4.11 Chunk preview/testing (teacher can query their KB before publishing)

Teacher Dashboard:
  1.4.12 Class creation + management (name, grade, subject, students)
  1.4.13 Student roster management (invite via code, CSV import, manual add)
  1.4.14 Knowledge base management UI (upload, view documents, status, delete)
  1.4.15 Persona customization (override system prompt per class)
  1.4.16 Basic analytics: session count, questions asked per student
  1.4.17 Preview mode: teacher chats with their own tutor to test KB

Student Onboarding:
  1.4.18 Student profile form (grade, interests, learning style preference, preferred language)
  1.4.19 Class join flow (enter class code or accept invite)
  1.4.20 Initial subject selection and interest mapping
```

#### Sprint 1.5 — UI Polish & Core UX (Week 8-10)
```
Chat Interface:
  1.5.1  Chat message rendering: Markdown, KaTeX math, syntax-highlighted code blocks
  1.5.2  Streaming display with typing indicator and progressive rendering
  1.5.3  Quick action chips (mode-specific: "Explain more", "Give me a hint", "Quiz me")
  1.5.4  Conversation starters (AI-suggested based on recent topics)
  1.5.5  Message feedback (thumbs up/down with optional comment)
  1.5.6  Session panel: active session info, topic, mode indicator, session history

Age-Adaptive UI:
  1.5.7  K-2 layout: large buttons, avatars, emoji-rich, simplified text, audio TTS for prompts
  1.5.8  3-5 layout: colorful, gamified elements, clear navigation
  1.5.9  6-8 layout: balanced, content-focused, subject organization
  1.5.10 9-12 layout: mature, productivity-focused, keyboard shortcuts, dense info

Navigation:
  1.5.11 Tutor selection screen (browse personas by subject, personality)
  1.5.12 Subject browser (explore topics within subjects)
  1.5.13 Session history panel (list past sessions, resume, search)
  1.5.14 Mobile responsive layout (all breakpoints)

Quality:
  1.5.15 Error handling: toast notifications, retry prompts, graceful degradation
  1.5.16 Loading states: skeleton screens, progress indicators
  1.5.17 Keyboard navigation and screen reader basics
  1.5.18 Basic E2E test suite (Playwright: login, chat, upload document)
  1.5.19 API integration tests (pytest: auth, chat, RAG)
  1.5.20 Performance: Lighthouse audit, Core Web Vitals baseline
```

**Phase 1 Deliverable**: A fully working AI tutor where students can log in via Clever Creator, select a tutor persona, chat across 6 modes with streaming responses, and teachers can upload materials to customize their tutor's knowledge. Credits are tracked and deducted per the root site.

---

### Phase 2: Intelligence & Study Tools (8-10 weeks)
**Goal**: Smart tutoring — adaptive learning, mastery tracking, quizzes, flashcards, study tools, and URL-based learning.

#### Sprint 2.1 — Hint Engine & Quiz System (Week 1-2)
```
3-Level Hint Engine:
  2.1.1  Server-enforced hint levels (stored in session state, not client-side)
  2.1.2  Level 1: Nudge — "Think about what happens when you divide both sides..."
  2.1.3  Level 2: Structured hint — "Step 1 is to isolate x. What operation removes +5?"
  2.1.4  Level 3: Guided walkthrough — full step-by-step with student filling in gaps
  2.1.5  Hint level tracking per problem (resets per new problem)
  2.1.6  Prompt engineering for each hint level (restrict AI from giving answers at L1/L2)

Quiz System:
  2.1.7  AI-generated quiz questions from topic + mastery level + KB materials
  2.1.8  Question types: multiple choice, short answer, true/false, fill-in-the-blank, matching
  2.1.9  Adaptive difficulty: scale based on recent performance
  2.1.10 Misconception-aware distractors (wrong answers that test common mistakes)
  2.1.11 Explain My Answer: one-click detailed explanation after each question
  2.1.12 Quiz results: score, per-question analysis, mastery impact
  2.1.13 Quiz history and retake with new questions on same topics
```

#### Sprint 2.2 — Flashcards & Spaced Repetition (Week 3)
```
  2.2.1  AI-generated flashcards from topics, KB materials, or session content
  2.2.2  SM-2 spaced repetition algorithm implementation
  2.2.3  Flashcard CRUD: student can create, edit, favorite, archive
  2.2.4  Teacher-created flashcard sets assignable to classes
  2.2.5  Magic Notes: upload handwritten/typed notes → auto-generate flashcards + quiz + study guide
  2.2.6  Review scheduling: "You have 23 cards due today"
  2.2.7  Flashcard modes: classic flip, type answer, multiple choice from deck
  2.2.8  Front/back customization (text, math, code, image)
```

#### Sprint 2.3 — Study Tools: Summaries, Study Guides, URL Learning (Week 4-5)
```
URL-Based Learning:
  2.3.1  URL paste → content extraction (web scraper with readability)
  2.3.2  YouTube URL → transcript extraction (YouTube API)
  2.3.3  Ingested as temporary session context or permanent KB document
  2.3.4  "Teach me about this article/video" — AI tutors from the content

Auto-Generated Study Guides:
  2.3.5  Generate from topic: key concepts, definitions, formulas, common mistakes, practice problems, summary
  2.3.6  Generate from teacher KB: follow structure of uploaded materials
  2.3.7  Pre-test study guide: based on weak mastery areas + mistake journal
  2.3.8  Export: PDF download, printable format, shareable link

Quick Summary:
  2.3.9  One-click summary of any document, URL, or YouTube video
  2.3.10 Adjustable length: 1-paragraph, 1-page, detailed
  2.3.11 Highlight key terms with definitions

Session Summaries:
  2.3.12 AI-generated recap at session end (what was covered, what to review)
  2.3.13 Email/notification with session summary to student (and optionally parent)
```

#### Sprint 2.4 — Mastery Tracking & Adaptive Learning (Week 6-7)
```
Mastery Tracking:
  2.4.1  5-level mastery model: Novice → Beginner → Proficient → Advanced → Master
  2.4.2  Per-topic and per-standard mastery scores
  2.4.3  Mastery updates from: quiz results, chat interactions, hint usage, problem solving
  2.4.4  Mastery decay over time (if not reviewed)
  2.4.5  Visual mastery dashboard for students

Misconception Detection Engine:
  2.4.6  Pattern matching on common misconceptions per topic (seeded database)
  2.4.7  AI analysis of student explanations to detect WHY they're wrong
  2.4.8  Misconception-specific remediation paths
  2.4.9  Teacher alerts when persistent misconceptions detected

Diagnostic Assessment:
  2.4.10 Placement test on first use of a subject (adaptive, 10-15 questions)
  2.4.11 Gap identification: pinpoint exactly which prerequisite concepts are missing
  2.4.12 Suggested starting point based on diagnostic results

Learning Path Generation:
  2.4.13 AI generates personalized learning path based on: mastery, gaps, goals, pace
  2.4.14 Path visualization: linear roadmap with milestones
  2.4.15 Adaptive: path adjusts as mastery changes

Standards Alignment:
  2.4.16 Import Common Core (Math + ELA) and NGSS standards (seed data)
  2.4.17 Map topics to standards
  2.4.18 Progress tracking per standard for reporting

Interleaving Engine:
  2.4.19 Mix review of old topics into new learning sessions
  2.4.20 Configurable interleaving ratio (default 20% review)
  2.4.21 Priority: weakest topics + topics approaching mastery decay
```

#### Sprint 2.5 — Model Router & Advanced AI (Week 8-10)
```
Model Router:
  2.5.1  Complexity classifier: route simple questions to cheaper/faster models
  2.5.2  Cost optimization: use GPT-4o-mini for hints, GPT-4o for complex explanations
  2.5.3  Plan-gated access: some models only available on certain subscription plans
  2.5.4  Auto-fallback: if primary provider fails, route to next available
  2.5.5  Provider health monitoring with circuit breaker pattern
  2.5.6  Usage analytics: cost per student, per subject, per model

Teacher KB Enhancements:
  2.5.7  Standards tagging on KB documents
  2.5.8  KB preview with test queries
  2.5.9  Class-level and grade-level KB assignment
  2.5.10 KB analytics: which documents are cited most, which are never used
```

**Phase 2 Deliverable**: An intelligent tutor that adapts to each student's level, tracks mastery, detects misconceptions, generates quizzes/flashcards/study guides, learns from URLs and notes, and routes AI calls cost-effectively.

---

### Phase 3: Engagement & Interactive Tools (8-10 weeks)
**Goal**: Make learning fun and multi-modal — gamification, interactive tools, audio lessons, emotional intelligence.

#### Sprint 3.1 — Gamification System (Week 1-2)
```
  3.1.1  XP system: earn XP from sessions, quizzes, streaks, milestones
  3.1.2  Level system: age-themed levels (K-5: animal evolution, 6-12: space explorer)
  3.1.3  Daily streaks with streak shields (miss 1 day without losing streak)
  3.1.4  Badge system: achievement-based (First Quiz, 7-Day Streak, Mastery in Algebra, etc.)
  3.1.5  Leaderboard: class-level, opt-in, weekly resets
  3.1.6  XP multipliers for challenging activities (harder quizzes, Show Your Thinking)
  3.1.7  Progress celebrations (confetti, level-up animations, tutor congratulations)
  3.1.8  Gamification dashboard widget on student home
```

#### Sprint 3.2 — Parent Dashboard & Co-Learning (Week 3-4)
```
Parent Dashboard:
  3.2.1  Child progress overview: mastery, session count, time spent, topics covered
  3.2.2  Activity feed: recent sessions with AI-generated summaries
  3.2.3  Report generation: weekly/monthly PDF progress report
  3.2.4  Controls: session time limits, subject restrictions, content filters
  3.2.5  Parental consent flow (COPPA compliance for under-13)
  3.2.6  Multi-child support (parent sees all children)

Parent Co-Learning Mode:
  3.2.7  Parent joins child's session as observer or participant
  3.2.8  "Parent guide" sidebar: tips on how to help without giving answers
  3.2.9  Shared session history: parent and child see the same conversation
  3.2.10 Parent-specific conversation starters ("Help me help my child with fractions")
```

#### Sprint 3.3 — Interactive Tools (Week 5-6)
```
Digital Whiteboard (tldraw):
  3.3.1  Embedded whiteboard in chat interface
  3.3.2  Draw-to-solve: student draws, AI interprets and provides feedback
  3.3.3  AI draws: tutor can render diagrams, graphs, geometric figures
  3.3.4  Shared state between student and AI during session
  3.3.5  Whiteboard snapshots saved to session history

Code Sandbox (Docker-based):
  3.3.6  Monaco Editor embedded in chat interface
  3.3.7  Python and JavaScript execution in isolated Docker container
  3.3.8  Resource limits: 30s timeout, 128MB memory, no network
  3.3.9  AI code review: tutor reviews student code and suggests improvements
  3.3.10 Step-by-step debugging guidance
  3.3.11 Code challenges: AI generates coding exercises

Math Editor (MathLive):
  3.3.12 Interactive math input field in chat
  3.3.13 Student types math expressions rendered in real-time
  3.3.14 MathJSON export for AI to understand the expression
  3.3.15 Step-by-step equation solving with student participation
```

#### Sprint 3.4 — Audio Lessons & Memory Tools (Week 7-8)
```
Audio Lesson Generator:
  3.4.1  AI scripts conversational audio lessons from any topic or KB material
  3.4.2  TTS rendering (OpenAI TTS API): two-host conversation format
  3.4.3  Formats: Brief (2 min), Deep Dive (10 min), Story Mode (narrative for K-5)
  3.4.4  Audio player UI with speed control, bookmarks
  3.4.5  Teacher can generate and assign audio lessons from their KB

Mind Map Generation:
  3.4.6  Generate visual mind maps from any topic
  3.4.7  react-flow rendering with interactive nodes
  3.4.8  Color-coded by mastery level
  3.4.9  Click any node to start a tutoring session on that concept
  3.4.10 Export: image, PDF

Memory Score:
  3.4.11 Track personal retention per flashcard/topic
  3.4.12 Predict when student will forget (spaced repetition curve)
  3.4.13 Proactive review reminders ("Review fractions before Thursday")

Roleplay Scenarios:
  3.4.14 Subject-appropriate roleplay (history debates, science experiments, language conversations)
  3.4.15 Character personas for roleplay (historical figures, scientists)
  3.4.16 Assessed: rubric-based evaluation of roleplay performance
```

#### Sprint 3.5 — Emotional Intelligence & Engagement Features (Week 9-10)
```
Emotional Intelligence Layer:
  3.5.1  Frustration detection from interaction patterns:
         - Rapid repeated wrong answers
         - Short/angry messages
         - Long pauses followed by "I don't get it"
         - Session abandonment patterns
  3.5.2  Adaptive responses: simplify, offer encouragement, suggest break, change approach
  3.5.3  Confidence detection: student is breezing through → increase difficulty
  3.5.4  Boredom detection: repetitive patterns → suggest new topic or mode change

Knowledge Graph Visualization:
  3.5.5  Interactive concept map showing how topics connect
  3.5.6  Mastery overlay: green (mastered) → yellow (learning) → red (struggling)
  3.5.7  Prerequisite chains visible ("You need X before Y")
  3.5.8  Click any node to start learning

Mistake Journal:
  3.5.9  Auto-logged: every mistake with context, correct answer, student's reasoning
  3.5.10 Pattern analysis: "You consistently confuse X with Y"
  3.5.11 Review mode: revisit past mistakes with fresh explanations
  3.5.12 Teacher view: aggregate mistake patterns across class

"Why Am I Learning This?" Engine:
  3.5.13 Real-world applications of every topic
  3.5.14 Career connections ("Engineers use algebra to...")
  3.5.15 Personalized to student interests ("You like gaming — game devs use trigonometry for...")

Notification System:
  3.5.16 In-app notifications: streak reminders, review due, teacher assignments
  3.5.17 Email notifications: weekly progress, parent reports
  3.5.18 Push notifications (when PWA is implemented)
```

#### Sprint 3.6 — Educational Gaming Engine (Week 11-13, extends Phase 3)
```
Gaming Framework:
  3.6.1  Game template system: database schema (game_templates, game_sessions, game_assignments, game_leaderboard)
  3.6.2  Game session API: start, answer, complete, results (see Section 22.9)
  3.6.3  Adaptive difficulty engine: zone of proximal development, scales with mastery
  3.6.4  Game-to-mastery integration: every game answer updates mastery tracker + mistake journal
  3.6.5  Game recommendation engine: suggest games based on learning gaps + learning style
  3.6.6  Teacher game assignment: assign specific games to classes with custom parameters
  3.6.7  Game leaderboard: class-level, weekly reset, opt-in
  3.6.8  Learning pathway selector: onboarding preference + AI detection over time

K-2 Games (Initial Set):
  3.6.9  Story Adventure template: narrative-driven puzzle solving with drag-and-drop
  3.6.10 Matching Game template: visual matching with audio feedback
  3.6.11 Virtual Pet template: nurture pet by answering questions correctly
  3.6.12 Treasure Hunt template: exploration-based learning with clues

3-5 Games (Initial Set):
  3.6.13 RPG Quest template: Prodigy-style battle-by-learning with equipment rewards
  3.6.14 Building Game template: construct structures using subject knowledge
  3.6.15 Mystery Detective template: solve mysteries using clues from curriculum
  3.6.16 Fraction Pizza Shop: run a pizza shop with fraction-based orders

6-8 Games (Initial Set):
  3.6.17 Escape Room template: timed multi-problem challenge rooms
  3.6.18 Civilization Builder template: manage resources with math/history decisions
  3.6.19 Coding Maze template: program a robot to navigate (block-based and text)
  3.6.20 Speed Challenge template: timed accuracy competition

9-12 Games (Initial Set):
  3.6.21 Business Simulation template: budgeting, revenue, market analysis
  3.6.22 Debate Tournament template: AI-scored formal debate with evidence
  3.6.23 Case Study Mystery template: analyze data, form hypotheses
  3.6.24 Stock Market Sim template: invest virtual money, track trends

Cross-Cutting:
  3.6.25 Learning style adaptation layer: visual/auditory/kinesthetic/reading modes per game
  3.6.26 Game results dashboard: student sees game history, mastery earned, streaks
  3.6.27 Teacher game analytics: which games work best for which topics/students
  3.6.28 Game XP integration: game achievements feed into main gamification system
```

**Phase 3 Deliverable**: An engaging, multi-modal learning platform with gamification, interactive tools (whiteboard, code sandbox, math editor), audio lessons, educational games by age/style/subject, emotional adaptation, and parent involvement.

---

### Phase 4: Scale, Test Prep & Advanced Features (10-12 weeks)
**Goal**: Enterprise features — IELTS/SAT/PSAT test prep, LMS integration, marketplace, compliance, internationalization.

#### Sprint 4.1 — Test Prep Framework: Core Engine (Week 1-3)
```
Test Prep Infrastructure:
  4.1.1  Test profile system: pluggable profiles for IELTS, SAT, PSAT, ACT, AP
  4.1.2  Test profile database tables (from Section 23.4)
  4.1.3  Scoring engine with descriptor-locked evaluation (per test type)
  4.1.4  Mock test generator: full-length timed tests from question bank
  4.1.5  Timed test mode: countdown, section transitions, auto-submit
  4.1.6  Score prediction model: estimate real score from practice performance
  4.1.7  Gap analysis: identify weakest areas vs target score
  4.1.8  Study plan generation: personalized roadmap to target score by target date

IELTS Module:
  4.1.9  Speaking practice: AI examiner for Parts 1, 2, 3
  4.1.10 Speaking evaluation: Fluency, Lexical Resource, Grammar, Pronunciation scoring
  4.1.11 Audio recording + Whisper transcription for speaking
  4.1.12 Writing practice: Task 1 (graph/letter) and Task 2 (essay)
  4.1.13 Writing evaluation: Task Achievement, Coherence, Lexical, Grammar scoring
  4.1.14 Band prediction per criterion and overall
  4.1.15 "Move to next band" coaching: specific tips to gain +0.5
  4.1.16 Reading practice: AI-generated IELTS-style passages + question types
  4.1.17 Listening practice: AI-generated audio with accent variety
  4.1.18 Progress tracking: band scores over time, per section

SAT/ACT/PSAT Module:
  4.1.19 Reading + Writing section: passage-based questions, grammar rules
  4.1.20 Math section: with and without calculator, grid-in answers
  4.1.21 Score prediction: estimated SAT/ACT composite
  4.1.22 College-readiness benchmarks
  4.1.23 PSAT/NMSQT profile: slightly shorter format, National Merit qualifier thresholds
  4.1.24 AP Exam profiles: per-subject scoring rubrics, FRQ practice, MCQ banks
```

#### Sprint 4.2 — LMS Integration & Teacher Tools (Week 4-5)
```
LMS Integration:
  4.2.1  Google Classroom integration (Classroom API: roster sync, assignments)
  4.2.2  Canvas LMS integration via LTI 1.3 (single sign-on, grade passback)
  4.2.3  Assignment sync: teacher creates assignment in LMS → appears in tutor
  4.2.4  Grade sync: tutor sends quiz/assessment grades back to LMS gradebook

Teacher AI Co-Pilot:
  4.2.5  Lesson plan generator from standards + KB materials
  4.2.6  Assessment generator: create quizzes/tests from curriculum
  4.2.7  Class-wide misconception report: "40% of students struggle with X"
  4.2.8  Differentiation suggestions: group students by level, suggest activities
  4.2.9  Parent communication drafts: AI writes progress update emails

Content Marketplace:
  4.2.10 Teachers share KB collections (opt-in, with ratings)
  4.2.11 KB cloning: one-click copy a shared knowledge base
  4.2.12 Flashcard deck sharing
  4.2.13 Moderation: review shared content before publishing
  4.2.14 Usage analytics for shared content
```

#### Sprint 4.3 — Advanced Analytics & Homework Scanner (Week 6-7)
```
Advanced Analytics:
  4.3.1  At-risk prediction: ML model identifies struggling students early
  4.3.2  Learning pattern analysis: optimal study times, session length correlation
  4.3.3  Engagement metrics: retention rate, feature usage, drop-off points
  4.3.4  Admin analytics dashboard: platform-wide usage, model costs, error rates
  4.3.5  Exportable reports: CSV, PDF for school administrators

Homework Scanner (OCR + Guided Solving):
  4.3.6  Camera capture or image upload
  4.3.7  OCR processing (Tesseract.js or cloud OCR)
  4.3.8  Problem identification: detect subject, topic, difficulty
  4.3.9  Guided solving: not just the answer, but step-by-step with hints
  4.3.10 Photo-based math: animated visual walkthrough (Photomath-style)
  4.3.11 Batch homework: scan multiple problems, get guided help for each

Brain Beats:
  4.3.12 Convert flashcard decks to catchy songs via AI lyric generation + TTS
  4.3.13 Audio player with lyrics display
  4.3.14 Especially effective for K-5 (multiplication tables, vocabulary, dates)
```

#### Sprint 4.4 — Compliance, Accessibility & i18n (Week 8-10)
```
Compliance:
  4.4.1  COPPA audit: parental consent flows, data handling for under-13
  4.4.2  FERPA compliance: educational records handling, access controls
  4.4.3  GDPR: data export, right to deletion, consent management
  4.4.4  Audit logging: all data access and modifications logged
  4.4.5  Data retention policies with automated cleanup

Accessibility (WCAG 2.1 AA):
  4.4.6  Full keyboard navigation
  4.4.7  Screen reader compatibility (ARIA labels, semantic HTML)
  4.4.8  Color contrast compliance
  4.4.9  Focus management for dynamic content (chat messages, modals)
  4.4.10 Alt text for all generated images/diagrams
  4.4.11 Accessibility audit with automated testing (axe-core)

Multi-Language & Localization:
  4.4.12 next-intl setup: English, Spanish, French, Arabic, Mandarin, Hindi
  4.4.13 RTL layout support (Arabic, Hebrew, Urdu)
  4.4.14 AI content generation in student's preferred language
  4.4.15 ESL/ELL mode: bilingual explanations, simplified vocabulary
  4.4.16 Teacher material auto-translation (optional)

Wellness Guardian:
  4.4.17 Session time limits (configurable per age group)
  4.4.18 Break reminders ("You've been studying for 45 minutes — take a break!")
  4.4.19 Quiet hours (no notifications during sleep hours)
  4.4.20 Parent-configurable limits

Micro-Tutoring Modes:
  4.4.21 5-minute quick review sessions
  4.4.22 "One concept a day" mode
  4.4.23 Bus-stop learning: short audio-based sessions for commute
```

**Phase 4 Deliverable**: A complete platform with IELTS/SAT/ACT test prep, LMS integration, teacher marketplace, homework scanning, full compliance (COPPA/FERPA/GDPR), accessibility, and multi-language support.

---

### Phase 5: Beyond — Mobile, Voice, Collaboration & University (Ongoing)
**Goal**: Expand reach — mobile apps, voice-first experience, collaborative learning, university extension.

#### Sprint 5.1 — Mobile & Voice (Week 1-4)
```
  5.1.1  PWA setup: service worker, offline caching, install prompt
  5.1.2  Offline mode: cached flashcards, study guides, past session summaries
  5.1.3  Voice input: STT (Whisper API) for hands-free tutoring
  5.1.4  Voice output: TTS for AI responses (critical for K-2 pre-readers)
  5.1.5  Voice-first mode: entire session via voice for young learners
  5.1.6  React Native app (optional): native iOS/Android if demand warrants
  5.1.7  Push notifications via service worker
```

#### Sprint 5.2 — Collaboration & Social (Week 5-8)
```
  5.2.1  Collaborative study rooms: 2-5 students + AI moderator
  5.2.2  Shared whiteboard in study rooms
  5.2.3  Study group matching: pair students with complementary strengths
  5.2.4  Peer tutoring: advanced students help beginners with AI oversight
  5.2.5  AI Video Call: spontaneous video conversation with tutor character (language subjects)
  5.2.6  Pronunciation assessment with phonetic highlighting
  5.2.7  Digital learning portfolio: curated collection of student's best work
  5.2.8  Portfolio export for college applications
```

#### Sprint 5.3 — Additional Test Prep Profiles (Week 9-12)
```
High School Admissions:
  5.3.1  SHSAT profile: ELA + Math, NYC-specific format, composite scoring
  5.3.2  ISEE profile: Verbal, Quantitative, Reading, Math, Essay (stanine scoring)
  5.3.3  SSAT profile: Verbal, Quantitative, Reading, Writing (scaled scoring)
  5.3.4  HSPT profile: Verbal, Quantitative, Reading, Math, Language (percentile)

International English (extended):
  5.3.5  TOEFL iBT profile: Reading, Listening, Speaking, Writing (0-120)
  5.3.6  Cambridge FCE/CAE/CPE profiles: exam-specific formats
  5.3.7  Duolingo English Test profile (if applicable)

Graduate & Professional:
  5.3.8  GRE profile: Verbal, Quantitative, Analytical Writing
  5.3.9  GMAT profile: Quantitative, Verbal, Data Insights, Analytical Writing

General:
  5.3.10 GED profile: Math, Science, Social Studies, Language Arts (100-200)
```

#### Sprint 5.4 — Advanced Content, Games & University (Week 13-16+)
```
Content & Simulations:
  5.4.1  Science simulations integration (PhET, Desmos embeds)
  5.4.2  Content freshness engine: tie topics to current events
  5.4.3  Study scheduling intelligence: suggest optimal study times
  5.4.4  Lecture recording ingestion: upload audio → transcribe → teach from it

University Extension:
  5.4.5  University mode: course-level KB, professor tools, TA mode
  5.4.6  Research paper analysis: upload papers, generate summaries, quiz from content
  5.4.7  Citation helper: proper academic referencing

Expanded Game Content:
  5.4.8  New game templates per subject area (quarterly releases)
  5.4.9  Community game templates: teachers create custom game configs
  5.4.10 Multiplayer tournament system: school-wide and inter-school competitions
  5.4.11 Seasonal game events: math olympiad week, science fair challenge, history bowl

Additional Test Profiles (Phase 5+):
  5.4.12 LSAT profile: Logical Reasoning, Analytical Reasoning, Reading Comprehension
  5.4.13 MCAT profile: Bio/Biochem, Chem/Physics, CARS, Psych/Soc
  5.4.14 STEAM assessments: cross-disciplinary STEM + Arts aptitude
  5.4.15 AMC/AIME profiles: competitive math problem solving
  5.4.16 Science Olympiad prep: event-specific practice
  5.4.17 STAAR, Regents, MAP, SBAC profiles: state-specific assessments
  5.4.18 ASVAB profile: 10-section vocational aptitude
  5.4.19 CLEP profiles: 34 college-level subject exams
  5.4.20 CLT profile: Verbal Reasoning, Grammar, Quantitative

Infrastructure:
  5.4.21 Edge AI: run smaller models (Phi, Gemma) locally for offline basic tutoring
  5.4.22 AR/VR-ready APIs: prepare for spatial learning experiences
  5.4.23 Optional Forge deep link for advanced CS education
```

**Phase 5 Deliverable**: A fully cross-platform, voice-enabled, collaborative AI tutoring platform with 30+ test prep profiles, expanding game library, and university-level education support.

---

## 35. Key Design Decisions

| Decision | Why |
|---|---|
| **Fully independent application** | Own Docker containers, codebase, database — no runtime dependency on ChatterMate |
| **Root site API only** | Auth, billing, credits, catalog via API — no duplication of these services |
| **FastAPI + Next.js** | Modern, performant, AI-native stack; Python for AI/ML ecosystem |
| **Pinned tech stack versions** | All major dependencies pinned to latest stable (March 2026) to avoid breaking upgrades |
| **PostgreSQL + pgvector** | Single database for relational + vector search; no separate vector DB overhead |
| **asyncpg, raw SQL, no ORM** | Maximum performance and control over queries |
| **7 interaction modes** | Original 4 + Show Your Thinking + Writing Workshop + Debate/Roleplay |
| **8-layer prompt assembly** | Deepest context injection: persona + custom + mode + RAG + mastery + interests + standards + history |
| **Misconception detection** | Diagnose WHY students are wrong, not just THAT they're wrong |
| **Emotional intelligence** | Detect frustration from interaction patterns; adapt without cameras/mics |
| **Age-adaptive UI** | 4 grade-band layouts (K-2, 3-5, 6-8, 9-12) — not one-size-fits-all |
| **Knowledge graph** | Show students how concepts connect; mastery overlay |
| **Interleaving** | Research-backed 43% retention improvement from mixed-topic review |
| **Teacher AI co-pilot** | Helps teachers teach better, not just students learn |
| **Wellness guardian** | Responsible AI: session limits, break reminders, quiet hours |
| **Server-enforced hints** | Hint rules enforced server-side — users can't bypass by manipulating client |
| **SSE streaming** | Conversational feel; lower perceived latency; industry standard |
| **Celery for async** | Document processing, embedding generation, reports, analytics |
| **Built-in code sandbox** | Independent Docker sandbox; Forge as optional deep link only |
| **Standards-aligned** | Every topic mapped to Common Core, NGSS; progress reports per standard |
| **COPPA + FERPA** | Non-negotiable for K-12; parental consent, data protection, audit logging |
| **AI Study Tools** | NotebookLM/Quizlet-inspired: audio lessons, mind maps, magic notes, brain beats, memory score |
| **URL + multimedia ingestion** | Learn from any URL, YouTube video, or uploaded lecture recording |
| **Pluggable test prep framework** | IELTS, SAT, ACT, AP as swappable "test profiles" — descriptor-locked scoring |
| **IELTS band descriptor-locked** | Evaluation criteria locked to official IELTS band descriptors for accuracy |
| **Educational Gaming Engine** | Optional game-based learning pathway — RPG quests, escape rooms, simulations, building games — all feeding same mastery tracker |
| **Multi-pathway learning** | Students choose how to learn (chat, quiz, flashcard, game, audio, test prep) — AI recommends based on what works for them |
| **30+ test prep profiles** | IELTS, SAT, PSAT, SHSAT, ISEE, SSAT, GED, ACT, AP, GRE, GMAT, LSAT, MCAT, TOEFL, Cambridge, STEAM, AMC, state exams |
| **Competitor feature parity** | Matched or exceeded: Khanmigo (Socratic), Quizlet (flashcards/AI), Duolingo (roleplay/video call), Photomath (visual math), Prodigy (game-based) |

---

## 36. Competitive Feature Matrix

Shows which competitor features we match, exceed, or uniquely offer.

| Feature | Khanmigo | Quizlet | Duolingo Max | Photomath | Prodigy | **Our Platform** |
|---|---|---|---|---|---|---|
| Socratic teaching method | Yes | No | No | No | No | **Yes (7 modes)** |
| Multi-subject | Math-focused | Yes | Languages | Math only | Math only | **All subjects** |
| Custom KB / teacher training | No | User decks | No | No | No | **Yes (full RAG)** |
| Flashcards + spaced repetition | No | Yes | No | No | No | **Yes (SM-2)** |
| Magic Notes (notes to cards) | No | Yes | No | No | No | **Yes** |
| Brain Beats (songs) | No | Yes | No | No | No | **Yes** |
| AI-generated quizzes | Yes | Yes | Yes | No | No | **Yes (adaptive)** |
| Explain My Answer | Limited | No | Yes | Step-by-step | No | **Yes** |
| Audio lessons | No | No | No | No | No | **Yes (Deep Dive)** |
| URL-based learning | No | No | No | No | No | **Yes (URL + video)** |
| Video call with AI | No | No | Yes | No | No | **Yes (Phase 5)** |
| Roleplay scenarios | Debate only | No | Yes | No | No | **Yes (multi-subject)** |
| Photo-based problem solving | No | No | No | Yes | No | **Yes (OCR + guided)** |
| Age-adaptive UI | Limited | No | No | No | Yes | **Yes (4 layouts)** |
| **Game-based learning** | No | No | No | No | **Yes (math RPG)** | **Yes (all subjects, 4 age bands, 8+ game types)** |
| **Learning style adaptation** | No | No | No | No | Limited | **Yes (visual, auditory, kinesthetic, R/W)** |
| **Multi-pathway learning** | No | No | No | No | No | **Yes (chat + quiz + game + audio + test prep)** |
| Knowledge graph visualization | No | No | No | No | No | **Yes** |
| Emotional intelligence | No | No | No | No | No | **Yes** |
| Parent co-learning | No | No | No | No | Parent reports | **Yes (co-learning + reports)** |
| **30+ test prep profiles** | No | No | No | No | No | **Yes (IELTS, SAT, PSAT, SHSAT, GED, etc.)** |
| Whiteboard | No | No | No | No | No | **Yes (tldraw)** |
| Code sandbox | No | No | No | No | No | **Yes (Docker)** |
| Gamification (XP/badges) | Limited | No | Yes | No | Yes | **Yes (full system)** |
| Standards alignment | Yes | No | No | No | Yes | **Yes** |
| LMS integration | No | Limited | No | No | Yes | **Yes (LTI 1.3)** |
| Misconception detection | Limited | No | No | No | Limited | **Yes (engine)** |
| **Multiplayer/class challenges** | No | No | No | No | Limited | **Yes (study rooms + game tournaments)** |

---

*Document version: 3.1 | Last updated: March 2026*
