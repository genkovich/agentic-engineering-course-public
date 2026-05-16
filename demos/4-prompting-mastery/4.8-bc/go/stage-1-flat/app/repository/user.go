package repository

import (
	"context"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgxpool"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/model"
)

type UserRepo struct {
	db *pgxpool.Pool
}

func NewUserRepo(db *pgxpool.Pool) *UserRepo {
	return &UserRepo{db: db}
}

func (r *UserRepo) Create(ctx context.Context, u model.User) error {
	_, err := r.db.Exec(ctx,
		`INSERT INTO users (id, email, password_hash, created_at) VALUES ($1, $2, $3, $4)`,
		u.ID, u.Email, u.PasswordHash, u.CreatedAt)
	return err
}

func (r *UserRepo) FindByEmail(ctx context.Context, email string) (*model.User, error) {
	var u model.User
	err := r.db.QueryRow(ctx,
		`SELECT id, email, password_hash, created_at FROM users WHERE email = $1`, email).
		Scan(&u.ID, &u.Email, &u.PasswordHash, &u.CreatedAt)
	if err != nil {
		return nil, err
	}
	return &u, nil
}

func (r *UserRepo) FindByID(ctx context.Context, id uuid.UUID) (*model.User, error) {
	var u model.User
	err := r.db.QueryRow(ctx,
		`SELECT id, email, password_hash, created_at FROM users WHERE id = $1`, id).
		Scan(&u.ID, &u.Email, &u.PasswordHash, &u.CreatedAt)
	if err != nil {
		return nil, err
	}
	return &u, nil
}
