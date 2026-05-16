-- Commerce BC. Замовлення.
-- Reference на user_id — тільки UUID, не FK на auth_users (BC ізоляція).
CREATE TABLE IF NOT EXISTS commerce_orders (
    id          UUID PRIMARY KEY,
    user_id     UUID NOT NULL,
    total_cents BIGINT NOT NULL CHECK (total_cents >= 0),
    status      VARCHAR(20) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS commerce_orders_user_idx ON commerce_orders (user_id);
