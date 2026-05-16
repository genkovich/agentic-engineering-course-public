package catalog

import (
	"net/http"

	"github.com/go-chi/chi/v5"

	"github.com/genkovich/claude-course-demos/4.8-bc/go/stage-2-feature-first/shared/httputil"
)

type Handler struct {
	svc *Service
}

func NewHandler(svc *Service) *Handler {
	return &Handler{svc: svc}
}

func (h *Handler) Register(r chi.Router) {
	r.Get("/products", h.list)
}

func (h *Handler) list(w http.ResponseWriter, r *http.Request) {
	products, err := h.svc.List(r.Context())
	if err != nil {
		httputil.WriteError(w, err)
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
	httputil.WriteJSON(w, http.StatusOK, map[string]any{"products": out})
}
