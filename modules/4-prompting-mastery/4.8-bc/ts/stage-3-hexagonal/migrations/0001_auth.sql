-- Auth BC. Префікс auth_ робить BC-власника явним у спільній БД.
CREATE TABLE IF NOT EXISTS auth_users (
    id              UUID PRIMARY KEY,
    email           VARCHAR(254) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS auth_users_email_idx ON auth_users (email);
