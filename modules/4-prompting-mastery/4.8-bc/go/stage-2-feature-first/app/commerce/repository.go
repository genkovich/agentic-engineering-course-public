package commerce

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

func (r *Repository) Create(ctx context.Context, o Order) error {
	_, err := r.db.Exec(ctx,
		`INSERT INTO commerce_orders (id, user_id, total_cents, status, created_at)
		 VALUES ($1, $2, $3, $4, $5)`,
		o.ID, o.UserID, o.TotalCents, o.Status, o.CreatedAt)
	return err
}
