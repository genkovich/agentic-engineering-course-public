-- Notifications BC. Лог надісланих сповіщень.
CREATE TABLE IF NOT EXISTS notifications_messages (
    id        UUID PRIMARY KEY,
    user_id   UUID NOT NULL,
    channel   VARCHAR(20) NOT NULL,
    payload   TEXT NOT NULL,
    sent_at   TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS notifications_messages_user_idx ON notifications_messages (user_id);
