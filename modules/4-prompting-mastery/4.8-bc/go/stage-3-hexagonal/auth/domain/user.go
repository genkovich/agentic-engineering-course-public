// Package domain — Auth Bounded Context, доменні типи й порти.
// Не імпортує net/http, БД, інші BC.
package domain

import (
	"time"

	"github.com/google/uuid"
)

type User struct {
	ID           uuid.UUID
	Email        string
	PasswordHash string
	CreatedAt    time.Time
}

// UserRegistered — domain event, публікується через event bus.
// Notifications BC підписується на нього для welcome-листа.
type UserRegistered struct {
	UserID uuid.UUID
	Email  string
	At     time.Time
}

func (UserRegistered) Name() string { return "auth.UserRegistered" }
