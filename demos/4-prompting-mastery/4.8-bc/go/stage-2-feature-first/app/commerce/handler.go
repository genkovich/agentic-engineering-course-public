package commerce

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
	r.Post("/orders", h.place)
}

type placeReq struct {
	UserID     string `json:"user_id"`
	TotalCents int64  `json:"total_cents"`
}

func (h *Handler) place(w http.ResponseWriter, r *http.Request) {
	var req placeReq
	if err := httputil.DecodeBody(r, &req); err != nil {
		httputil.WriteJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	uid, err := uuid.Parse(req.UserID)
	if err != nil {
		httputil.WriteJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_user_id"})
		return
	}
	o, err := h.svc.Place(r.Context(), uid, req.TotalCents)
	if err != nil {
		httputil.WriteError(w, err)
		return
	}
	httputil.WriteJSON(w, http.StatusCreated, map[string]string{"order_id": o.ID.String(), "status": o.Status})
}
