-- Billing BC. Підписки.
CREATE TABLE IF NOT EXISTS billing_subscriptions (
    id              UUID PRIMARY KEY,
    user_id         UUID NOT NULL,
    plan            VARCHAR(50) NOT NULL,
    next_charge_at  TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS billing_subscriptions_user_idx ON billing_subscriptions (user_id);
