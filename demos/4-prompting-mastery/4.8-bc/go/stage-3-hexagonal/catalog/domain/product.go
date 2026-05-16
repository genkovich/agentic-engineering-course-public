// Package domain — Catalog Bounded Context.
package domain

import (
	"context"

	"github.com/google/uuid"
)

type Product struct {
	ID         uuid.UUID
	Name       string
	PriceCents int64
	CategoryID uuid.UUID
}

type Repository interface {
	List(ctx context.Context) ([]Product, error)
}
