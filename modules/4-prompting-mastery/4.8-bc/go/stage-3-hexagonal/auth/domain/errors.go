package domain

import "errors"

var (
	ErrInvalidCredentials = errors.New("auth.invalid_credentials")
	ErrEmailAlreadyExists = errors.New("auth.email_already_exists")
	ErrUserNotFound       = errors.New("auth.user_not_found")
)
