package billing

import (
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-2-feature-first/shared/httputil"
)

type Handler struct {
	svc *Service
}

func NewHandler(svc *Service) *Handler {
	return &Handler{svc: svc}
}

func (h *Handler) Register(r chi.Router) {
	r.Post("/subscriptions", h.subscribe)
}

type subscribeReq struct {
	UserID string `json:"user_id"`
	Plan   string `json:"plan"`
}

func (h *Handler) subscribe(w http.ResponseWriter, r *http.Request) {
	var req subscribeReq
	if err := httputil.DecodeBody(r, &req); err != nil || req.Plan == "" {
		httputil.WriteJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	uid, err := uuid.Parse(req.UserID)
	if err != nil {
		httputil.WriteJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_user_id"})
		return
	}
	sub, err := h.svc.Subscribe(r.Context(), uid, req.Plan)
	if err != nil {
		httputil.WriteError(w, err)
		return
	}
	httputil.WriteJSON(w, http.StatusCreated, map[string]any{
		"subscription_id": sub.ID.String(),
		"plan":            sub.Plan,
		"next_charge_at":  sub.NextChargeAt,
	})
}
