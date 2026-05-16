.PHONY: help verify verify-syntax verify-devcontainer verify-whitelist verify-sandbox verify-firewall test build rebuild clean clean-artifacts fmt lint

STARTER_NAME := rust-axum
TEST_CMD := cargo test

help:
	@echo "Targets:"
	@echo "  verify              Запустити всі security перевірки"
	@echo "  verify-syntax       JSON, bash syntax, devcontainer runArgs, whitelist consistency"
	@echo "  verify-devcontainer Перевірити devcontainer.json runArgs і postStartCommand"
	@echo "  verify-whitelist    Перевірити консистентність sandbox і init-firewall whitelists"
	@echo "  verify-sandbox      Перевірити що sandbox блокує cat .env (потребує Docker)"
	@echo "  verify-firewall     Перевірити firewall у devcontainer (тільки всередині контейнера)"
	@echo "  test                Запустити cargo test"
	@echo "  fmt                 cargo fmt"
	@echo "  lint                cargo clippy"
	@echo "  build               Зібрати Docker image"
	@echo "  rebuild             Перезібрати без cache"
	@echo "  clean               Прибрати containers і volumes (build artifacts: 'make clean-artifacts')"
	@echo "  clean-artifacts     Видалити локальні build артефакти через cargo clean"

verify: verify-syntax
	@echo ""
	@echo "=== Verify $(STARTER_NAME) ==="
	@if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then \
		$(MAKE) --no-print-directory verify-sandbox; \
	else \
		if [ "$${CI:-}" = "true" ]; then \
			echo "FAIL: Docker не запущений, у CI це fatal."; \
			exit 1; \
		else \
			echo "SKIP: Docker не запущений. Тільки syntax checks виконані."; \
		fi; \
	fi
	@echo ""
	@echo "=== Verify завершено ==="

verify-syntax:
	@echo "=== Syntax checks ==="
	@python3 -m json.tool < .claude/settings.json > /dev/null && echo "OK: .claude/settings.json valid"
	@python3 -m json.tool < .claude/settings.local.json.example > /dev/null && echo "OK: .claude/settings.local.json.example valid"
	@python3 -m json.tool < .devcontainer/devcontainer.json > /dev/null && echo "OK: .devcontainer/devcontainer.json valid"
	@bash -n .devcontainer/init-firewall.sh && echo "OK: init-firewall.sh syntax valid"
	@bash -n tests/sandbox-leak.test.sh && echo "OK: tests/sandbox-leak.test.sh syntax valid"
	@bash -n tests/firewall.test.sh && echo "OK: tests/firewall.test.sh syntax valid"
	@bash -n tests/validate-devcontainer.sh && echo "OK: tests/validate-devcontainer.sh syntax valid"
	@bash -n tests/validate-whitelist.sh && echo "OK: tests/validate-whitelist.sh syntax valid"
	@$(MAKE) --no-print-directory verify-devcontainer
	@$(MAKE) --no-print-directory verify-whitelist

verify-devcontainer:
	@bash tests/validate-devcontainer.sh

verify-whitelist:
	@bash tests/validate-whitelist.sh

verify-sandbox:
	@echo ""
	@echo "=== Sandbox leak test ==="
	@bash tests/sandbox-leak.test.sh

verify-firewall:
	@echo ""
	@echo "=== Firewall test ==="
	@bash tests/firewall.test.sh

test:
	@$(TEST_CMD)

fmt:
	@cargo fmt

lint:
	@cargo clippy --all-targets -- -D warnings

build:
	@docker compose build

rebuild:
	@docker compose build --no-cache

clean:
	@docker compose down -v 2>/dev/null || true

clean-artifacts:
	@if command -v cargo >/dev/null 2>&1; then \
		echo "cargo clean"; \
		cargo clean; \
	else \
		echo "cargo не доступний - скіпаю clean-artifacts"; \
	fi
