package catalog

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

func (r *Repository) List(ctx context.Context) ([]Product, error) {
	rows, err := r.db.Query(ctx,
		`SELECT id, name, price_cents, category_id FROM catalog_products ORDER BY name`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var out []Product
	for rows.Next() {
		var p Product
		if err := rows.Scan(&p.ID, &p.Name, &p.PriceCents, &p.CategoryID); err != nil {
			return nil, err
		}
		out = append(out, p)
	}
	return out, rows.Err()
}
