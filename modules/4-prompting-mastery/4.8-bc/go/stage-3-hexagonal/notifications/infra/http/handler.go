package http

import (
	stdhttp "net/http"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/notifications/app"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/notifications/domain"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/httputil"
)

type Handler struct {
	svc *app.Service
}

func NewHandler(svc *app.Service) *Handler {
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

type sendTestResp struct {
	NotificationID uuid.UUID  `json:"notification_id"`
	Channel        string     `json:"channel"`
	SentAt         *time.Time `json:"sent_at"`
}

func (h *Handler) sendTest(w stdhttp.ResponseWriter, r *stdhttp.Request) {
	var req sendTestReq
	if err := httputil.DecodeBody(r, &req); err != nil {
		httputil.WriteJSON(w, stdhttp.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	uid, err := uuid.Parse(req.UserID)
	if err != nil {
		httputil.WriteJSON(w, stdhttp.StatusBadRequest, map[string]string{"error": "invalid_user_id"})
		return
	}
	channel := domain.Channel(req.Channel)
	if channel == "" {
		channel = domain.ChannelEmail
	}
	if req.Payload == "" {
		req.Payload = "test notification"
	}

	n, err := h.svc.Send(r.Context(), uid, channel, req.Payload)
	if err != nil {
		httputil.WriteError(w, err)
		return
	}
	httputil.WriteJSON(w, stdhttp.StatusOK, sendTestResp{
		NotificationID: n.ID,
		Channel:        string(n.Channel),
		SentAt:         n.SentAt,
	})
}
