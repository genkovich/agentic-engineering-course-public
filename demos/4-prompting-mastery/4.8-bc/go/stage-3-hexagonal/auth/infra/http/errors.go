// Package http — HTTP adapter для Auth BC.
// errors.go мапить domain sentinel errors на shared/apperr.Error.
package http

import (
	"errors"
	stdhttp "net/http"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/auth/domain"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/apperr"
)

func toAPIError(err error) error {
	switch {
	case errors.Is(err, domain.ErrInvalidCredentials):
		return apperr.New("auth.invalid_credentials", "invalid email or password", stdhttp.StatusUnauthorized)
	case errors.Is(err, domain.ErrEmailAlreadyExists):
		return apperr.New("auth.email_already_exists", "email is already registered", stdhttp.StatusConflict)
	case errors.Is(err, domain.ErrUserNotFound):
		return apperr.New("auth.user_not_found", "user not found", stdhttp.StatusNotFound)
	default:
		return err
	}
}
