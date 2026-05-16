// Package domain — Notifications Bounded Context.
// Notifications — sink BC: підписується на події інших BC і шле email/push/sms.
package domain

import (
	"context"
	"time"

	"github.com/google/uuid"
)

type Channel string

const (
	ChannelEmail Channel = "email"
	ChannelPush  Channel = "push"
	ChannelSMS   Channel = "sms"
)

type Notification struct {
	ID      uuid.UUID
	UserID  uuid.UUID
	Channel Channel
	Payload string
	SentAt  *time.Time
}

// Sender — port. Реалізації живуть у notifications/infra/{email,push,stub}.
type Sender interface {
	Send(ctx context.Context, n Notification) error
}

type Repository interface {
	Save(ctx context.Context, n Notification) error
}
