package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/handler"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/repository"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/service"
)

func main() {
	dsn := envOr("DATABASE_URL", "postgres://demo:demo@localhost:5432/demo?sslmode=disable")
	addr := envOr("HTTP_ADDR", ":8080")

	pool, err := pgxpool.New(context.Background(), dsn)
	if err != nil {
		log.Fatalf("db connect: %v", err)
	}
	defer pool.Close()

	userRepo := repository.NewUserRepo(pool)
	productRepo := repository.NewProductRepo(pool)
	orderRepo := repository.NewOrderRepo(pool)
	subscriptionRepo := repository.NewSubscriptionRepo(pool)
	notificationRepo := repository.NewNotificationRepo(pool)

	userSvc := service.NewUserService(userRepo)
	productSvc := service.NewProductService(productRepo)
	orderSvc := service.NewOrderService(orderRepo)
	subscriptionSvc := service.NewSubscriptionService(subscriptionRepo)
	notificationSvc := service.NewNotificationService(notificationRepo)

	r := chi.NewRouter()
	handler.MountUser(r, userSvc)
	handler.MountProduct(r, productSvc)
	handler.MountOrder(r, orderSvc)
	handler.MountSubscription(r, subscriptionSvc)
	handler.MountNotification(r, notificationSvc)

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
