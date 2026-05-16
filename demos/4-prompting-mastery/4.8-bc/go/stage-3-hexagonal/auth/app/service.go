// Package app — use cases для Auth BC. Залежить тільки від domain interfaces.
package app

import (
	"context"
	"errors"
	"time"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgconn"
	"golang.org/x/crypto/bcrypt"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/auth/domain"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/events"
)

type Service struct {
	repo domain.UserRepository
	bus  *events.Bus
}

func New(repo domain.UserRepository, bus *events.Bus) *Service {
	return &Service{repo: repo, bus: bus}
}

func (s *Service) Register(ctx context.Context, email, password string) (*domain.User, error) {
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}

	u := domain.User{
		ID:           uuid.New(),
		Email:        email,
		PasswordHash: string(hash),
		CreatedAt:    time.Now().UTC(),
	}

	if err := s.repo.Create(ctx, u); err != nil {
		var pgErr *pgconn.PgError
		if errors.As(err, &pgErr) && pgErr.Code == "23505" {
			return nil, domain.ErrEmailAlreadyExists
		}
		return nil, err
	}

	s.bus.Publish(ctx, domain.UserRegistered{UserID: u.ID, Email: u.Email, At: u.CreatedAt})
	return &u, nil
}

func (s *Service) Login(ctx context.Context, email, password string) (*domain.User, error) {
	u, err := s.repo.FindByEmail(ctx, email)
	if err != nil {
		return nil, domain.ErrInvalidCredentials
	}
	if err := bcrypt.CompareHashAndPassword([]byte(u.PasswordHash), []byte(password)); err != nil {
		return nil, domain.ErrInvalidCredentials
	}
	return u, nil
}
