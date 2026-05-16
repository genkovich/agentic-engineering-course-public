DATABASE_URL ?= postgres://demo:demo@localhost:5432/demo
HTTP_ADDR    ?= :8080
BASE_URL     ?= http://localhost:8080

.PHONY: help db-up db-down db-migrate run smoke build arch-test clean

help:
	@echo "Targets:"
	@echo "  db-up           Start postgres via docker compose"
	@echo "  db-down         Stop postgres and remove volume"
	@echo "  db-migrate      Apply migrations/*.sql in order"
	@echo "  build           Compile TS to JS"
	@echo "  run             Run the API on $(HTTP_ADDR)"
	@echo "  smoke           Hit 6 endpoints, expect all 2xx"
	@echo "  arch-test       Run dependency-cruiser arch rules"
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
	npx tsc

run:
	DATABASE_URL=$(DATABASE_URL) HTTP_ADDR=$(HTTP_ADDR) npx tsx src/index.ts

smoke:
	@bash ./scripts/smoke.sh $(BASE_URL)

arch-test:
	npx depcruise --config .dependency-cruiser.cjs src

clean: db-down
