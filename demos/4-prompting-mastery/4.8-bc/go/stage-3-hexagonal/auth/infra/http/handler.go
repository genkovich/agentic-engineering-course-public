package http

import (
	stdhttp "net/http"

	"github.com/go-chi/chi/v5"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/auth/app"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/httputil"
)

type Handler struct {
	svc *app.Service
}

func NewHandler(svc *app.Service) *Handler {
	return &Handler{svc: svc}
}

func (h *Handler) Register(r chi.Router) {
	r.Post("/auth/register", h.register)
	r.Post("/auth/login", h.login)
}

func (h *Handler) register(w stdhttp.ResponseWriter, r *stdhttp.Request) {
	var req registerReq
	if err := httputil.DecodeBody(r, &req); err != nil || req.Email == "" || req.Password == "" {
		httputil.WriteJSON(w, stdhttp.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	u, err := h.svc.Register(r.Context(), req.Email, req.Password)
	if err != nil {
		httputil.WriteError(w, toAPIError(err))
		return
	}
	httputil.WriteJSON(w, stdhttp.StatusCreated, registerResp{
		UserID:    u.ID,
		Email:     u.Email,
		CreatedAt: u.CreatedAt,
	})
}

func (h *Handler) login(w stdhttp.ResponseWriter, r *stdhttp.Request) {
	var req loginReq
	if err := httputil.DecodeBody(r, &req); err != nil {
		httputil.WriteJSON(w, stdhttp.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	u, err := h.svc.Login(r.Context(), req.Email, req.Password)
	if err != nil {
		httputil.WriteError(w, toAPIError(err))
		return
	}
	httputil.WriteJSON(w, stdhttp.StatusOK, loginResp{UserID: u.ID, Email: u.Email})
}
