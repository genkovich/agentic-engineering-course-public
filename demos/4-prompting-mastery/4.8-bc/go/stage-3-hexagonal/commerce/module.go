package commerce

import (
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/commerce/app"
	commercehttp "github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/commerce/infra/http"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/commerce/infra/postgres"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/events"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/server"
)

type Module struct {
	Service *app.Service
	Handler *commercehttp.Handler
}

func New(db *pgxpool.Pool, bus *events.Bus) *Module {
	repo := postgres.NewOrderRepo(db)
	svc := app.New(repo, bus)
	return &Module{Service: svc, Handler: commercehttp.NewHandler(svc)}
}

func (m *Module) Routes() server.RouteRegistrar { return m.Handler }
