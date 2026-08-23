DATABASE_URL ?= postgres://demo:demo@localhost:5432/demo?sslmode=disable
HTTP_ADDR    ?= :8080
BASE_URL     ?= http://localhost:8080

.PHONY: help db-up db-down db-migrate run smoke arch-test arch-lint-install build clean

help:
	@echo "Targets:"
	@echo "  db-up           Start postgres via docker compose"
	@echo "  db-down         Stop postgres and remove volume"
	@echo "  db-migrate      Apply migrations/*.sql in order"
	@echo "  build           Build the binary"
	@echo "  run             Run the API on $(HTTP_ADDR)"
	@echo "  smoke           Hit 6 endpoints, expect all 2xx"
	@echo "  arch-test       Run go-arch-lint and go vet"
	@echo "  arch-lint-install  Install go-arch-lint binary"
	@echo "  clean           Stop docker, remove pgdata"

db-up:
	docker compose up -d
	@echo "Waiting for postgres..."
	@until docker compose exec -T postgres pg_isready -U demo > /dev/null 2>&1; do sleep 1; done
	@echo "Postgres ready."

db-down:
	docker compose down -v

db-migrate:
	@for f in migrations/*.sql; do \
		echo "applying $$f"; \
		docker compose exec -T postgres psql -U demo -d demo < "$$f" || exit 1; \
	done

build:
	go build -o bin/server .

run:
	DATABASE_URL=$(DATABASE_URL) HTTP_ADDR=$(HTTP_ADDR) go run .

smoke:
	@bash ./scripts/smoke.sh $(BASE_URL)

arch-lint-install:
	go install github.com/fe3dback/go-arch-lint@v1.17.0

arch-test:
	@command -v go-arch-lint >/dev/null 2>&1 || { echo "go-arch-lint not installed; run: make arch-lint-install"; exit 1; }
	go-arch-lint check
	go vet ./...

clean: db-down
