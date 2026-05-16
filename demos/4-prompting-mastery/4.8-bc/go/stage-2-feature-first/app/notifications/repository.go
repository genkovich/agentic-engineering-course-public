package notifications

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"
)

type Repository struct {
	db *pgxpool.Pool
}

func NewRepository(db *pgxpool.Pool) *Repository {
	return &Repository{db: db}
}

func (r *Repository) Save(ctx context.Context, n Notification) error {
	_, err := r.db.Exec(ctx,
		`INSERT INTO notifications_messages (id, user_id, channel, payload, sent_at)
		 VALUES ($1, $2, $3, $4, $5)`,
		n.ID, n.UserID, n.Channel, n.Payload, n.SentAt)
	return err
}
