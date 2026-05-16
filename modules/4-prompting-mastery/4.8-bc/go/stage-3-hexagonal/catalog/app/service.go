package app

import (
	"context"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/catalog/domain"
)

type Service struct {
	repo domain.Repository
}

func New(repo domain.Repository) *Service {
	return &Service{repo: repo}
}

func (s *Service) List(ctx context.Context) ([]domain.Product, error) {
	return s.repo.List(ctx)
}
