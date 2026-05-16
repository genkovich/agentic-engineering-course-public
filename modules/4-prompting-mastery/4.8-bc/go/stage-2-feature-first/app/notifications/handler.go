package notifications

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
	r.Post("/notifications/test", h.sendTest)
}

type sendTestReq struct {
	UserID  string `json:"user_id"`
	Channel string `json:"channel"`
	Payload string `json:"payload"`
}

func (h *Handler) sendTest(w http.ResponseWriter, r *http.Request) {
	var req sendTestReq
	if err := httputil.DecodeBody(r, &req); err != nil {
		httputil.WriteJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	uid, err := uuid.Parse(req.UserID)
	if err != nil {
		httputil.WriteJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_user_id"})
		return
	}
	if req.Channel == "" {
		req.Channel = "email"
	}
	if req.Payload == "" {
		req.Payload = "test notification"
	}
	n, err := h.svc.Send(r.Context(), uid, req.Channel, req.Payload)
	if err != nil {
		httputil.WriteError(w, err)
		return
	}
	httputil.WriteJSON(w, http.StatusOK, map[string]any{
		"notification_id": n.ID.String(),
		"channel":         n.Channel,
		"sent_at":         n.SentAt,
	})
}
