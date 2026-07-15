.PHONY: agent-flow agent-show agent-create-issue agent-run agent-block-demo \
	verify clean help

COURSE_REPO ?= genkovich/course-project
MALICIOUS_ISSUE ?= 11

agent-flow:
	@sed -n '1,240p' production-agent/agent-flow.md

agent-show:
	@echo "=== 1. GitHub Actions workflow ==="
	@sed -n '1,260p' production-agent/github/issue-worker.yml
	@echo "\n=== 2. Agent rules ==="
	@sed -n '1,220p' production-agent/.claude/agents/issue-worker.md

agent-create-issue:
	@command -v gh >/dev/null || { echo "ERROR: install GitHub CLI first"; exit 1; }
	@gh auth status >/dev/null
	@gh issue create --repo "$(COURSE_REPO)" \
		--title "docs: add a short issue-worker demo note" \
		--label agent-ready \
		--body-file production-agent/demo-issue.md

agent-run:
	@command -v gh >/dev/null || { echo "ERROR: install GitHub CLI first"; exit 1; }
	@gh auth status >/dev/null
	@run_url="$$(gh workflow run issue-worker.yml --repo "$(COURSE_REPO)" --ref main)"; \
		echo "$$run_url"; \
		run_id="$${run_url##*/}"; \
		gh run watch "$$run_id" --repo "$(COURSE_REPO)" --exit-status

agent-block-demo:
	@gh issue edit "$(MALICIOUS_ISSUE)" --repo "$(COURSE_REPO)" \
		--remove-label agent-blocked --add-label agent-ready
	@$(MAKE) agent-run

verify:
	@test -s production-agent/github/issue-worker.yml
	@test -s production-agent/.claude/agents/issue-worker.md
	@test -s production-agent/demo-issue.md
	@ruby -e 'require "yaml"; YAML.load_file(ARGV[0])' \
		production-agent/github/issue-worker.yml
	@echo "PASS: GitHub worker materials"

clean:
	@rm -rf production-agent/__pycache__

help:
	@echo "GitHub-only lecture commands:"
	@echo "  agent-flow         show the worker diagram"
	@echo "  agent-show         show workflow and agent rules"
	@echo "  agent-create-issue create a safe issue with agent-ready"
	@echo "  agent-run          start GitHub Actions and follow the run"
	@echo "  agent-block-demo   requeue issue #11 and show agent-blocked"
	@echo "  verify             validate the teaching materials"
