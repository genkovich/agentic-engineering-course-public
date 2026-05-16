package service

import (
	"context"
	"log"
	"time"

	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/model"
)

type NotificationRepo interface {
	Create(ctx context.Context, n model.Notification) error
}

type NotificationService struct {
	repo NotificationRepo
}

func NewNotificationService(r NotificationRepo) *NotificationService {
	return &NotificationService{repo: r}
}

func (s *NotificationService) SendTest(ctx context.Context, userID uuid.UUID, channel, payload string) (*model.Notification, error) {
	now := time.Now().UTC()
	n := model.Notification{
		ID:      uuid.New(),
		UserID:  userID,
		Channel: channel,
		Payload: payload,
		SentAt:  &now,
	}

	log.Printf("[stub-sender] %s -> user=%s payload=%q", channel, userID, payload)

	if err := s.repo.Create(ctx, n); err != nil {
		return nil, err
	}
	return &n, nil
}
