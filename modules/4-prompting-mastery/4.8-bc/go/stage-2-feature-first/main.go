package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/go-chi/chi/v5"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-2-feature-first/app/auth"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-2-feature-first/app/billing"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-2-feature-first/app/catalog"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-2-feature-first/app/commerce"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-2-feature-first/app/notifications"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-2-feature-first/shared/db"
)

func main() {
	dsn := envOr("DATABASE_URL", "postgres://demo:demo@localhost:5432/demo?sslmode=disable")
	addr := envOr("HTTP_ADDR", ":8080")

	pool, err := db.NewPool(context.Background(), dsn)
	if err != nil {
		log.Fatalf("db connect: %v", err)
	}
	defer pool.Close()

	authH := auth.NewHandler(auth.NewService(auth.NewRepository(pool)))
	catalogH := catalog.NewHandler(catalog.NewService(catalog.NewRepository(pool)))
	commerceH := commerce.NewHandler(commerce.NewService(commerce.NewRepository(pool)))
	billingH := billing.NewHandler(billing.NewService(billing.NewRepository(pool)))
	notificationsH := notifications.NewHandler(notifications.NewService(notifications.NewRepository(pool)))

	r := chi.NewRouter()
	authH.Register(r)
	catalogH.Register(r)
	commerceH.Register(r)
	billingH.Register(r)
	notificationsH.Register(r)

	r.Get("/healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte(`{"ok":true}`))
	})

	srv := &http.Server{
		Addr:              addr,
		Handler:           r,
		ReadHeaderTimeout: 5 * time.Second,
	}

	log.Printf("listening on %s", addr)
	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("server: %v", err)
	}
}

func envOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}
