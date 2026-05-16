-- db/migrations/0001_initial.sql
-- Hard Rule: DO NOT change. Незворотна зміна — одна помилка ламає прод-схему,
-- відкат вимагає окремої міграції-зворот. Якщо потрібно поміняти схему —
-- нова міграція 0002_*.sql, не редагування 0001.

CREATE TABLE users (
    id           UUID PRIMARY KEY,
    email        VARCHAR(254) NOT NULL UNIQUE,
    password     VARCHAR(72)  NOT NULL,                -- bcrypt hash
    status       VARCHAR(16)  NOT NULL DEFAULT 'pending',
    verify_token VARCHAR(64),
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_verify_token ON users(verify_token);
