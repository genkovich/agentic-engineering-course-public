// Package notifications — Notifications feature: відправка email/push.
package notifications

import (
	"context"
	"log"
	"time"

	"github.com/google/uuid"
)

type Service struct {
	repo *Repository
}

func NewService(repo *Repository) *Service {
	return &Service{repo: repo}
}

func (s *Service) Send(ctx context.Context, userID uuid.UUID, channel, payload string) (*Notification, error) {
	now := time.Now().UTC()
	n := Notification{
		ID:      uuid.New(),
		UserID:  userID,
		Channel: channel,
		Payload: payload,
		SentAt:  &now,
	}
	log.Printf("[stub-sender] %s -> user=%s payload=%q", channel, userID, payload)
	if err := s.repo.Save(ctx, n); err != nil {
		return nil, err
	}
	return &n, nil
}
