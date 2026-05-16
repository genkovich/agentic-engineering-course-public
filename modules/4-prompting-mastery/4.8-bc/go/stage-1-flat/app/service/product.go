package service

import (
	"context"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/model"
)

type ProductRepo interface {
	List(ctx context.Context) ([]model.Product, error)
}

type ProductService struct {
	repo ProductRepo
}

func NewProductService(r ProductRepo) *ProductService {
	return &ProductService{repo: r}
}

func (s *ProductService) List(ctx context.Context) ([]model.Product, error) {
	return s.repo.List(ctx)
}
