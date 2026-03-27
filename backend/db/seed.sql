-- AI Tutor baseline seed data (Phase 1.1.13)
-- Idempotent inserts for personas, subjects/topics, and standards.

BEGIN;

-- Default tutor roster personas
INSERT INTO tutor_personas (
    slug,
    name,
    tagline,
    personality,
    system_prompt,
    teaching_style,
    subject_expertise,
    is_custom,
    is_active,
    sort_order
)
SELECT
    v.slug,
    v.name,
    v.tagline,
    v.personality,
    v.system_prompt,
    v.teaching_style,
    v.subject_expertise::jsonb,
    FALSE,
    TRUE,
    v.sort_order
FROM (
    VALUES
        (
            'sofia',
            'Sofia',
            'The patient explainer',
            'Patient, encouraging, nurturing',
            'You are Sofia, a warm tutor. Teach step-by-step, celebrate progress, and keep explanations age-appropriate.',
            'step-by-step',
            '["math","science"]',
            1
        ),
        (
            'marcus',
            'Marcus',
            'The Socratic challenger',
            'Socratic, deep, challenging',
            'You are Marcus, a Socratic tutor. Ask guiding questions first, then scaffold toward the answer.',
            'socratic',
            '["philosophy","history","literature"]',
            2
        ),
        (
            'aiko',
            'Aiko',
            'The creative coach',
            'Playful, creative, energetic',
            'You are Aiko, a creative tutor. Use stories, analogies, and light humor to keep learning engaging.',
            'peer',
            '["languages","arts"]',
            3
        ),
        (
            'reza',
            'Reza',
            'The rigorous mentor',
            'Direct, rigorous, no-nonsense',
            'You are Reza, a precise tutor. Use worked examples, verify each step, and require clear reasoning.',
            'direct',
            '["math","science","coding"]',
            4
        ),
        (
            'dr-chen',
            'Dr. Chen',
            'The formal scientist',
            'Methodical, thorough, formal',
            'You are Dr. Chen, a formal academic tutor. Teach from first principles with clear notation and definitions.',
            'direct',
            '["science","research","math"]',
            5
        ),
        (
            'alex',
            'Alex',
            'The study buddy',
            'Peer-like, collaborative, casual',
            'You are Alex, a collaborative tutor. Keep tone friendly and practical, and co-solve with the learner.',
            'peer',
            '["math","science","history","ela","coding"]',
            6
        )
) AS v(slug, name, tagline, personality, system_prompt, teaching_style, subject_expertise, sort_order)
ON CONFLICT (slug) DO UPDATE
SET
    name = EXCLUDED.name,
    tagline = EXCLUDED.tagline,
    personality = EXCLUDED.personality,
    system_prompt = EXCLUDED.system_prompt,
    teaching_style = EXCLUDED.teaching_style,
    subject_expertise = EXCLUDED.subject_expertise,
    is_active = TRUE,
    updated_at = NOW();

-- Standards frameworks
INSERT INTO standards_frameworks (name, version, country, grades_range)
SELECT 'Common Core State Standards', '1.0', 'US', 'K-12'
WHERE NOT EXISTS (
    SELECT 1 FROM standards_frameworks WHERE name = 'Common Core State Standards'
);

INSERT INTO standards_frameworks (name, version, country, grades_range)
SELECT 'Next Generation Science Standards', '1.0', 'US', 'K-12'
WHERE NOT EXISTS (
    SELECT 1 FROM standards_frameworks WHERE name = 'Next Generation Science Standards'
);

-- Baseline standards rows (starter subset)
INSERT INTO standards (framework_id, code, description, grade_level, subject)
SELECT sf.id, s.code, s.description, s.grade_level, s.subject
FROM standards_frameworks sf
JOIN (
    VALUES
        ('Common Core State Standards', 'CCSS.MATH.CONTENT.8.EE.A.1', 'Know and apply the properties of integer exponents to generate equivalent numerical expressions.', 8, 'Math'),
        ('Common Core State Standards', 'CCSS.MATH.CONTENT.HSA.CED.A.1', 'Create equations and inequalities in one variable and use them to solve problems.', 9, 'Math'),
        ('Common Core State Standards', 'CCSS.ELA-LITERACY.RI.6.1', 'Cite textual evidence to support analysis of what the text says explicitly and inferences.', 6, 'ELA'),
        ('Common Core State Standards', 'CCSS.ELA-LITERACY.W.7.1', 'Write arguments to support claims with clear reasons and relevant evidence.', 7, 'ELA'),
        ('Next Generation Science Standards', 'MS-PS2-2', 'Plan an investigation to provide evidence that change in an object motion depends on force and mass.', 8, 'Science'),
        ('Next Generation Science Standards', 'HS-LS1-5', 'Use a model to illustrate how photosynthesis transforms light energy into stored chemical energy.', 10, 'Science'),
        ('Next Generation Science Standards', 'MS-ESS2-1', 'Develop a model to describe cycling of Earth materials and flow of energy that drives this process.', 7, 'Science')
) AS s(framework_name, code, description, grade_level, subject)
    ON sf.name = s.framework_name
WHERE NOT EXISTS (
    SELECT 1 FROM standards existing WHERE existing.code = s.code
);

-- Subject/topic seed using concept nodes
INSERT INTO concept_nodes (subject, topic, name, description, grade_level, prerequisites_json, standard_codes_json)
SELECT
    c.subject,
    c.topic,
    c.name,
    c.description,
    c.grade_level,
    c.prerequisites_json::jsonb,
    c.standard_codes_json::jsonb
FROM (
    VALUES
        ('Math', 'Algebra', 'Linear Equations', 'Solve and model one-variable linear equations.', 8, '["integer_arithmetic"]', '["CCSS.MATH.CONTENT.8.EE.A.1"]'),
        ('Math', 'Algebra', 'Quadratic Functions', 'Understand and analyze quadratic expressions and graphs.', 9, '["linear_equations"]', '["CCSS.MATH.CONTENT.HSA.CED.A.1"]'),
        ('Science', 'Physics', 'Forces and Motion', 'Explore relationship between force, mass, and acceleration.', 8, '["measurement_basics"]', '["MS-PS2-2"]'),
        ('Science', 'Biology', 'Photosynthesis', 'Understand light-energy conversion in plants.', 10, '["cell_structure"]', '["HS-LS1-5"]'),
        ('Science', 'Earth Science', 'Earth Systems', 'Model Earth material cycles and energy transfer.', 7, '["matter_and_energy"]', '["MS-ESS2-1"]'),
        ('ELA', 'Reading', 'Evidence-Based Analysis', 'Use textual evidence to support claims and inferences.', 6, '["reading_comprehension"]', '["CCSS.ELA-LITERACY.RI.6.1"]'),
        ('ELA', 'Writing', 'Argument Writing', 'Write claims supported by relevant evidence.', 7, '["evidence_based_analysis"]', '["CCSS.ELA-LITERACY.W.7.1"]'),
        ('Coding', 'Programming Fundamentals', 'Variables and Control Flow', 'Use variables, conditionals, and loops in beginner programs.', 7, '["logic_basics"]', '[]')
) AS c(subject, topic, name, description, grade_level, prerequisites_json, standard_codes_json)
WHERE NOT EXISTS (
    SELECT 1
    FROM concept_nodes existing
    WHERE existing.subject = c.subject
      AND existing.topic = c.topic
      AND existing.name = c.name
      AND existing.grade_level = c.grade_level
);

COMMIT;

BEGIN;

INSERT INTO tutor_users (root_user_id, role, display_name, grade_level, preferred_language)
SELECT v.root_user_id, v.role, v.display_name, v.grade_level, 'en'
FROM (
    VALUES
        (101, 'student', 'Student Demo', 8),
        (102, 'teacher', 'Teacher Demo', NULL),
        (104, 'admin', 'Admin Demo', NULL),
        (201, 'student', 'Ava Newton', 8),
        (202, 'student', 'Leo Faraday', 8)
) AS v(root_user_id, role, display_name, grade_level)
WHERE NOT EXISTS (
    SELECT 1 FROM tutor_users u WHERE u.root_user_id = v.root_user_id
);

INSERT INTO classes (teacher_id, name, subject, grade_level, invite_code, persona_id, settings_json)
SELECT t.id, 'Grade 8 Physics A', 'Physics', 8, 'PHY8A', p.id, '{"teacher_persona_overlay":"Use evidence-based explanations, then finish each response with one retrieval check."}'::jsonb
FROM tutor_users t
JOIN tutor_personas p ON p.slug = 'reza'
WHERE t.root_user_id = 102
  AND NOT EXISTS (
      SELECT 1
      FROM classes c
      WHERE c.teacher_id = t.id
        AND c.name = 'Grade 8 Physics A'
  );

INSERT INTO teacher_student_links (teacher_id, student_id, status, source, notes_json)
SELECT teacher.id, student.id, 'active', 'seed', '{}'::jsonb
FROM tutor_users teacher
JOIN tutor_users student ON student.root_user_id IN (101, 201, 202)
WHERE teacher.root_user_id = 102
  AND NOT EXISTS (
      SELECT 1
      FROM teacher_student_links l
      WHERE l.teacher_id = teacher.id
        AND l.student_id = student.id
  );

INSERT INTO class_enrollments (class_id, student_id, status)
SELECT c.id, s.id, 'active'
FROM classes c
JOIN tutor_users teacher ON teacher.id = c.teacher_id AND teacher.root_user_id = 102
JOIN tutor_users s ON s.root_user_id IN (101, 201)
WHERE c.name = 'Grade 8 Physics A'
  AND NOT EXISTS (
      SELECT 1
      FROM class_enrollments e
      WHERE e.class_id = c.id
        AND e.student_id = s.id
  );

INSERT INTO teacher_join_codes (teacher_id, code, status, expires_at, metadata_json)
SELECT t.id, 'TEACHPHY8', 'active', NOW() + INTERVAL '30 days', '{}'::jsonb
FROM tutor_users t
WHERE t.root_user_id = 102
  AND NOT EXISTS (
      SELECT 1
      FROM teacher_join_codes jc
      WHERE jc.teacher_id = t.id
        AND jc.code = 'TEACHPHY8'
  );

INSERT INTO teacher_join_requests (teacher_id, student_id, join_code_id, class_id, status, request_message)
SELECT teacher.id, student.id, code.id, c.id, 'pending', 'I would like to join the physics class.'
FROM tutor_users teacher
JOIN tutor_users student ON student.root_user_id = 202
JOIN teacher_join_codes code ON code.teacher_id = teacher.id AND code.code = 'TEACHPHY8'
JOIN classes c ON c.teacher_id = teacher.id AND c.name = 'Grade 8 Physics A'
WHERE teacher.root_user_id = 102
  AND NOT EXISTS (
      SELECT 1
      FROM teacher_join_requests r
      WHERE r.teacher_id = teacher.id
        AND r.student_id = student.id
        AND r.class_id = c.id
  );

INSERT INTO knowledge_bases (owner_id, name, description, subject, grade_level, visibility, status)
SELECT t.id, 'Newton Laws Unit', 'Class notes and worked examples for motion and force.', 'Physics', 8, 'class', 'active'
FROM tutor_users t
WHERE t.root_user_id = 102
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_bases kb WHERE kb.owner_id = t.id AND kb.name = 'Newton Laws Unit'
  );

INSERT INTO kb_class_assignments (kb_id, class_id)
SELECT kb.id, c.id
FROM knowledge_bases kb
JOIN tutor_users t ON t.id = kb.owner_id AND t.root_user_id = 102
JOIN classes c ON c.teacher_id = t.id AND c.name = 'Grade 8 Physics A'
WHERE kb.name = 'Newton Laws Unit'
  AND NOT EXISTS (
      SELECT 1 FROM kb_class_assignments a WHERE a.kb_id = kb.id AND a.class_id = c.id
  );

INSERT INTO student_mastery (student_id, subject, topic, mastery_level, reasoning_quality, last_assessed_at)
SELECT s.id, 'Physics', v.topic, v.mastery_level, v.reasoning_quality, NOW()
FROM tutor_users s
JOIN (
    VALUES
        (101, 'Newton''s 2nd Law', 2, 2),
        (101, 'Free-Body Diagrams', 3, 3),
        (201, 'Newton''s 2nd Law', 4, 4),
        (201, 'Momentum', 3, 3),
        (202, 'Force And Motion', 1, 2)
) AS v(root_user_id, topic, mastery_level, reasoning_quality)
    ON v.root_user_id = s.root_user_id
WHERE NOT EXISTS (
    SELECT 1 FROM student_mastery sm WHERE sm.student_id = s.id AND sm.subject = 'Physics' AND sm.topic = v.topic
);

INSERT INTO misconception_log (student_id, subject, topic, misconception_type, description, detected_at)
SELECT s.id, 'Physics', v.topic, v.kind, v.description, NOW()
FROM tutor_users s
JOIN (
    VALUES
        (101, 'Newton''s 2nd Law', 'formula-confusion', 'Confuses force with mass when rearranging F = ma.'),
        (202, 'Force And Motion', 'directionality', 'Treats velocity and acceleration as always pointing in the same direction.')
) AS v(root_user_id, topic, kind, description)
    ON v.root_user_id = s.root_user_id
WHERE NOT EXISTS (
    SELECT 1 FROM misconception_log m WHERE m.student_id = s.id AND m.topic = v.topic AND m.misconception_type = v.kind
);

INSERT INTO adaptive_quiz_attempts (user_id, subject, topic, difficulty, question_text, correct_answer, selected_answer, is_correct, status, submitted_at)
SELECT s.id, 'Physics', v.topic, 2, v.question_text, v.correct_answer, v.selected_answer, v.is_correct, 'graded', NOW()
FROM tutor_users s
JOIN (
    VALUES
        (101, 'Newton''s 2nd Law', 'What happens to acceleration if force doubles and mass stays the same?', 'It doubles', 'It stays the same', FALSE),
        (101, 'Free-Body Diagrams', 'A balanced force diagram shows what net force?', 'Zero', 'Zero', TRUE),
        (201, 'Momentum', 'Momentum depends on mass and what else?', 'Velocity', 'Velocity', TRUE)
    ) AS v(root_user_id, topic, question_text, correct_answer, selected_answer, is_correct)
    ON v.root_user_id = s.root_user_id
WHERE NOT EXISTS (
    SELECT 1
    FROM adaptive_quiz_attempts q
    WHERE q.user_id = s.id
      AND q.topic = v.topic
      AND q.question_text = v.question_text
);

INSERT INTO tutor_sessions (user_id, persona_id, class_id, subject, topic, mode, status, tokens_used, model_used, started_at)
SELECT s.id, p.id, c.id, 'Physics', v.topic, 'teach_me', 'completed', v.tokens_used, 'gpt-4o-mini', NOW() - v.offset_interval
FROM tutor_users s
JOIN (
    VALUES
        (101, 'Newton''s 2nd Law', 10, INTERVAL '2 days'),
        (201, 'Momentum', 14, INTERVAL '1 day')
    ) AS v(root_user_id, topic, tokens_used, offset_interval)
    ON v.root_user_id = s.root_user_id
JOIN tutor_personas p ON p.slug = 'reza'
JOIN tutor_users teacher ON teacher.root_user_id = 102
JOIN classes c ON c.teacher_id = teacher.id AND c.name = 'Grade 8 Physics A'
WHERE NOT EXISTS (
    SELECT 1
    FROM tutor_sessions ts
    WHERE ts.user_id = s.id
      AND ts.class_id = c.id
      AND ts.topic = v.topic
);

INSERT INTO tutor_messages (session_id, kb_id, role, content, mode, tokens_used, model_used, created_at)
SELECT ts.id, kb.id, v.role, v.content, 'chat', 40, 'gpt-4o-mini', NOW()
FROM tutor_sessions ts
JOIN tutor_users s ON s.id = ts.user_id
JOIN knowledge_bases kb ON kb.name = 'Newton Laws Unit'
JOIN (
    VALUES
        ('user', 'I do not understand why acceleration changes when force changes.'),
        ('assistant', 'Start with F = ma. If mass stays fixed and force gets bigger, acceleration must also get bigger.')
    ) AS v(role, content) ON TRUE
WHERE s.root_user_id = 101
  AND ts.topic = 'Newton''s 2nd Law'
  AND NOT EXISTS (
      SELECT 1 FROM tutor_messages m WHERE m.session_id = ts.id AND m.content = v.content
  );

INSERT INTO assessments (teacher_id, title, type, subject, grade_level, standards_json, time_limit_minutes)
SELECT t.id, 'Physics Checkpoint 1', 'quiz', 'Physics', 8, '[]'::jsonb, 15
FROM tutor_users t
WHERE t.root_user_id = 102
  AND NOT EXISTS (
      SELECT 1 FROM assessments a WHERE a.teacher_id = t.id AND a.title = 'Physics Checkpoint 1'
  );

INSERT INTO assessment_questions (assessment_id, question_type, content, correct_answer, sort_order)
SELECT a.id, 'short-answer', 'Explain what it means when net force equals zero.', 'The forces are balanced so acceleration is zero.', 1
FROM assessments a
JOIN tutor_users t ON t.id = a.teacher_id AND t.root_user_id = 102
WHERE a.title = 'Physics Checkpoint 1'
  AND NOT EXISTS (
      SELECT 1 FROM assessment_questions q WHERE q.assessment_id = a.id AND q.content = 'Explain what it means when net force equals zero.'
  );

INSERT INTO teacher_reports (teacher_id, class_id, student_id, report_type, title, status, body_json)
SELECT t.id, c.id, s.id, 'summary', 'Physics Progress Draft', 'draft',
       '{"suggestions":["Review force-mass-acceleration relationships with one worked example.","Ask the student to narrate each step before solving independently."]}'::jsonb
FROM tutor_users t
JOIN classes c ON c.teacher_id = t.id AND c.name = 'Grade 8 Physics A'
JOIN tutor_users s ON s.root_user_id = 101
WHERE t.root_user_id = 102
  AND NOT EXISTS (
      SELECT 1 FROM teacher_reports r WHERE r.teacher_id = t.id AND r.title = 'Physics Progress Draft'
  );

COMMIT;
