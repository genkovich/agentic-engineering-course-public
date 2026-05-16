package catalog

import (
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/catalog/app"
	cataloghttp "github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/catalog/infra/http"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/catalog/infra/postgres"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/server"
)

type Module struct {
	Service *app.Service
	Handler *cataloghttp.Handler
}

func New(db *pgxpool.Pool) *Module {
	repo := postgres.NewProductRepo(db)
	svc := app.New(repo)
	return &Module{Service: svc, Handler: cataloghttp.NewHandler(svc)}
}

func (m *Module) Routes() server.RouteRegistrar { return m.Handler }
