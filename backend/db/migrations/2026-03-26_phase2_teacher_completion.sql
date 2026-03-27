BEGIN;

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

CREATE INDEX IF NOT EXISTS idx_teacher_links_teacher ON teacher_student_links(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_links_student ON teacher_student_links(student_id);
CREATE INDEX IF NOT EXISTS idx_teacher_join_codes_teacher ON teacher_join_codes(teacher_id);
CREATE INDEX IF NOT EXISTS idx_teacher_join_requests_teacher ON teacher_join_requests(teacher_id, status);
CREATE INDEX IF NOT EXISTS idx_teacher_join_requests_student ON teacher_join_requests(student_id, status);
CREATE INDEX IF NOT EXISTS idx_teacher_reports_teacher ON teacher_reports(teacher_id, created_at DESC);

COMMIT;
