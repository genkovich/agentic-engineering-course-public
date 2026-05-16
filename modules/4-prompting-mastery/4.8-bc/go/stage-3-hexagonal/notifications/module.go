package notifications

import (
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/notifications/app"
	notifevents "github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/notifications/infra/events"
	notifhttp "github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/notifications/infra/http"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/notifications/infra/postgres"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/notifications/infra/stub"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/events"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/server"
)

type Module struct {
	Service *app.Service
	Handler *notifhttp.Handler
}

func New(db *pgxpool.Pool, bus *events.Bus) *Module {
	repo := postgres.NewNotificationRepo(db)
	sender := stub.NewSender()
	svc := app.New(repo, sender)
	notifevents.Register(bus, svc)
	return &Module{Service: svc, Handler: notifhttp.NewHandler(svc)}
}

func (m *Module) Routes() server.RouteRegistrar { return m.Handler }
