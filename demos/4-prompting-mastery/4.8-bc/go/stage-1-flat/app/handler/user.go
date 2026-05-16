package handler

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"

	"github.com/go-chi/chi/v5"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/model"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/service"
)

type userServiceAPI interface {
	Register(ctx context.Context, email, password string) (*model.User, error)
	Login(ctx context.Context, email, password string) (*model.User, error)
}

type userHandler struct {
	svc userServiceAPI
}

func MountUser(r chi.Router, svc userServiceAPI) {
	h := &userHandler{svc: svc}
	r.Post("/auth/register", h.register)
	r.Post("/auth/login", h.login)
}

type credsReq struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

func (h *userHandler) register(w http.ResponseWriter, r *http.Request) {
	var req credsReq
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.Email == "" || req.Password == "" {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	u, err := h.svc.Register(r.Context(), req.Email, req.Password)
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "register_failed"})
		return
	}
	writeJSON(w, http.StatusCreated, map[string]string{"user_id": u.ID.String(), "email": u.Email})
}

func (h *userHandler) login(w http.ResponseWriter, r *http.Request) {
	var req credsReq
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid_request"})
		return
	}
	u, err := h.svc.Login(r.Context(), req.Email, req.Password)
	if err != nil {
		if errors.Is(err, service.ErrInvalidCredentials) {
			writeJSON(w, http.StatusUnauthorized, map[string]string{"error": "invalid_credentials"})
			return
		}
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "login_failed"})
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"user_id": u.ID.String(), "email": u.Email})
}
