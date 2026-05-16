package http

import (
	"errors"
	stdhttp "net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/billing/app"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/billing/domain"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/apperr"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/httputil"
)

type Handler struct {
	svc *app.Service
}

func NewHandler(svc *app.Service) *Handler {
	return &Handler{svc: svc}
}

func (h *Handler) Register(r chi.Router) {
	r.Post("/subscriptions", h.subscribe)
}

type subscribeReq struct {
	UserID string `json:"user_id"`
	Plan   string `json:"plan"`
}

type subscribeResp struct {
	SubscriptionID uuid.UUID `json:"subscription_id"`
	Plan           string    `json:"plan"`
	NextChargeAt   time.Time `json:"next_charge_at"`
}

func (h *Handler) subscribe(w stdhttp.ResponseWriter, r *stdhttp.Request) {
	var req subscribeReq
	if err := httputil.DecodeBody(r, &req); err != nil {
		httputil.WriteJSON(w, stdhttp.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	uid, err := uuid.Parse(req.UserID)
	if err != nil {
		httputil.WriteJSON(w, stdhttp.StatusBadRequest, map[string]string{"error": "invalid_user_id"})
		return
	}
	sub, err := h.svc.Subscribe(r.Context(), uid, req.Plan)
	if err != nil {
		if errors.Is(err, domain.ErrInvalidPlan) {
			httputil.WriteError(w, apperr.New("billing.invalid_plan", "plan must be basic|pro|enterprise", stdhttp.StatusBadRequest))
			return
		}
		httputil.WriteError(w, err)
		return
	}
	httputil.WriteJSON(w, stdhttp.StatusCreated, subscribeResp{
		SubscriptionID: sub.ID,
		Plan:           sub.Plan,
		NextChargeAt:   sub.NextChargeAt,
	})
}
