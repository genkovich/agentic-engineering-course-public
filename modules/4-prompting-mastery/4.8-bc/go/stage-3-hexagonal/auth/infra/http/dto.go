package http

import (
	"time"

	"github.com/google/uuid"
)

type registerReq struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type registerResp struct {
	UserID    uuid.UUID `json:"user_id"`
	Email     string    `json:"email"`
	CreatedAt time.Time `json:"created_at"`
}

type loginReq struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

type loginResp struct {
	UserID uuid.UUID `json:"user_id"`
	Email  string    `json:"email"`
}
