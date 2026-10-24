-- 001_init.up.sql
-- Initial schema. UUID v7 IDs generated in application layer, not in DB.
-- No business defaults, no CHECK constraints, no triggers.

CREATE TABLE users (
    id          uuid PRIMARY KEY,
    email       VARCHAR(254) NOT NULL,
    first_name  VARCHAR(100),
    last_name   VARCHAR(100),
    role        VARCHAR(32)  NOT NULL,
    status      VARCHAR(32)  NOT NULL,
    created_at  timestamptz  NOT NULL DEFAULT now(),
    updated_at  timestamptz  NOT NULL DEFAULT now(),

    CONSTRAINT users_email_unique UNIQUE (email)
);

CREATE INDEX users_status_idx ON users (status);

CREATE TABLE sessions (
    id          uuid PRIMARY KEY,
    user_id     uuid NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    expires_at  timestamptz NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX sessions_user_id_idx ON sessions (user_id);
CREATE INDEX sessions_expires_at_idx ON sessions (expires_at);
