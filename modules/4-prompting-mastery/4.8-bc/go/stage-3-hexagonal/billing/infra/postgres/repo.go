package postgres

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/billing/domain"
)

type SubscriptionRepo struct {
	db *pgxpool.Pool
}

func NewSubscriptionRepo(db *pgxpool.Pool) *SubscriptionRepo {
	return &SubscriptionRepo{db: db}
}

func (r *SubscriptionRepo) Create(ctx context.Context, s domain.Subscription) error {
	_, err := r.db.Exec(ctx,
		`INSERT INTO billing_subscriptions (id, user_id, plan, next_charge_at, created_at)
		 VALUES ($1, $2, $3, $4, $5)`,
		s.ID, s.UserID, s.Plan, s.NextChargeAt, s.CreatedAt)
	return err
}
