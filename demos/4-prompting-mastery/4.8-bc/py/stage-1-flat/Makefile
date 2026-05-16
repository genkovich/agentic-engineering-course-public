DATABASE_URL ?= postgresql+asyncpg://demo:demo@localhost:5432/demo
SYNC_DSN     ?= postgresql://demo:demo@localhost:5432/demo
HTTP_ADDR    ?= 0.0.0.0:8080
BASE_URL     ?= http://localhost:8080

.PHONY: help db-up db-down db-migrate run smoke clean

help:
	@echo "Targets:"
	@echo "  db-up       Start postgres via docker compose"
	@echo "  db-down     Stop postgres and remove volume"
	@echo "  db-migrate  Apply Alembic migrations (single revision)"
	@echo "  run         Run the API on $(HTTP_ADDR)"
	@echo "  smoke       Hit 6 endpoints, expect all 2xx"
	@echo "  clean       Stop docker, remove pgdata"

db-up:
	docker compose up -d
	@echo "Waiting for postgres..."
	@until docker compose exec -T postgres pg_isready -U demo > /dev/null 2>&1; do sleep 1; done
	@echo "Postgres ready."

db-down:
	docker compose down -v

db-migrate:
	DATABASE_URL=$(SYNC_DSN) alembic upgrade head

run:
	DATABASE_URL=$(DATABASE_URL) uvicorn app.main:app --host $(word 1,$(subst :, ,$(HTTP_ADDR))) --port $(word 2,$(subst :, ,$(HTTP_ADDR)))

smoke:
	@bash ./scripts/smoke.sh $(BASE_URL)

clean: db-down
