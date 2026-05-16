package postgres

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/catalog/domain"
)

type ProductRepo struct {
	db *pgxpool.Pool
}

func NewProductRepo(db *pgxpool.Pool) *ProductRepo {
	return &ProductRepo{db: db}
}

func (r *ProductRepo) List(ctx context.Context) ([]domain.Product, error) {
	rows, err := r.db.Query(ctx,
		`SELECT id, name, price_cents, category_id FROM catalog_products ORDER BY name`)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var out []domain.Product
	for rows.Next() {
		var p domain.Product
		if err := rows.Scan(&p.ID, &p.Name, &p.PriceCents, &p.CategoryID); err != nil {
			return nil, err
		}
		out = append(out, p)
	}
	return out, rows.Err()
}
