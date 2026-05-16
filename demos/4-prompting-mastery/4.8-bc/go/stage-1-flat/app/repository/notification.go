package repository

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/model"
)

type NotificationRepo struct {
	db *pgxpool.Pool
}

func NewNotificationRepo(db *pgxpool.Pool) *NotificationRepo {
	return &NotificationRepo{db: db}
}

func (r *NotificationRepo) Create(ctx context.Context, n model.Notification) error {
	_, err := r.db.Exec(ctx,
		`INSERT INTO notifications (id, user_id, channel, payload, sent_at)
		 VALUES ($1, $2, $3, $4, $5)`,
		n.ID, n.UserID, n.Channel, n.Payload, n.SentAt)
	return err
}
