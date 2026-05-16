package domain

import (
	"context"

	"github.com/google/uuid"
)

// UserRepository — port. Реалізація живе в auth/infra/postgres.
type UserRepository interface {
	Create(ctx context.Context, u User) error
	FindByEmail(ctx context.Context, email string) (*User, error)
	FindByID(ctx context.Context, id uuid.UUID) (*User, error)
}
