// Package auth — self-wiring entry point для Auth BC.
// main.go викликає New(...) і отримує *Module з готовим RouteRegistrar.
package auth

import (
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/auth/app"
	authhttp "github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/auth/infra/http"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/auth/infra/postgres"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/events"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/server"
)

type Module struct {
	Service  *app.Service
	Handler  *authhttp.Handler
}

func New(db *pgxpool.Pool, bus *events.Bus) *Module {
	repo := postgres.NewUserRepo(db)
	svc := app.New(repo, bus)
	h := authhttp.NewHandler(svc)
	return &Module{Service: svc, Handler: h}
}

func (m *Module) Routes() server.RouteRegistrar { return m.Handler }
