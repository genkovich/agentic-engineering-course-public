-- Rollback: drop all 8 tables created by the course-lesson-mvp feature.
-- Order is reverse of creation (child → parent) to respect FK constraints.

DROP TABLE IF EXISTS comment_audit;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS user_preference_audit;
DROP TABLE IF EXISTS user_preferences;
DROP TABLE IF EXISTS lesson_completions;
DROP TABLE IF EXISTS lesson_blocks;
DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS courses;
