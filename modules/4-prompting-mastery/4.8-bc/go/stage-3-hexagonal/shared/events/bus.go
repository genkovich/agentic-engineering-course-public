// Package events — мінімальний in-memory event bus для cross-BC комунікації.
// BC-публікатор не знає про підписників. BC-підписник реєструє handler у своєму infra/events/.
package events

import (
	"context"
	"sync"
)

type Event interface {
	Name() string
}

type Handler func(ctx context.Context, e Event)

type Bus struct {
	mu       sync.RWMutex
	handlers map[string][]Handler
}

func NewBus() *Bus {
	return &Bus{handlers: make(map[string][]Handler)}
}

func (b *Bus) Subscribe(name string, h Handler) {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.handlers[name] = append(b.handlers[name], h)
}

func (b *Bus) Publish(ctx context.Context, e Event) {
	b.mu.RLock()
	hs := append([]Handler(nil), b.handlers[e.Name()]...)
	b.mu.RUnlock()
	for _, h := range hs {
		h(ctx, e)
	}
}
