-- Rollback: drop composite indexes added for course-lesson-mvp hot paths

DROP INDEX IF EXISTS idx_comments_lesson_created;
DROP INDEX IF EXISTS idx_lesson_completions_lesson_org;
DROP INDEX IF EXISTS idx_lessons_course_status;
