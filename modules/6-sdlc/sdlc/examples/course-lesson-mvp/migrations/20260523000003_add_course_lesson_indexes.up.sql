-- Staged migration: add composite query indexes for course-lesson-mvp hot paths
-- Promoted by sdlc-implement-tasks to live migrations tree with fresh timestamp.
-- Source: data-model.md §Indexes (rows marked "000022")
--
-- These indexes are separated from the table-creation migration so they can be
-- dropped and re-created independently (e.g., CONCURRENTLY in production).

-- US-03 publish-gate: SELECT COUNT(*) FROM lessons WHERE course_id=$1 AND status='published'
CREATE INDEX IF NOT EXISTS idx_lessons_course_status
    ON lessons (course_id, status);

-- US-08 peer-blob hot path: WHERE lesson_id=$1 AND org_id=$2
CREATE INDEX IF NOT EXISTS idx_lesson_completions_lesson_org
    ON lesson_completions (lesson_id, org_id);

-- GET /lessons/{id}/comments — paginated reverse-chronological
CREATE INDEX IF NOT EXISTS idx_comments_lesson_created
    ON comments (lesson_id, created_at DESC);
