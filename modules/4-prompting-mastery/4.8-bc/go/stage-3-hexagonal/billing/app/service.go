package app

import (
	"context"
	"time"

	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/billing/domain"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/events"
)

var validPlans = map[string]bool{"basic": true, "pro": true, "enterprise": true}

type Service struct {
	repo domain.Repository
	bus  *events.Bus
}

func New(repo domain.Repository, bus *events.Bus) *Service {
	return &Service{repo: repo, bus: bus}
}

func (s *Service) Subscribe(ctx context.Context, userID uuid.UUID, plan string) (*domain.Subscription, error) {
	if !validPlans[plan] {
		return nil, domain.ErrInvalidPlan
	}
	now := time.Now().UTC()
	sub := domain.Subscription{
		ID:           uuid.New(),
		UserID:       userID,
		Plan:         plan,
		NextChargeAt: now.AddDate(0, 1, 0),
		CreatedAt:    now,
	}
	if err := s.repo.Create(ctx, sub); err != nil {
		return nil, err
	}
	s.bus.Publish(ctx, domain.SubscriptionCreated{
		SubscriptionID: sub.ID,
		UserID:         sub.UserID,
		Plan:           sub.Plan,
		At:             sub.CreatedAt,
	})
	return &sub, nil
}
