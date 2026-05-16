package billing

import (
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/billing/app"
	billinghttp "github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/billing/infra/http"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/billing/infra/postgres"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/events"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/server"
)

type Module struct {
	Service *app.Service
	Handler *billinghttp.Handler
}

func New(db *pgxpool.Pool, bus *events.Bus) *Module {
	repo := postgres.NewSubscriptionRepo(db)
	svc := app.New(repo, bus)
	return &Module{Service: svc, Handler: billinghttp.NewHandler(svc)}
}

func (m *Module) Routes() server.RouteRegistrar { return m.Handler }
