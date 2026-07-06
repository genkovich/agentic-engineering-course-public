# Demo 10.2 — Custom Subagents (authoring focus). Builds a throwaway sandbox
# monorepo with two surfaces + six authored subagents, so the authoring
# screencasts (least-privilege, spawn-restriction, model comparison,
# auto-delegation, scope priority, persistent memory) have a real repo to run
# against. Nothing here needs ANTHROPIC_API_KEY for the base setup: the demos are
# driven interactively through Claude Code, not an API script. The demo-* targets
# only PRINT the recording runbook for a scenario — they never launch claude.

.PHONY: sandbox reset clean test help demo-a demo-b demo-c demo-d demo-e demo-f

help:
	@echo "Targets — 10.2 Custom Subagents (authoring demos):"
	@echo ""
	@echo "  sandbox   - build a clean sandbox/ monorepo (two surfaces + six subagents)."
	@echo "  reset     - clean + sandbox: rebuild from scratch between takes."
	@echo "  clean     - remove sandbox/."
	@echo "  test      - node --test inside sandbox (queue tests green)."
	@echo ""
	@echo "  demo-a    - print runbook: least-privilege (safe-researcher vs file-writer)."
	@echo "  demo-b    - print runbook: spawn restriction (two mechanisms)."
	@echo "  demo-c    - print runbook: model comparison (haiku vs opus bug-hunter)."
	@echo "  demo-d    - print runbook: auto-delegation (vague vs proactive description)."
	@echo "  demo-e    - print runbook: scope priority (project vs user, touches \$$HOME)."
	@echo "  demo-f    - print runbook: persistent memory (memory-keeper across sessions)."
	@echo ""
	@echo "  demo-* only PRINT the runbook from screencast-prompts.md — they do NOT run claude."

# Build a clean sandbox/ monorepo with seed history and two surfaces.
sandbox:
	bash setup.sh

# Rebuild a clean sandbox from scratch (between takes).
reset: clean sandbox

# Remove the sandbox repo.
clean:
	rm -rf sandbox

# Run the test suite inside the sandbox: queue tests pass (the bug is on an
# untested edge — that is the point of the model-comparison scenario).
test:
	cd sandbox && node --test

# --- demo-* : print the recording runbook for one scenario (no claude launch) ---

demo-a:
	@echo "== Сценарій (a) least-privilege — runbook =="
	@echo "Деталі й копі-пейст промпт: screencast-prompts.md → '🎬 Сценарій (a)'."
	@echo "Pre-state: cat sandbox/.claude/agents/safe-researcher.md sandbox/.claude/agents/file-writer.md"
	@echo "Дивимось: safe-researcher (disallowedTools: Write, Edit) фізично не пише — git diff порожній;"
	@echo "          file-writer (той самий prompt, без denylist) виправляє баг — git diff непорожній."

demo-b:
	@echo "== Сценарій (b) spawn restriction (ДВА механізми) — runbook =="
	@echo "Деталі: screencast-prompts.md → '🎬 Сценарій (b)'. Механізми РОЗВЕДЕНО окремими підрозділами."
	@echo "Механізм 1 (frontmatter allowlist типів): fixtures/spawn-allowlist/.claude/agents/lead-restricted.md"
	@echo "          -> claude --agent lead-restricted : може спавнити лише worker/researcher."
	@echo "Механізм 2 (settings.json глобальний deny): fixtures/spawn-deny/.claude/settings.json"
	@echo "          -> permissions.deny: Agent(Explore) : Explore не спавниться незалежно від активного агента."

demo-c:
	@echo "== Сценарій (c) model comparison — runbook =="
	@echo "Деталі: screencast-prompts.md → '🎬 Сценарій (c)'."
	@echo "Reasoning-таргет: packages/queue/consumer.js (баг дубль-requeue на межі MAX_RETRIES)."
	@echo "Дивимось: bug-hunter з model: haiku проти model: opus на цьому багу — точність проти вартості."

demo-d:
	@echo "== Сценарій (d) auto-delegation — runbook =="
	@echo "Деталі: screencast-prompts.md → '🎬 Сценарій (d)'."
	@echo "Порівняння: code-explainer-vague (description загальний) проти"
	@echo "            code-explainer-proactive (той самий prompt, description з 'use proactively' + тригер)."
	@echo "Дивимось: на природний запит користувача авто-делегування спрацьовує по-різному."

demo-e:
	@echo "== Сценарій (e) scope priority — runbook (ТОРКАЄ \$$HOME) =="
	@echo "Деталі: screencast-prompts.md → '🎬 Сценарій (e)'. Це ручний runbook, НЕ автоматизований таргет."
	@echo "УВАГА: сценарій копіює helper.md у \$$HOME/.claude/agents/ (реальний глобальний конфіг)."
	@echo "       ПІСЛЯ запису ОБОВ'ЯЗКОВО прибери: rm \$$HOME/.claude/agents/helper.md"

demo-f:
	@echo "== Сценарій (f) persistent memory — runbook =="
	@echo "Деталі: screencast-prompts.md → '🎬 Сценарій (f)'."
	@echo "Агент: memory-keeper (memory: project). Пише у .claude/agent-memory/memory-keeper/MEMORY.md."
	@echo "Дивимось: сесія 1 (окремий процес claude) пише спостереження; сесія 2 (НОВИЙ процес) їх читає."
