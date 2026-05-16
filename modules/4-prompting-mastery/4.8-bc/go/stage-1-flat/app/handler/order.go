package handler

import (
	"context"
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/model"
)

type orderServiceAPI interface {
	Place(ctx context.Context, userID uuid.UUID, totalCents int64) (*model.Order, error)
}

type orderHandler struct {
	svc orderServiceAPI
}

func MountOrder(r chi.Router, svc orderServiceAPI) {
	h := &orderHandler{svc: svc}
	r.Post("/orders", h.place)
}

type placeOrderReq struct {
	UserID     string `json:"user_id"`
	TotalCents int64  `json:"total_cents"`
}

func (h *orderHandler) place(w http.ResponseWriter, r *http.Request) {
	var req placeOrderReq
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	uid, err := uuid.Parse(req.UserID)
	if err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_user_id"})
		return
	}
	o, err := h.svc.Place(r.Context(), uid, req.TotalCents)
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "place_failed"})
		return
	}
	writeJSON(w, http.StatusCreated, map[string]string{"order_id": o.ID.String(), "status": o.Status})
}
