package billing

import (
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
