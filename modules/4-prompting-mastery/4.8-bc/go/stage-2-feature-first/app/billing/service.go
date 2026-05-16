// Package billing — Billing feature: підписки.
package billing

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

func (s *Service) Subscribe(ctx context.Context, userID uuid.UUID, plan string) (*Subscription, error) {
	now := time.Now().UTC()
	sub := Subscription{
		ID:           uuid.New(),
		UserID:       userID,
		Plan:         plan,
		NextChargeAt: now.AddDate(0, 1, 0),
		CreatedAt:    now,
	}
	if err := s.repo.Create(ctx, sub); err != nil {
		return nil, err
	}
	return &sub, nil
}
