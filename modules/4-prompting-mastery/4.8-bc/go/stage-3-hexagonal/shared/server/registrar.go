// Package server — RouteRegistrar interface and Server bootstrapping.
// Кожен BC self-wires і повертає *Module зі своїм registrar.
package server

import "github.com/go-chi/chi/v5"

type RouteRegistrar interface {
	Register(r chi.Router)
}
