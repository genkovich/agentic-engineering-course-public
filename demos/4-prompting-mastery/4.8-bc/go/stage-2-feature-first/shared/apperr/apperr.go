// Package apperr — типізовані помилки для крос-BC помилкової семантики.
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
