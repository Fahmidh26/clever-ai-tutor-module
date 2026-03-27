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
CREATE INDEX IF NOT EXISTS idx_messages_session ON tutor_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_tutor_messages_kb ON tutor_messages(kb_id);
