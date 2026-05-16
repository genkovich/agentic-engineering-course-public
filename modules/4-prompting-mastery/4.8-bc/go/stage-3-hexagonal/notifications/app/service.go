package app

import (
	"context"
	"time"

	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/notifications/domain"
)

type Service struct {
	repo   domain.Repository
	sender domain.Sender
}

func New(repo domain.Repository, sender domain.Sender) *Service {
	return &Service{repo: repo, sender: sender}
}

// Send — головний use case. Створює notification, шле через Sender, зберігає у БД.
// Викликається і HTTP handler-ом, і event subscriber-ами.
func (s *Service) Send(ctx context.Context, userID uuid.UUID, channel domain.Channel, payload string) (*domain.Notification, error) {
	n := domain.Notification{
		ID:      uuid.New(),
		UserID:  userID,
		Channel: channel,
		Payload: payload,
	}
	if err := s.sender.Send(ctx, n); err != nil {
		return nil, err
	}
	now := time.Now().UTC()
	n.SentAt = &now
	if err := s.repo.Save(ctx, n); err != nil {
		return nil, err
	}
	return &n, nil
}
