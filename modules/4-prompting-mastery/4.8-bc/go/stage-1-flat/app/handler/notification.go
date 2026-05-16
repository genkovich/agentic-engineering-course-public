package handler

import (
	"context"
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/model"
)

type notificationServiceAPI interface {
	SendTest(ctx context.Context, userID uuid.UUID, channel, payload string) (*model.Notification, error)
}

type notificationHandler struct {
	svc notificationServiceAPI
}

func MountNotification(r chi.Router, svc notificationServiceAPI) {
	h := &notificationHandler{svc: svc}
	r.Post("/notifications/test", h.sendTest)
}

type sendTestReq struct {
	UserID  string `json:"user_id"`
	Channel string `json:"channel"`
	Payload string `json:"payload"`
}

func (h *notificationHandler) sendTest(w http.ResponseWriter, r *http.Request) {
	var req sendTestReq
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	uid, err := uuid.Parse(req.UserID)
	if err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_user_id"})
		return
	}
	if req.Channel == "" {
		req.Channel = "email"
	}
	if req.Payload == "" {
		req.Payload = "test notification"
	}
	n, err := h.svc.SendTest(r.Context(), uid, req.Channel, req.Payload)
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "send_failed"})
		return
	}
	writeJSON(w, http.StatusOK, map[string]any{
		"notification_id": n.ID.String(),
		"channel":         n.Channel,
		"sent_at":         n.SentAt,
	})
}
