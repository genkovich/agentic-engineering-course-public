package handler

import (
	"context"
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/model"
)

type subscriptionServiceAPI interface {
	Subscribe(ctx context.Context, userID uuid.UUID, plan string) (*model.Subscription, error)
}

type subscriptionHandler struct {
	svc subscriptionServiceAPI
}

func MountSubscription(r chi.Router, svc subscriptionServiceAPI) {
	h := &subscriptionHandler{svc: svc}
	r.Post("/subscriptions", h.subscribe)
}

type subscribeReq struct {
	UserID string `json:"user_id"`
	Plan   string `json:"plan"`
}

func (h *subscriptionHandler) subscribe(w http.ResponseWriter, r *http.Request) {
	var req subscribeReq
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.Plan == "" {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	uid, err := uuid.Parse(req.UserID)
	if err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_user_id"})
		return
	}
	sub, err := h.svc.Subscribe(r.Context(), uid, req.Plan)
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "subscribe_failed"})
		return
	}
	writeJSON(w, http.StatusCreated, map[string]any{
		"subscription_id": sub.ID.String(),
		"plan":            sub.Plan,
		"next_charge_at":  sub.NextChargeAt,
	})
}
