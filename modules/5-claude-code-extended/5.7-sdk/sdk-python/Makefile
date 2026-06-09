.PHONY: install demo-fixture clean help

VENV := .venv
PYTHON := $(CURDIR)/$(VENV)/bin/python
PIP := $(CURDIR)/$(VENV)/bin/pip
AGENT := $(CURDIR)/generate_release_notes.py

help:
	@echo "Targets:"
	@echo "  make install       - create venv and install claude-agent-sdk"
	@echo "  make demo-fixture  - run generate_release_notes.py against the deterministic fixture-repo"
	@echo "                       (the target the lecture screencast records)"
	@echo "  make clean         - revert any agent edits in fixture-repo + drop venv/__pycache__"

install:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install claude-agent-sdk

# Pre-requisites (checked inline, not as Make deps, so screencast does
# not get polluted by setup chatter):
#   - this venv must exist (run `make install` once)
#   - ../fixture-repo/ must exist with tags and unreleased commits
#     (run `bash ../setup-fixture.sh` once)
#
# We `cd ../fixture-repo` so the agent's Bash(git log *) calls resolve
# against the fixture's git history, and so the script sees docs/ at cwd.
demo-fixture:
	@if [ ! -x $(PYTHON) ]; then \
		echo "ERROR: sdk-python venv not found. Run: make install"; \
		exit 1; \
	fi
	@if [ ! -d ../fixture-repo/.git ]; then \
		echo "ERROR: fixture-repo not found. Run: bash ../setup-fixture.sh"; \
		exit 1; \
	fi
	@if [ ! -f ../fixture-repo/docs/CHANGELOG.md ]; then \
		echo "ERROR: ../fixture-repo/docs/CHANGELOG.md missing. Run: bash ../setup-fixture.sh --force"; \
		exit 1; \
	fi
	@cd ../fixture-repo && $(PYTHON) $(AGENT)

# Revert any agent edits + clear local caches.
clean:
	@if [ -d ../fixture-repo/.git ]; then \
		cd ../fixture-repo && git restore docs/CHANGELOG.md && rm -rf release-artifacts && echo "[clean] fixture-repo restored; release-artifacts/ removed"; \
	else \
		echo "[clean] fixture-repo not found — nothing to clean"; \
	fi
	rm -rf $(VENV) __pycache__ *.pyc
