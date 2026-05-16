package catalog

import "github.com/google/uuid"

type Product struct {
	ID         uuid.UUID
	Name       string
	PriceCents int64
	CategoryID uuid.UUID
}
