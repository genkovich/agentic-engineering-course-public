// Package events — підписники на події інших BC.
// Notifications — sink: слухає auth.UserRegistered, billing.SubscriptionCreated etc
// і викликає notifications/app/service.Send.
//
// Імпорт чужих BC domain-ів припустимий ТУТ, бо це event subscription layer
// (за конвенцією — як і pub/sub topic name є cross-BC). go-arch-lint config дозволяє це
// тільки для notifications/infra/events.
package events

import (
	"context"
	"log"

	authdomain "github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/auth/domain"
	billingdomain "github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/billing/domain"
	commercedomain "github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/commerce/domain"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/notifications/app"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/notifications/domain"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/events"
)

func Register(bus *events.Bus, svc *app.Service) {
	bus.Subscribe(authdomain.UserRegistered{}.Name(), func(ctx context.Context, e events.Event) {
		ev := e.(authdomain.UserRegistered)
		if _, err := svc.Send(ctx, ev.UserID, domain.ChannelEmail, "Welcome to our service!"); err != nil {
			log.Printf("[notifications.subscriber] welcome email: %v", err)
		}
	})

	bus.Subscribe(commercedomain.OrderPlaced{}.Name(), func(ctx context.Context, e events.Event) {
		ev := e.(commercedomain.OrderPlaced)
		if _, err := svc.Send(ctx, ev.UserID, domain.ChannelEmail, "Your order has been placed."); err != nil {
			log.Printf("[notifications.subscriber] order placed: %v", err)
		}
	})

	bus.Subscribe(billingdomain.SubscriptionCreated{}.Name(), func(ctx context.Context, e events.Event) {
		ev := e.(billingdomain.SubscriptionCreated)
		if _, err := svc.Send(ctx, ev.UserID, domain.ChannelEmail, "Subscription confirmed: "+ev.Plan); err != nil {
			log.Printf("[notifications.subscriber] subscription created: %v", err)
		}
	})
}
