---
paths:
  - "api/**/*.go"
---

# API development rules

Завантажується тільки коли Claude чіпає `.go` файл під `api/`. Покриває handlers, router setup, middleware.

## Endpoint structure

- Every endpoint validates input before doing anything. Use `go-playground/validator` for struct tags.
- Validation errors return `400 Bad Request` with a structured body: `{"code": "module.error_name", "message": "..."}`.
- Handlers are thin. Parse request, call domain, render response. No business logic in handler bodies.
- One file per resource: `api/handlers/users.go` owns user endpoints, `api/handlers/orders.go` owns orders.

## Error handling

- Domain returns sentinel errors: `var ErrUserNotFound = errors.New("user.not_found")`.
- Ports layer maps sentinels to HTTP codes through a single `apperr.Error{Code, Message, StatusCode}` translator.
- Never return raw `error` strings to clients. Always go through the error code map.
- Use `errors.Is` and `errors.As` for comparison. Never compare error strings.

## Logging and observability

- Log at the boundary, not inside domain. Handler logs request metadata, not domain internals.
- Structured logs via `slog`: `slog.Info("user created", "user_id", id, "request_id", reqID)`. No `fmt.Sprintf` log lines.
- Every request gets a request ID via middleware. Pass it through context.
- Never log request bodies. Log field names if needed for debugging.

## Concurrency

- Pass `context.Context` as the first argument to every function that does I/O.
- Cancel propagation: respect `ctx.Done()` in long-running loops and database queries.
- No `goroutine` launches without a `context.Context` and a clear shutdown path.
