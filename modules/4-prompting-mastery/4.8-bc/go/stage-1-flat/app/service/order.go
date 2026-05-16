package service

import (
	"context"
	"time"

	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/model"
)

type OrderRepo interface {
	Create(ctx context.Context, o model.Order) error
}

type OrderService struct {
	repo OrderRepo
}

func NewOrderService(r OrderRepo) *OrderService {
	return &OrderService{repo: r}
}

func (s *OrderService) Place(ctx context.Context, userID uuid.UUID, totalCents int64) (*model.Order, error) {
	o := model.Order{
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
