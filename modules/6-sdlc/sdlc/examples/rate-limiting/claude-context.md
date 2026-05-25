---
status: Approved
owner: Kyrylo
reviewers: [Backend Lead]
updated_at: "2026-05-14"
feature_size: S
stage: "14"
ticket: INC-841
---

# Claude execution context — Rate limiting

## Goal
Реалізувати task **T1: Lua `sliding_window.lua` + Go repo wrapper** з [task-breakdown.md](task-breakdown.md).

## Scope
- `internal/middleware/ratelimit/sliding_window.lua` (Lua-script).
- `internal/middleware/ratelimit/redis_repo.go` (тонкий обгортатель `redis.EvalSha`).
- `internal/middleware/ratelimit/redis_repo_test.go` (unit + table-driven).

## Files to read (in order)
1. [SPEC.md](SPEC.md) — §3 AC + §4 NFR.
2. [data-model.md](data-model.md) — алгоритм Lua-скрипта дослівно.
3. [adr/0007-sliding-window-rate-limit.md](adr/0007-sliding-window-rate-limit.md)
4. [task-breakdown.md](task-breakdown.md) — T1 scope + dependencies.
5. `internal/middleware/` — приклади існуючих middleware (для conventions).

## Hard Rules
1. **Один Lua EVAL** на decision — не серія команд.
2. Скрипт лежить у файлі, embed через `//go:embed sliding_window.lua`.
3. Repo повертає struct: `Decision{Allowed bool; Count int; RetryAfterSec int}`.
4. Timeout до Redis — 50ms (`context.WithTimeout`).
5. UUID v7 для запис ID generated **app-side**.
6. **НЕ** змінюй `internal/auth/` чи інший middleware.
7. **НЕ** додавай нові залежності — `github.com/redis/go-redis/v9` вже у `go.mod`.

## Commands
- Test: `make test PKG=./internal/middleware/ratelimit/...`
- Lint: `make lint`
- Format: `make fmt`
- Local Redis: `docker compose up -d redis`

## Out of scope
- Wiring у `main.go` (це T3).
- Метрики (це T4).
- HTTP layer / 429 (це T3).

## Acceptance
- [ ] `make test` зелений на пакеті `ratelimit`.
- [ ] Unit tests покривають: під лімітом, на ліміті, над лімітом, Redis timeout (через mocked client).
- [ ] Lint pass.
- [ ] No new dependencies.
