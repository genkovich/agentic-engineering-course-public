// Package auth — Auth feature: реєстрація, логін.
// Vertical slice: handler, service, repository, model — всі в одному пакеті.
package auth

import (
	"context"
	"errors"
	"time"

	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

var (
	ErrInvalidCredentials = errors.New("auth.invalid_credentials")
)

type Service struct {
	repo *Repository
}

func NewService(repo *Repository) *Service {
	return &Service{repo: repo}
}

func (s *Service) Register(ctx context.Context, email, password string) (*User, error) {
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}
	u := User{
		ID:           uuid.New(),
		Email:        email,
		PasswordHash: string(hash),
		CreatedAt:    time.Now().UTC(),
	}
	if err := s.repo.Create(ctx, u); err != nil {
		return nil, err
	}
	return &u, nil
}

func (s *Service) Login(ctx context.Context, email, password string) (*User, error) {
	u, err := s.repo.FindByEmail(ctx, email)
	if err != nil {
		return nil, ErrInvalidCredentials
	}
	if err := bcrypt.CompareHashAndPassword([]byte(u.PasswordHash), []byte(password)); err != nil {
		return nil, ErrInvalidCredentials
	}
	return u, nil
}
