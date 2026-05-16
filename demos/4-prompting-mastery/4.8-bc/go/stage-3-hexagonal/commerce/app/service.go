package app

import (
	"context"
	"time"

	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/commerce/domain"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/events"
)

type Service struct {
	repo domain.Repository
	bus  *events.Bus
}

func New(repo domain.Repository, bus *events.Bus) *Service {
	return &Service{repo: repo, bus: bus}
}

func (s *Service) Place(ctx context.Context, userID uuid.UUID, totalCents int64) (*domain.Order, error) {
	if totalCents < 0 {
		return nil, domain.ErrInvalidOrder
	}
	o := domain.Order{
		ID:         uuid.New(),
		UserID:     userID,
		TotalCents: totalCents,
		Status:     "pending",
		CreatedAt:  time.Now().UTC(),
	}
	if err := s.repo.Create(ctx, o); err != nil {
		return nil, err
	}
	s.bus.Publish(ctx, domain.OrderPlaced{OrderID: o.ID, UserID: o.UserID, TotalCents: o.TotalCents, At: o.CreatedAt})
	return &o, nil
}
