package service

import (
	"context"
	"time"

	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/model"
)

type SubscriptionRepo interface {
	Create(ctx context.Context, s model.Subscription) error
}

type SubscriptionService struct {
	repo SubscriptionRepo
}

func NewSubscriptionService(r SubscriptionRepo) *SubscriptionService {
	return &SubscriptionService{repo: r}
}

func (s *SubscriptionService) Subscribe(ctx context.Context, userID uuid.UUID, plan string) (*model.Subscription, error) {
	now := time.Now().UTC()
	sub := model.Subscription{
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
