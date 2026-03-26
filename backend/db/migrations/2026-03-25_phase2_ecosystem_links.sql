ALTER TABLE IF EXISTS tutor_sessions
ADD COLUMN IF NOT EXISTS class_id INTEGER REFERENCES classes(id) ON DELETE SET NULL;

ALTER TABLE IF EXISTS tutor_messages
ADD COLUMN IF NOT EXISTS kb_id INTEGER REFERENCES knowledge_bases(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_tutor_sessions_class ON tutor_sessions(class_id);
CREATE INDEX IF NOT EXISTS idx_tutor_messages_kb ON tutor_messages(kb_id);
