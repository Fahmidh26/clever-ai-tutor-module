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
