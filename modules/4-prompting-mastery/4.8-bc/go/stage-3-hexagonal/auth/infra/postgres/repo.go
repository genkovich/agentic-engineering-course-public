// Package postgres — Postgres adapter для auth.UserRepository.
// Реалізує port, оголошений у auth/domain. Domain не знає про pgx.
package postgres

import (
	"context"
	"errors"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/auth/domain"
)

type UserRepo struct {
	db *pgxpool.Pool
}

func NewUserRepo(db *pgxpool.Pool) *UserRepo {
	return &UserRepo{db: db}
}

func (r *UserRepo) Create(ctx context.Context, u domain.User) error {
	_, err := r.db.Exec(ctx,
		`INSERT INTO auth_users (id, email, password_hash, created_at) VALUES ($1, $2, $3, $4)`,
		u.ID, u.Email, u.PasswordHash, u.CreatedAt)
	return err
}

func (r *UserRepo) FindByEmail(ctx context.Context, email string) (*domain.User, error) {
	var u domain.User
	err := r.db.QueryRow(ctx,
		`SELECT id, email, password_hash, created_at FROM auth_users WHERE email = $1`, email).
		Scan(&u.ID, &u.Email, &u.PasswordHash, &u.CreatedAt)
	if errors.Is(err, pgx.ErrNoRows) {
		return nil, domain.ErrUserNotFound
	}
	if err != nil {
		return nil, err
	}
	return &u, nil
}

func (r *UserRepo) FindByID(ctx context.Context, id uuid.UUID) (*domain.User, error) {
	var u domain.User
	err := r.db.QueryRow(ctx,
		`SELECT id, email, password_hash, created_at FROM auth_users WHERE id = $1`, id).
		Scan(&u.ID, &u.Email, &u.PasswordHash, &u.CreatedAt)
	if errors.Is(err, pgx.ErrNoRows) {
		return nil, domain.ErrUserNotFound
	}
	if err != nil {
		return nil, err
	}
	return &u, nil
}
