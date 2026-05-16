// Package apperr — типізовані помилки для крос-BC помилкової семантики.
// Кожен BC мапить власні sentinel errors на Error через свій ports-шар.
package apperr

import "fmt"

type Error struct {
	Code       string
	Message    string
	StatusCode int
}

func (e *Error) Error() string {
	return fmt.Sprintf("%s: %s", e.Code, e.Message)
}

func New(code, message string, statusCode int) *Error {
	return &Error{Code: code, Message: message, StatusCode: statusCode}
}
