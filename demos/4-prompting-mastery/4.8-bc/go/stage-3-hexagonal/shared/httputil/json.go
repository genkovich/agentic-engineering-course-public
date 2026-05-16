// Package httputil — спільні HTTP helpers (JSON write + error mapping).
// Це cross-cutting утиліти, мінімум — без бізнес-логіки.
package httputil

import (
	"encoding/json"
	"errors"
	"net/http"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/apperr"
)

func WriteJSON(w http.ResponseWriter, status int, body any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(body)
}

func WriteError(w http.ResponseWriter, err error) {
	var ae *apperr.Error
	if errors.As(err, &ae) {
		WriteJSON(w, ae.StatusCode, map[string]string{"error": ae.Code, "message": ae.Message})
		return
	}
	WriteJSON(w, http.StatusInternalServerError, map[string]string{"error": "internal", "message": "unexpected error"})
}

func DecodeBody(r *http.Request, dst any) error {
	return json.NewDecoder(r.Body).Decode(dst)
}
