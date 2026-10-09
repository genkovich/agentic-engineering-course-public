.PHONY: verify apply alert-run alert-show legacy-verify help

TARGET ?= /path/to/course-project
REPO ?=
REPO_FLAG = $(if $(REPO),--repo $(REPO),)

verify:
	@bash scripts/verify-course-project-kit.sh

apply:
	@bash apply-to-course-project.sh "$(TARGET)"

# Trigger the alert-worker in the course-project repo and follow the run.
# Run from inside a course-project checkout, or pass REPO=owner/name.
alert-run:
	@gh workflow run alert-worker.yml $(REPO_FLAG)
	@sleep 4
	@gh run watch "$$(gh run list --workflow=alert-worker.yml --limit=1 --json databaseId --jq '.[0].databaseId' $(REPO_FLAG))" $(REPO_FLAG)

# Show recent alert-worker runs and the draft PRs it opened.
alert-show:
	@gh run list --workflow=alert-worker.yml --limit 5 $(REPO_FLAG)
	@gh pr list --label alert-worker --state all --limit 5 $(REPO_FLAG)

legacy-verify:
	@docker compose config -q
	@node --check victim-app/server.js
	@node --check agent/receiver.js
	@bash -n agent/run-issue.sh
	@bash -n duty/release-watch.sh

help:
	@echo "Lecture 11.2.1 — observability + AI"
	@echo "  make verify                  перевірити новий course-project kit"
	@echo "  make apply TARGET=/path      додати kit після Lecture 11.2"
	@echo "  make alert-run [REPO=o/n]    запустити alert-worker і стежити за run"
	@echo "  make alert-show [REPO=o/n]   показати runs alert-worker і draft PR"
	@echo "  make legacy-verify           перевірити historical standalone demo"
