// Package commerce — Commerce feature: замовлення.
package commerce

import (
	"context"
	"time"

	"github.com/google/uuid"
)

type Service struct {
	repo *Repository
}

func NewService(repo *Repository) *Service {
	return &Service{repo: repo}
}

func (s *Service) Place(ctx context.Context, userID uuid.UUID, totalCents int64) (*Order, error) {
	o := Order{
		ID:         uuid.New(),
		UserID:     userID,
		TotalCents: totalCents,
		Status:     "pending",
		CreatedAt:  time.Now().UTC(),
	}
	if err := s.repo.Create(ctx, o); err != nil {
		return nil, err
	}
	return &o, nil
}
