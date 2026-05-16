package http

import (
	stdhttp "net/http"

	"github.com/go-chi/chi/v5"
	"github.com/google/uuid"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/catalog/app"
	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-3-hexagonal/shared/httputil"
)

type Handler struct {
	svc *app.Service
}

func NewHandler(svc *app.Service) *Handler {
	return &Handler{svc: svc}
}

func (h *Handler) Register(r chi.Router) {
	r.Get("/products", h.list)
}

type productDTO struct {
	ID         uuid.UUID `json:"id"`
	Name       string    `json:"name"`
	PriceCents int64     `json:"price_cents"`
	CategoryID uuid.UUID `json:"category_id"`
}

func (h *Handler) list(w stdhttp.ResponseWriter, r *stdhttp.Request) {
	products, err := h.svc.List(r.Context())
	if err != nil {
		httputil.WriteError(w, err)
		return
	}
	out := make([]productDTO, 0, len(products))
	for _, p := range products {
		out = append(out, productDTO{
			ID:         p.ID,
			Name:       p.Name,
			PriceCents: p.PriceCents,
			CategoryID: p.CategoryID,
		})
	}
	httputil.WriteJSON(w, stdhttp.StatusOK, map[string]any{"products": out})
}
