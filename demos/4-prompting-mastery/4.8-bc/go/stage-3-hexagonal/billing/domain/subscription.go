// Package domain — Billing Bounded Context.
package domain

import (
	"context"
	"errors"
	"time"

	"github.com/google/uuid"
)

type Subscription struct {
	ID           uuid.UUID
	UserID       uuid.UUID
	Plan         string
	NextChargeAt time.Time
	CreatedAt    time.Time
}

type Repository interface {
	Create(ctx context.Context, s Subscription) error
}

var ErrInvalidPlan = errors.New("billing.invalid_plan")

// SubscriptionCreated — Notifications підписується для welcome-letter.
type SubscriptionCreated struct {
	SubscriptionID uuid.UUID
	UserID         uuid.UUID
	Plan           string
	At             time.Time
}

func (SubscriptionCreated) Name() string { return "billing.SubscriptionCreated" }
