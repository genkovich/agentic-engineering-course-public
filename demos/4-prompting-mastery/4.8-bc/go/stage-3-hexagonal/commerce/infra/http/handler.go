package http

import (
	stdhttp "net/http"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/commerce/app"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/httputil"
)

type Handler struct {
	svc *app.Service
}

func NewHandler(svc *app.Service) *Handler {
	return &Handler{svc: svc}
}

func (h *Handler) Register(r chi.Router) {
	r.Post("/orders", h.place)
}

type placeReq struct {
	UserID     string `json:"user_id"`
	TotalCents int64  `json:"total_cents"`
}

type placeResp struct {
	OrderID uuid.UUID `json:"order_id"`
	Status  string    `json:"status"`
}

func (h *Handler) place(w stdhttp.ResponseWriter, r *stdhttp.Request) {
	var req placeReq
	if err := httputil.DecodeBody(r, &req); err != nil {
		httputil.WriteJSON(w, stdhttp.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	uid, err := uuid.Parse(req.UserID)
	if err != nil {
		httputil.WriteJSON(w, stdhttp.StatusBadRequest, map[string]string{"error": "invalid_user_id"})
		return
	}
	o, err := h.svc.Place(r.Context(), uid, req.TotalCents)
	if err != nil {
		httputil.WriteError(w, err)
		return
	}
	httputil.WriteJSON(w, stdhttp.StatusCreated, placeResp{OrderID: o.ID, Status: o.Status})
}
