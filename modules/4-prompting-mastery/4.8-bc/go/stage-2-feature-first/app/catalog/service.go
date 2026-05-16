// Package catalog — Catalog feature: продукти, категорії.
package catalog

import "context"

type Service struct {
	repo *Repository
}

func NewService(repo *Repository) *Service {
	return &Service{repo: repo}
}

func (s *Service) List(ctx context.Context) ([]Product, error) {
	return s.repo.List(ctx)
}
