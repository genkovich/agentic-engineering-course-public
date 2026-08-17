# Локальні перевизначення (порти) — у .env поруч із цим Makefile.
# Той самий файл читає docker compose, тому порт міняється в одному місці.
-include .env
export

PGPORT       ?= 5432
HTTP_PORT    ?= 8080
DATABASE_URL ?= postgres://demo:demo@localhost:$(PGPORT)/demo
HTTP_ADDR    ?= :$(HTTP_PORT)
BASE_URL     ?= http://localhost:$(HTTP_PORT)

# Ніякого npx: він мовчки лізе в мережу і питає дозволу посеред демо.
# Беремо тільки те, що вже встановлене локально через `make install`.
NPM_BIN := ./node_modules/.bin

.PHONY: help doctor install db-up db-down db-migrate build run smoke clean

help:
	@echo "Targets:"
	@echo "  doctor      Перевірити середовище (docker, node, порти)"
	@echo "  install     doctor + npm ci"
	@echo "  db-up       Підняти postgres через docker compose"
	@echo "  db-down     Зупинити postgres і видалити том"
	@echo "  db-migrate  Накотити migrations/*.sql по порядку"
	@echo "  build       Скомпілювати TS у JS"
	@echo "  run         Запустити API на $(HTTP_ADDR)"
	@echo "  smoke       Смикнути 6 ендпоінтів, чекати 2xx"
	@echo "  clean       Зупинити docker, прибрати pgdata"

doctor:
	@bash ../../scripts/preflight.sh ts 2

install: doctor
	npm ci

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
	@for f in migrations/*.sql; do \
		echo "applying $$f"; \
		docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U demo -d demo < "$$f" || exit 1; \
	done

build:
	@test -x $(NPM_BIN)/tsc || { echo "✗ Залежності не встановлені. Запусти: make install"; exit 1; }
	$(NPM_BIN)/tsc

run:
	@test -x $(NPM_BIN)/tsx || { echo "✗ Залежності не встановлені. Запусти: make install"; exit 1; }
	DATABASE_URL=$(DATABASE_URL) HTTP_ADDR=$(HTTP_ADDR) $(NPM_BIN)/tsx src/index.ts

smoke:
	@bash ./scripts/smoke.sh $(BASE_URL)

clean: db-down
