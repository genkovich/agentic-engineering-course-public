-- Staged migration: create all 8 new tables for course-lesson-mvp
-- Promoted by sdlc-implement-tasks to live migrations tree with fresh timestamp.
-- Source: data-model.md §Entities (courses, lessons, lesson_blocks,
--         lesson_completions, user_preferences, user_preference_audit,
--         comments, comment_audit)
--
-- DB conventions (course SDLC toolkit — not sdd stack-agnostic):
--   audit cols    = created_at only (immutable-first; event/audit tables have no updated_at)
--   hard delete   = no deleted_at or is_deleted columns
--   no CHECK      = CHECK constraints deliberately absent (DB as dumb storage;
--                   business validation lives in app layer per PRD §6.1)
--   no TRIGGER    = no triggers
--   no business DEFAULT = only DEFAULT now() for timestamp columns
--   UUID v7       = generated app-side; DB receives the value, never generates it

-- ─── courses ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS courses (
    id               UUID         NOT NULL,
    org_id           UUID         NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    course_owner_id  UUID         NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title            VARCHAR(200) NOT NULL,
    description      VARCHAR(500),
    cover_image_url  TEXT,
    status           VARCHAR(20)  NOT NULL,
    published_at     TIMESTAMPTZ,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT courses_pkey PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_courses_org_id
    ON courses (org_id);

CREATE INDEX IF NOT EXISTS idx_courses_course_owner_id
    ON courses (course_owner_id);

-- ─── lessons ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS lessons (
    id               UUID         NOT NULL,
    course_id        UUID         NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    sequence         INT          NOT NULL,
    title            VARCHAR(200) NOT NULL,
    status           VARCHAR(20)  NOT NULL,
    duration_seconds INT,
    published_at     TIMESTAMPTZ,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT lessons_pkey PRIMARY KEY (id),
    CONSTRAINT lessons_course_sequence_unique UNIQUE (course_id, sequence)
);

-- ─── lesson_blocks ──────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS lesson_blocks (
    id          UUID         NOT NULL,
    lesson_id   UUID         NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    sequence    INT          NOT NULL,
    block_type  VARCHAR(20)  NOT NULL,
    payload     JSONB        NOT NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT lesson_blocks_pkey PRIMARY KEY (id),
    CONSTRAINT lesson_blocks_lesson_sequence_unique UNIQUE (lesson_id, sequence)
);

-- ─── lesson_completions ─────────────────────────────────────────────────────
-- Event-log: immutable after insert (no updated_at).

CREATE TABLE IF NOT EXISTS lesson_completions (
    id           UUID        NOT NULL,
    user_id      UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lesson_id    UUID        NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    org_id       UUID        NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT lesson_completions_pkey PRIMARY KEY (id),
    CONSTRAINT lesson_completions_user_lesson_unique UNIQUE (user_id, lesson_id)
);

CREATE INDEX IF NOT EXISTS idx_lesson_completions_org_id
    ON lesson_completions (org_id);

-- ─── user_preferences ───────────────────────────────────────────────────────
-- Singleton per user: PK = FK (no surrogate id).

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id        UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    peer_visibility VARCHAR(20) NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT user_preferences_pkey PRIMARY KEY (user_id)
);

-- ─── user_preference_audit ──────────────────────────────────────────────────
-- Immutable audit log: no updated_at.

CREATE TABLE IF NOT EXISTS user_preference_audit (
    id         UUID         NOT NULL,
    user_id    UUID         NOT NULL REFERENCES user_preferences(user_id) ON DELETE CASCADE,
    field      VARCHAR(64)  NOT NULL,
    old_value  VARCHAR(255),
    new_value  VARCHAR(255) NOT NULL,
    changed_at TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT user_preference_audit_pkey PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_user_preference_audit_user_id
    ON user_preference_audit (user_id);

-- ─── comments ───────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS comments (
    id         UUID        NOT NULL,
    lesson_id  UUID        NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    author_id  UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content    TEXT        NOT NULL,
    status     VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT comments_pkey PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_comments_author_id
    ON comments (author_id);

-- ─── comment_audit ──────────────────────────────────────────────────────────
-- Immutable moderation log: no updated_at.

CREATE TABLE IF NOT EXISTS comment_audit (
    id               UUID        NOT NULL,
    comment_id       UUID        NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
    moderator_id     UUID        NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    action           VARCHAR(20) NOT NULL,
    original_content TEXT        NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT comment_audit_pkey PRIMARY KEY (id)
);

CREATE INDEX IF NOT EXISTS idx_comment_audit_comment_id
    ON comment_audit (comment_id);

CREATE INDEX IF NOT EXISTS idx_comment_audit_moderator_id
    ON comment_audit (moderator_id);
