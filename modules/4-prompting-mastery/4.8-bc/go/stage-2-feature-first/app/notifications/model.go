package notifications

import (
	"time"

	"github.com/google/uuid"
)

type Notification struct {
	ID      uuid.UUID
	UserID  uuid.UUID
	Channel string
	Payload string
	SentAt  *time.Time
}
