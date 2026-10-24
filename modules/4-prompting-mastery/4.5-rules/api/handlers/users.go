package handlers

import (
	"encoding/json"
	"errors"
	"log/slog"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-playground/validator/v10"
)

var (
	ErrUserNotFound      = errors.New("user.not_found")
	ErrEmailAlreadyTaken = errors.New("user.email_already_exists")
)

type Users struct {
	log      *slog.Logger
	validate *validator.Validate
}

func NewUsers(log *slog.Logger) *Users {
	return &Users{log: log, validate: validator.New()}
}

func (h *Users) Mount(r chi.Router) {
	r.Post("/", h.create)
	r.Get("/{id}", h.get)
}

type createUserRequest struct {
	Email     string `json:"email" validate:"required,email"`
	FirstName string `json:"first_name" validate:"omitempty,max=100"`
	LastName  string `json:"last_name" validate:"omitempty,max=100"`
}

func (h *Users) create(w http.ResponseWriter, r *http.Request) {
	var req createUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeError(w, http.StatusBadRequest, "user.invalid_body", "invalid JSON")
		return
	}
	if err := h.validate.Struct(&req); err != nil {
		writeError(w, http.StatusBadRequest, "user.validation_failed", err.Error())
		return
	}
	h.log.Info("user created", "email", req.Email, "request_id", middlewareRequestID(r))
	w.WriteHeader(http.StatusCreated)
}

func (h *Users) get(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	if id == "" {
		writeError(w, http.StatusBadRequest, "user.missing_id", "id is required")
		return
	}
	writeError(w, http.StatusNotFound, "user.not_found", "user does not exist")
}

func writeError(w http.ResponseWriter, status int, code, message string) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(map[string]string{"code": code, "message": message})
}

func middlewareRequestID(r *http.Request) string {
	if id := r.Context().Value("request_id"); id != nil {
		if s, ok := id.(string); ok {
			return s
		}
	}
	return ""
}
