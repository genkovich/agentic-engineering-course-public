# Локальні перевизначення (порти) — у .env поруч із цим Makefile.
# Той самий файл читає docker compose, тому порт міняється в одному місці.
-include .env
export

PGPORT       ?= 5432
HTTP_PORT    ?= 8080
DATABASE_URL ?= postgres://demo:demo@localhost:$(PGPORT)/demo?sslmode=disable
HTTP_ADDR    ?= :$(HTTP_PORT)
BASE_URL     ?= http://localhost:$(HTTP_PORT)

# Лінтер запускаємо через `go run pkg@version`, а не `go install`:
# бінар не треба класти в $PATH, а версія завжди та, що написана тут.
ARCH_LINT_VERSION ?= v1.17.0
ARCH_LINT         := go run github.com/fe3dback/go-arch-lint@$(ARCH_LINT_VERSION)

.PHONY: help doctor install db-up db-down db-migrate build run smoke \
        arch-lint-install arch-test arch-test-selftest arch-test-docker clean

help:
	@echo "Targets:"
	@echo "  doctor             Перевірити середовище (docker, go, порти)"
	@echo "  install            doctor + залежності + прогрів arch-lint"
	@echo "  db-up              Підняти postgres через docker compose"
	@echo "  db-down            Зупинити postgres і видалити том"
	@echo "  db-migrate         Накотити migrations/*.sql по порядку"
	@echo "  build              Зібрати бінар"
	@echo "  run                Запустити API на $(HTTP_ADDR)"
	@echo "  smoke              Смикнути 6 ендпоінтів, чекати 2xx"
	@echo "  arch-test          Прогнати go-arch-lint і go vet"
	@echo "  arch-lint-install  Один раз зібрати лінтер у кеш модулів"
	@echo "  arch-test-selftest Довести, що лінтер ловить навмисне порушення"
	@echo "  arch-test-docker   Запасний шлях без локального Go (див. TROUBLESHOOTING)"
	@echo "  clean              Зупинити docker, прибрати pgdata"

doctor:
	@bash ../../scripts/preflight.sh go 3

install: doctor
	go mod download
	@$(MAKE) --no-print-directory arch-lint-install

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
	go build -o bin/server .

run:
	DATABASE_URL=$(DATABASE_URL) HTTP_ADDR=$(HTTP_ADDR) go run .

smoke:
	@bash ./scripts/smoke.sh $(BASE_URL)

# Одноразовий крок: тягне і збирає лінтер у кеш модулів,
# щоб перший `make arch-test` не чекав на завантаження.
arch-lint-install:
	GOFLAGS= $(ARCH_LINT) version

arch-test:
	@ARCH_LINT_VERSION=$(ARCH_LINT_VERSION) bash ./scripts/arch-test.sh
	go vet ./...

# Негативний контроль: крихітний модуль із навмисним порушенням.
# Якщо лінтер його НЕ бачить — значить, лінтер зламався, а не код чистий.
arch-test-selftest:
	@ARCH_LINT_VERSION=$(ARCH_LINT_VERSION) bash ./scripts/archlint-selftest/run.sh

# Запасний шлях, якщо локального Go немає зовсім.
# Образ зібраний лише під amd64: на Apple Silicon іде через емуляцію і повільний.
arch-test-docker:
	docker run --rm --platform linux/amd64 -v "$(CURDIR)":/app -w /app \
		fe3dback/go-arch-lint:latest check

clean: db-down
