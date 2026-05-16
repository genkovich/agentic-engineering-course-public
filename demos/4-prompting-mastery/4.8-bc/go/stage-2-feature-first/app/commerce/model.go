package commerce

import (
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
