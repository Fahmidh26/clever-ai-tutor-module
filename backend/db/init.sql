-- AI Tutor baseline schema (Phase 1.1.12)
-- Idempotent setup for PostgreSQL 17 + pgvector.

CREATE EXTENSION IF NOT EXISTS vector;

-- Core tables
CREATE TABLE IF NOT EXISTS tutor_users (
    id                  SERIAL PRIMARY KEY,
    root_user_id        INTEGER NOT NULL UNIQUE,
    role                VARCHAR(20) NOT NULL DEFAULT 'student',
    display_name        VARCHAR(255),
    grade_level         SMALLINT,
    learning_style      VARCHAR(50),
    preferred_language  VARCHAR(10) DEFAULT 'en',
    interests_json      JSONB,
    onboarded_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tutor_personas (
    id                  SERIAL PRIMARY KEY,
    slug                VARCHAR(100) NOT NULL UNIQUE,
    name                VARCHAR(100) NOT NULL,
    tagline             VARCHAR(255),
    avatar_url          VARCHAR(500),
    personality         TEXT NOT NULL,
    system_prompt       TEXT NOT NULL,
    teaching_style      VARCHAR(50) NOT NULL,
    subject_expertise   JSONB,
    is_custom           BOOLEAN DEFAULT FALSE,
    created_by_teacher_id INTEGER REFERENCES tutor_users(id),
    is_active           BOOLEAN DEFAULT TRUE,
    sort_order          INTEGER DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tutor_sessions (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES tutor_users(id),
    persona_id          INTEGER NOT NULL REFERENCES tutor_personas(id),
    class_id            INTEGER,
    subject             VARCHAR(255),
    topic               VARCHAR(255),
    subtopic            VARCHAR(255),
    grade_level         SMALLINT,
    mode                VARCHAR(20) DEFAULT 'teach',
    status              VARCHAR(20) DEFAULT 'active',
    summary             TEXT,
    tokens_used         INTEGER DEFAULT 0,
    model_used          VARCHAR(100),
    emotional_state_log JSONB,
    started_at          TIMESTAMPTZ DEFAULT NOW(),
    ended_at            TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tutor_messages (
    id                  SERIAL PRIMARY KEY,
    session_id          INTEGER NOT NULL REFERENCES tutor_sessions(id) ON DELETE CASCADE,
    kb_id               INTEGER REFERENCES knowledge_bases(id) ON DELETE SET NULL,
    role                VARCHAR(20) NOT NULL,
    content             TEXT NOT NULL,
    mode                VARCHAR(20) DEFAULT 'chat',
    hint_level          SMALLINT,
    tokens_used         INTEGER DEFAULT 0,
    model_used          VARCHAR(100),
    feedback            VARCHAR(10),
    reasoning_quality_score SMALLINT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Class tables (created before kb assignments to satisfy foreign keys)
CREATE TABLE IF NOT EXISTS classes (
    id                  SERIAL PRIMARY KEY,
    teacher_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    name                VARCHAR(255) NOT NULL,
    subject             VARCHAR(255),
    grade_level         SMALLINT,
    invite_code         VARCHAR(20) UNIQUE,
    persona_id          INTEGER REFERENCES tutor_personas(id),
    settings_json       JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS class_enrollments (
    id                  SERIAL PRIMARY KEY,
    class_id            INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    enrolled_at         TIMESTAMPTZ DEFAULT NOW(),
    status              VARCHAR(20) DEFAULT 'active',
    UNIQUE(class_id, student_id)
);

CREATE TABLE IF NOT EXISTS teacher_student_links (
    id                  SERIAL PRIMARY KEY,
    teacher_id          INTEGER NOT NULL REFERENCES tutor_users(id) ON DELETE CASCADE,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id) ON DELETE CASCADE,
    status              VARCHAR(20) NOT NULL DEFAULT 'active',
    source              VARCHAR(50) DEFAULT 'manual',
    notes_json          JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(teacher_id, student_id)
);

CREATE TABLE IF NOT EXISTS teacher_join_codes (
    id                  SERIAL PRIMARY KEY,
    teacher_id          INTEGER NOT NULL REFERENCES tutor_users(id) ON DELETE CASCADE,
    code                VARCHAR(24) NOT NULL UNIQUE,
    status              VARCHAR(20) NOT NULL DEFAULT 'active',
    expires_at          TIMESTAMPTZ,
    metadata_json       JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS teacher_join_requests (
    id                  SERIAL PRIMARY KEY,
    teacher_id          INTEGER NOT NULL REFERENCES tutor_users(id) ON DELETE CASCADE,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id) ON DELETE CASCADE,
    join_code_id        INTEGER REFERENCES teacher_join_codes(id) ON DELETE SET NULL,
    class_id            INTEGER REFERENCES classes(id) ON DELETE SET NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'pending',
    request_message     TEXT,
    reviewed_by         INTEGER REFERENCES tutor_users(id) ON DELETE SET NULL,
    requested_at        TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at         TIMESTAMPTZ,
    UNIQUE(teacher_id, student_id, class_id)
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_name = 'tutor_sessions_class_id_fkey'
          AND table_name = 'tutor_sessions'
    ) THEN
        ALTER TABLE tutor_sessions
        ADD CONSTRAINT tutor_sessions_class_id_fkey
        FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS parent_student_links (
    id                  SERIAL PRIMARY KEY,
    parent_id           INTEGER NOT NULL REFERENCES tutor_users(id),
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    consent_status      VARCHAR(20) DEFAULT 'pending',
    consent_date        TIMESTAMPTZ,
    restrictions_json   JSONB,
    UNIQUE(parent_id, student_id)
);

-- RAG / KB tables
CREATE TABLE IF NOT EXISTS knowledge_bases (
    id                  SERIAL PRIMARY KEY,
    owner_id            INTEGER NOT NULL REFERENCES tutor_users(id),
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    subject             VARCHAR(255),
    grade_level         SMALLINT,
    visibility          VARCHAR(20) DEFAULT 'private',
    status              VARCHAR(20) DEFAULT 'active',
    standards_json      JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kb_documents (
    id                  SERIAL PRIMARY KEY,
    kb_id               INTEGER NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    filename            VARCHAR(500) NOT NULL,
    file_path           VARCHAR(1000) NOT NULL,
    file_type           VARCHAR(50),
    file_size           BIGINT,
    status              VARCHAR(20) DEFAULT 'queued',
    page_count          INTEGER,
    extracted_text_preview TEXT,
    error_message       TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kb_chunks (
    id                  SERIAL PRIMARY KEY,
    document_id         INTEGER NOT NULL REFERENCES kb_documents(id) ON DELETE CASCADE,
    kb_id               INTEGER NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    chunk_index         INTEGER NOT NULL,
    content             TEXT NOT NULL,
    embedding           vector(1536),
    metadata_json       JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kb_class_assignments (
    id                  SERIAL PRIMARY KEY,
    kb_id               INTEGER NOT NULL REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    class_id            INTEGER NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    assigned_at         TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(kb_id, class_id)
);

-- Learning intelligence tables
CREATE TABLE IF NOT EXISTS student_mastery (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    subject             VARCHAR(255) NOT NULL,
    topic               VARCHAR(255) NOT NULL,
    standard_code       VARCHAR(50),
    mastery_level       SMALLINT DEFAULT 0,
    reasoning_quality   SMALLINT,
    last_assessed_at    TIMESTAMPTZ,
    UNIQUE(student_id, subject, topic)
);

CREATE TABLE IF NOT EXISTS misconception_log (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    subject             VARCHAR(255),
    topic               VARCHAR(255),
    misconception_type  VARCHAR(255),
    description         TEXT,
    detected_at         TIMESTAMPTZ DEFAULT NOW(),
    resolved_at         TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS mistake_journal (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    session_id          INTEGER REFERENCES tutor_sessions(id),
    question            TEXT NOT NULL,
    student_answer      TEXT,
    correct_answer      TEXT,
    misconception_id    INTEGER REFERENCES misconception_log(id),
    explanation_that_worked TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hint_progressions (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES tutor_users(id),
    session_id          INTEGER REFERENCES tutor_sessions(id) ON DELETE SET NULL,
    subject             VARCHAR(255),
    topic               VARCHAR(255),
    problem_text        TEXT NOT NULL,
    current_level       SMALLINT NOT NULL DEFAULT 1,
    status              VARCHAR(20) NOT NULL DEFAULT 'active',
    last_hint           TEXT,
    model_used          VARCHAR(100),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS adaptive_quiz_attempts (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES tutor_users(id),
    session_id          INTEGER REFERENCES tutor_sessions(id) ON DELETE SET NULL,
    subject             VARCHAR(255),
    topic               VARCHAR(255),
    prompt_context      TEXT,
    difficulty          SMALLINT NOT NULL DEFAULT 2,
    question_text       TEXT NOT NULL,
    options_json        JSONB,
    correct_answer      TEXT NOT NULL,
    explanation         TEXT,
    selected_answer     TEXT,
    is_correct          BOOLEAN,
    feedback            TEXT,
    status              VARCHAR(20) NOT NULL DEFAULT 'pending',
    model_used          VARCHAR(100),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    submitted_at        TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS concept_nodes (
    id                  SERIAL PRIMARY KEY,
    subject             VARCHAR(255) NOT NULL,
    topic               VARCHAR(255) NOT NULL,
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    grade_level         SMALLINT,
    prerequisites_json  JSONB,
    standard_codes_json JSONB
);

CREATE TABLE IF NOT EXISTS concept_edges (
    id                  SERIAL PRIMARY KEY,
    from_node_id        INTEGER NOT NULL REFERENCES concept_nodes(id),
    to_node_id          INTEGER NOT NULL REFERENCES concept_nodes(id),
    relationship_type   VARCHAR(50),
    weight              REAL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS career_topic_mappings (
    id                  SERIAL PRIMARY KEY,
    career              VARCHAR(255) NOT NULL,
    interest_tags       JSONB,
    topic_id            INTEGER REFERENCES concept_nodes(id),
    explanation         TEXT
);

-- Assessment tables
CREATE TABLE IF NOT EXISTS assessments (
    id                  SERIAL PRIMARY KEY,
    teacher_id          INTEGER REFERENCES tutor_users(id),
    title               VARCHAR(255) NOT NULL,
    type                VARCHAR(50),
    subject             VARCHAR(255),
    grade_level         SMALLINT,
    standards_json      JSONB,
    time_limit_minutes  INTEGER,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS assessment_questions (
    id                  SERIAL PRIMARY KEY,
    assessment_id       INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_type       VARCHAR(50),
    content             TEXT NOT NULL,
    options_json        JSONB,
    correct_answer      TEXT,
    explanation         TEXT,
    misconceptions_tested_json JSONB,
    sort_order          INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS assessment_attempts (
    id                  SERIAL PRIMARY KEY,
    assessment_id       INTEGER NOT NULL REFERENCES assessments(id),
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    score               REAL,
    answers_json        JSONB,
    started_at          TIMESTAMPTZ DEFAULT NOW(),
    completed_at        TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS teacher_reports (
    id                  SERIAL PRIMARY KEY,
    teacher_id          INTEGER NOT NULL REFERENCES tutor_users(id) ON DELETE CASCADE,
    class_id            INTEGER REFERENCES classes(id) ON DELETE SET NULL,
    student_id          INTEGER REFERENCES tutor_users(id) ON DELETE SET NULL,
    report_type         VARCHAR(50) NOT NULL,
    title               VARCHAR(255) NOT NULL,
    status              VARCHAR(20) NOT NULL DEFAULT 'draft',
    body_json           JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Gamification tables
CREATE TABLE IF NOT EXISTS student_xp (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id) UNIQUE,
    total_xp            INTEGER DEFAULT 0,
    level               VARCHAR(50) DEFAULT 'Learner',
    current_streak      INTEGER DEFAULT 0,
    longest_streak      INTEGER DEFAULT 0,
    last_activity_date  DATE,
    streak_freezes      INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS xp_transactions (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    amount              INTEGER NOT NULL,
    source_type         VARCHAR(50),
    source_id           INTEGER,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS badges (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    icon                VARCHAR(500),
    criteria_json       JSONB,
    category            VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS student_badges (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    badge_id            INTEGER NOT NULL REFERENCES badges(id),
    earned_at           TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_id, badge_id)
);

-- Flashcard tables
CREATE TABLE IF NOT EXISTS flashcard_decks (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    title               VARCHAR(255),
    subject             VARCHAR(255),
    topic               VARCHAR(255),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS flashcards (
    id                  SERIAL PRIMARY KEY,
    deck_id             INTEGER NOT NULL REFERENCES flashcard_decks(id) ON DELETE CASCADE,
    front               TEXT NOT NULL,
    back                TEXT NOT NULL,
    source_session_id   INTEGER REFERENCES tutor_sessions(id),
    next_review_at      TIMESTAMPTZ,
    ease_factor         REAL DEFAULT 2.5,
    interval            INTEGER DEFAULT 1,
    review_count        INTEGER DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Standards tables
CREATE TABLE IF NOT EXISTS standards_frameworks (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(255) NOT NULL,
    version             VARCHAR(50),
    country             VARCHAR(10) DEFAULT 'US',
    grades_range        VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS standards (
    id                  SERIAL PRIMARY KEY,
    framework_id        INTEGER NOT NULL REFERENCES standards_frameworks(id),
    parent_id           INTEGER REFERENCES standards(id),
    code                VARCHAR(100) NOT NULL,
    description         TEXT NOT NULL,
    grade_level         SMALLINT,
    subject             VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS content_standard_mappings (
    id                  SERIAL PRIMARY KEY,
    content_type        VARCHAR(50),
    content_id          INTEGER NOT NULL,
    standard_id         INTEGER NOT NULL REFERENCES standards(id)
);

-- Portfolio / analytics / restrictions tables
CREATE TABLE IF NOT EXISTS portfolio_items (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    item_type           VARCHAR(50),
    title               VARCHAR(255),
    content_json        JSONB,
    standards_json      JSONB,
    is_highlighted      BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS self_reflections (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    session_id          INTEGER REFERENCES tutor_sessions(id),
    prompt              TEXT,
    response            TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS session_analytics (
    id                  SERIAL PRIMARY KEY,
    session_id          INTEGER NOT NULL REFERENCES tutor_sessions(id),
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    duration_seconds    INTEGER,
    messages_count      INTEGER,
    hints_used          SMALLINT,
    mode_switches       SMALLINT,
    mastery_before      SMALLINT,
    mastery_after       SMALLINT,
    emotional_states_json JSONB
);

CREATE TABLE IF NOT EXISTS daily_analytics (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    date                DATE NOT NULL,
    sessions_count      INTEGER DEFAULT 0,
    total_duration      INTEGER DEFAULT 0,
    xp_earned           INTEGER DEFAULT 0,
    subjects_json       JSONB,
    interleaved_reviews INTEGER DEFAULT 0,
    UNIQUE(student_id, date)
);

CREATE TABLE IF NOT EXISTS notifications (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES tutor_users(id),
    type                VARCHAR(50),
    title               VARCHAR(255),
    body                TEXT,
    data_json           JSONB,
    read_at             TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS content_restrictions (
    id                  SERIAL PRIMARY KEY,
    parent_id           INTEGER NOT NULL REFERENCES tutor_users(id),
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    restriction_type    VARCHAR(50),
    restriction_value   JSONB,
    quiet_hours_json    JSONB
);

CREATE TABLE IF NOT EXISTS learning_paths (
    id                  SERIAL PRIMARY KEY,
    teacher_id          INTEGER REFERENCES tutor_users(id),
    title               VARCHAR(255) NOT NULL,
    subject             VARCHAR(255),
    grade_level         SMALLINT,
    standards_json      JSONB,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS learning_path_items (
    id                  SERIAL PRIMARY KEY,
    path_id             INTEGER NOT NULL REFERENCES learning_paths(id) ON DELETE CASCADE,
    item_type           VARCHAR(50),
    item_id             INTEGER,
    sort_order          INTEGER DEFAULT 0,
    prerequisite_item_id INTEGER REFERENCES learning_path_items(id)
);

CREATE TABLE IF NOT EXISTS student_interests (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES tutor_users(id),
    interest            VARCHAR(255) NOT NULL,
    used_for_analogies  BOOLEAN DEFAULT TRUE
);

-- Core indexes (idempotent)
CREATE INDEX IF NOT EXISTS idx_messages_session ON tutor_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON tutor_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_persona ON tutor_sessions(persona_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_bases_owner ON knowledge_bases(owner_id);
CREATE INDEX IF NOT EXISTS idx_kb_documents_kb ON kb_documents(kb_id);
CREATE INDEX IF NOT EXISTS idx_chunks_kb ON kb_chunks(kb_id);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON kb_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_classes_teacher ON classes(teacher_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_class ON class_enrollments(class_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_student ON class_enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_teacher_links_teacher ON teacher_student_links(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_links_student ON teacher_student_links(student_id);
CREATE INDEX IF NOT EXISTS idx_teacher_join_codes_teacher ON teacher_join_codes(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_join_requests_teacher ON teacher_join_requests(teacher_id, status);
CREATE INDEX IF NOT EXISTS idx_teacher_join_requests_student ON teacher_join_requests(student_id, status);
CREATE INDEX IF NOT EXISTS idx_tutor_sessions_class ON tutor_sessions(class_id);
CREATE INDEX IF NOT EXISTS idx_tutor_messages_kb ON tutor_messages(kb_id);
CREATE INDEX IF NOT EXISTS idx_mastery_student ON student_mastery(student_id);
CREATE INDEX IF NOT EXISTS idx_misconception_student ON misconception_log(student_id);
CREATE INDEX IF NOT EXISTS idx_hint_progressions_user ON hint_progressions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_hint_progressions_session ON hint_progressions(session_id);
CREATE INDEX IF NOT EXISTS idx_adaptive_quiz_user ON adaptive_quiz_attempts(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_adaptive_quiz_session ON adaptive_quiz_attempts(session_id);
CREATE INDEX IF NOT EXISTS idx_assessment_attempts_student ON assessment_attempts(student_id);
CREATE INDEX IF NOT EXISTS idx_teacher_reports_teacher ON teacher_reports(teacher_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_xp_transactions_student ON xp_transactions(student_id);
CREATE INDEX IF NOT EXISTS idx_flashcard_decks_student ON flashcard_decks(student_id);
CREATE INDEX IF NOT EXISTS idx_flashcards_deck ON flashcards(deck_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_analytics_student_date ON daily_analytics(student_id, date);
