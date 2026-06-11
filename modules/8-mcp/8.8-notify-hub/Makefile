PORT ?= 3334
BASE_URL ?= http://localhost:$(PORT)

.PHONY: run test seed clean

## run: dev-сервер на :3334 (webhook receiver + MCP endpoint)
run:
	npm run dev

## test: unit + e2e тести (vitest)
test:
	npm test

## seed: шле 3 фейкові CI/CD payload на /webhook (2 GitHub + 1 GitLab). Сервер має бути запущений (make run)
seed:
	@echo "→ GitHub pull_request (opened)"
	@curl -s -X POST $(BASE_URL)/webhook \
		-H "Content-Type: application/json" \
		-H "X-GitHub-Event: pull_request" \
		--data @examples/github-pr-opened.json; echo
	@echo "→ GitHub workflow_run (failure)"
	@curl -s -X POST $(BASE_URL)/webhook \
		-H "Content-Type: application/json" \
		-H "X-GitHub-Event: workflow_run" \
		--data @examples/github-workflow-run-failed.json; echo
	@echo "→ GitLab Pipeline Hook (failed)"
	@curl -s -X POST $(BASE_URL)/webhook \
		-H "Content-Type: application/json" \
		-H "X-Gitlab-Event: Pipeline Hook" \
		--data @examples/gitlab-pipeline-failed.json; echo
	@echo "→ Черга зараз:"
	@curl -s $(BASE_URL)/events | head -c 2000; echo

## clean: прибирає node_modules, build artifacts і локальні дані
clean:
	rm -rf node_modules dist data
