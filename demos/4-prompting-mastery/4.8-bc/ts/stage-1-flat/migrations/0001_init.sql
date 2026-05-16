-- All tables in one schema. BC не виражений у структурі — це stage-1-flat.

CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY,
    email           VARCHAR(254) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS categories (
    id   UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    id          UUID PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    price_cents BIGINT NOT NULL CHECK (price_cents >= 0),
    category_id UUID NOT NULL REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id          UUID PRIMARY KEY,
    user_id     UUID NOT NULL REFERENCES users(id),
    total_cents BIGINT NOT NULL CHECK (total_cents >= 0),
    status      VARCHAR(20) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id              UUID PRIMARY KEY,
    user_id         UUID NOT NULL REFERENCES users(id),
    plan            VARCHAR(50) NOT NULL,
    next_charge_at  TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS notifications (
    id        UUID PRIMARY KEY,
    user_id   UUID NOT NULL REFERENCES users(id),
    channel   VARCHAR(20) NOT NULL,
    payload   TEXT NOT NULL,
    sent_at   TIMESTAMPTZ
);

INSERT INTO categories (id, name) VALUES
    ('11111111-1111-1111-1111-111111111111', 'Books'),
    ('22222222-2222-2222-2222-222222222222', 'Electronics')
ON CONFLICT DO NOTHING;

INSERT INTO products (id, name, price_cents, category_id) VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'A Philosophy of Software Design', 4500, '11111111-1111-1111-1111-111111111111'),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Domain-Driven Design', 6500, '11111111-1111-1111-1111-111111111111'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'Mechanical Keyboard', 18900, '22222222-2222-2222-2222-222222222222')
ON CONFLICT DO NOTHING;
