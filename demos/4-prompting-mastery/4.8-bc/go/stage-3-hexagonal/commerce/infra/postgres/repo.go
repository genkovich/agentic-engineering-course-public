package postgres

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/commerce/domain"
)

type OrderRepo struct {
	db *pgxpool.Pool
}

func NewOrderRepo(db *pgxpool.Pool) *OrderRepo {
	return &OrderRepo{db: db}
}

func (r *OrderRepo) Create(ctx context.Context, o domain.Order) error {
	_, err := r.db.Exec(ctx,
		`INSERT INTO commerce_orders (id, user_id, total_cents, status, created_at)
		 VALUES ($1, $2, $3, $4, $5)`,
		o.ID, o.UserID, o.TotalCents, o.Status, o.CreatedAt)
	return err
}
