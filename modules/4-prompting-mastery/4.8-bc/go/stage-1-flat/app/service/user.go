package service

import (
	"context"
	"errors"
	"time"

	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/model"
)

var (
	ErrInvalidCredentials = errors.New("invalid credentials")
)

type UserRepo interface {
	Create(ctx context.Context, u model.User) error
	FindByEmail(ctx context.Context, email string) (*model.User, error)
}

type UserService struct {
	repo UserRepo
}

func NewUserService(r UserRepo) *UserService {
	return &UserService{repo: r}
}

func (s *UserService) Register(ctx context.Context, email, password string) (*model.User, error) {
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}
	u := model.User{
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

func (s *UserService) Login(ctx context.Context, email, password string) (*model.User, error) {
	u, err := s.repo.FindByEmail(ctx, email)
	if err != nil {
		return nil, ErrInvalidCredentials
	}
	if err := bcrypt.CompareHashAndPassword([]byte(u.PasswordHash), []byte(password)); err != nil {
		return nil, ErrInvalidCredentials
	}
	return u, nil
}
