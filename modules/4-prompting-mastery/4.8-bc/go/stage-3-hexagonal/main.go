package main

import (
	"context"
	"log"
	stdhttp "net/http"
	"os"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/auth"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/billing"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/catalog"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/commerce"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/notifications"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/events"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/server"
)

func main() {
	dsn := envOr("DATABASE_URL", "postgres://demo:demo@localhost:5432/demo?sslmode=disable")
	addr := envOr("HTTP_ADDR", ":8080")

	pool, err := pgxpool.New(context.Background(), dsn)
	if err != nil {
		log.Fatalf("db connect: %v", err)
	}
	defer pool.Close()

	bus := events.NewBus()

	authMod := auth.New(pool, bus)
	catalogMod := catalog.New(pool)
	commerceMod := commerce.New(pool, bus)
	billingMod := billing.New(pool, bus)
	notificationsMod := notifications.New(pool, bus)

	r := chi.NewRouter()
	for _, reg := range []server.RouteRegistrar{
		authMod.Routes(),
		catalogMod.Routes(),
		commerceMod.Routes(),
		billingMod.Routes(),
		notificationsMod.Routes(),
	} {
		reg.Register(r)
	}
	r.Get("/healthz", func(w stdhttp.ResponseWriter, _ *stdhttp.Request) {
		w.WriteHeader(stdhttp.StatusOK)
		_, _ = w.Write([]byte(`{"ok":true}`))
	})

	srv := &stdhttp.Server{
		Addr:              addr,
		Handler:           r,
		ReadHeaderTimeout: 5 * time.Second,
	}

	log.Printf("listening on %s", addr)
	if err := srv.ListenAndServe(); err != nil && err != stdhttp.ErrServerClosed {
		log.Fatalf("server: %v", err)
	}
}

func envOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
