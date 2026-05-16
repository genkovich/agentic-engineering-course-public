// Package domain — Commerce Bounded Context.
package domain

import (
	"context"
	"errors"
	"time"

	"github.com/google/uuid"
)

type Order struct {
	ID         uuid.UUID
	UserID     uuid.UUID
	TotalCents int64
	Status     string
	CreatedAt  time.Time
}

type Repository interface {
	Create(ctx context.Context, o Order) error
}

var ErrInvalidOrder = errors.New("commerce.invalid_order")

// OrderPlaced — domain event. Billing and Notifications BCs підписуються.
type OrderPlaced struct {
	OrderID    uuid.UUID
	UserID     uuid.UUID
	TotalCents int64
	At         time.Time
}

func (OrderPlaced) Name() string { return "commerce.OrderPlaced" }
