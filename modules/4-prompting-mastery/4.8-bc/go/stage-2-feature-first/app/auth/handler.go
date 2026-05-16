package auth

import (
	"errors"
	"net/http"

	"github.com/go-chi/chi/v5"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-2-feature-first/shared/httputil"
)

type Handler struct {
	svc *Service
}

func NewHandler(svc *Service) *Handler {
	return &Handler{svc: svc}
}

func (h *Handler) Register(r chi.Router) {
	r.Post("/auth/register", h.register)
	r.Post("/auth/login", h.login)
}

type credsReq struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

func (h *Handler) register(w http.ResponseWriter, r *http.Request) {
	var req credsReq
	if err := httputil.DecodeBody(r, &req); err != nil || req.Email == "" || req.Password == "" {
		httputil.WriteJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	u, err := h.svc.Register(r.Context(), req.Email, req.Password)
	if err != nil {
		httputil.WriteError(w, err)
		return
	}
	httputil.WriteJSON(w, http.StatusCreated, map[string]string{"user_id": u.ID.String(), "email": u.Email})
}

func (h *Handler) login(w http.ResponseWriter, r *http.Request) {
	var req credsReq
	if err := httputil.DecodeBody(r, &req); err != nil {
		httputil.WriteJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	u, err := h.svc.Login(r.Context(), req.Email, req.Password)
	if err != nil {
		if errors.Is(err, ErrInvalidCredentials) {
			httputil.WriteJSON(w, http.StatusUnauthorized, map[string]string{"error": "invalid_credentials"})
			return
		}
		httputil.WriteError(w, err)
		return
	}
	httputil.WriteJSON(w, http.StatusOK, map[string]string{"user_id": u.ID.String(), "email": u.Email})
}
