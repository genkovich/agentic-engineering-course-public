package billing

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

func (r *Repository) Create(ctx context.Context, s Subscription) error {
	_, err := r.db.Exec(ctx,
		`INSERT INTO billing_subscriptions (id, user_id, plan, next_charge_at, created_at)
		 VALUES ($1, $2, $3, $4, $5)`,
		s.ID, s.UserID, s.Plan, s.NextChargeAt, s.CreatedAt)
	return err
}
