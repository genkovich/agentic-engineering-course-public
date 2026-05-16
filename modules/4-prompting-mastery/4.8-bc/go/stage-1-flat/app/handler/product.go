package handler

import (
	"context"
	"net/http"

	"github.com/go-chi/chi/v5"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-1-flat/app/model"
)

type productServiceAPI interface {
	List(ctx context.Context) ([]model.Product, error)
}

type productHandler struct {
	svc productServiceAPI
}

func MountProduct(r chi.Router, svc productServiceAPI) {
	h := &productHandler{svc: svc}
	r.Get("/products", h.list)
}

func (h *productHandler) list(w http.ResponseWriter, r *http.Request) {
	products, err := h.svc.List(r.Context())
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": "list_failed"})
		return
	}
	out := make([]map[string]any, 0, len(products))
	for _, p := range products {
		out = append(out, map[string]any{
			"id":          p.ID.String(),
			"name":        p.Name,
			"price_cents": p.PriceCents,
			"category_id": p.CategoryID.String(),
		})
	}
	writeJSON(w, http.StatusOK, map[string]any{"products": out})
}
