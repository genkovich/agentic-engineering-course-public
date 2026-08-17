# Локальні перевизначення (порти) — у .env поруч із цим Makefile.
# Той самий файл читає docker compose, тому порт міняється в одному місці.
-include .env
export

PGPORT       ?= 5432
HTTP_PORT    ?= 8080
# Застосунок ходить у базу асинхронно (asyncpg), alembic — синхронно (psycopg 3).
# Драйвер у DSN названий явно: інакше SQLAlchemy вгадує psycopg2, якого тут немає.
DATABASE_URL ?= postgresql+asyncpg://demo:demo@localhost:$(PGPORT)/demo
SYNC_DSN     ?= postgresql+psycopg://demo:demo@localhost:$(PGPORT)/demo
HTTP_ADDR    ?= 0.0.0.0:$(HTTP_PORT)
BASE_URL     ?= http://localhost:$(HTTP_PORT)

.PHONY: help doctor install db-up db-down db-migrate run smoke clean

help:
	@echo "Targets:"
	@echo "  doctor      Перевірити середовище (docker, python, venv, порти)"
	@echo "  install     doctor + залежності з requirements.lock.txt"
	@echo "  db-up       Підняти postgres через docker compose"
	@echo "  db-down     Зупинити postgres і видалити том"
	@echo "  db-migrate  Накотити міграції Alembic (5 ревізій, по одній на BC)"
	@echo "  run         Запустити API на $(HTTP_ADDR)"
	@echo "  smoke       Смикнути 6 ендпоінтів, чекати 2xx"
	@echo "  clean       Зупинити docker, прибрати pgdata"

doctor:
	@bash ../../scripts/preflight.sh py 2

install: doctor
	python3 -m pip install -r requirements.lock.txt

db-up:
	docker compose up -d
	@printf 'Чекаю на postgres'
	@for i in $$(seq 1 60); do \
		if docker compose exec -T postgres pg_isready -U demo -d demo -h 127.0.0.1 >/dev/null 2>&1; then \
			echo " готовий."; exit 0; \
		fi; \
		printf '.'; sleep 1; \
	done; \
	echo ""; \
	echo "✗ Postgres не піднявся за 60 с. Останні рядки логу:"; \
	docker compose logs --tail=40 postgres; \
	exit 1

db-down:
	docker compose down -v

db-migrate: db-up
	DATABASE_URL=$(SYNC_DSN) alembic upgrade head

run:
	DATABASE_URL=$(DATABASE_URL) uvicorn app.main:app --host $(word 1,$(subst :, ,$(HTTP_ADDR))) --port $(word 2,$(subst :, ,$(HTTP_ADDR)))

smoke:
	@bash ./scripts/smoke.sh $(BASE_URL)

clean: db-down
