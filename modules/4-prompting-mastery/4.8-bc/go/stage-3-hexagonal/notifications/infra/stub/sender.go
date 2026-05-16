// Package stub — заглушка Sender, що логує у stdout. Для демо.
// Production-варіант жив би у notifications/infra/email/, notifications/infra/push/.
package stub

import (
	"context"
	"log"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/notifications/domain"
)

type Sender struct{}

func NewSender() *Sender { return &Sender{} }

func (s *Sender) Send(_ context.Context, n domain.Notification) error {
	log.Printf("[stub-sender] %s -> user=%s payload=%q", n.Channel, n.UserID, n.Payload)
	return nil
}
