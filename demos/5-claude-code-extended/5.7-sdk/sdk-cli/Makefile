.PHONY: demo-fixture clean help

help:
	@echo "Targets:"
	@echo "  make demo-fixture  - run release-notes.sh against the deterministic fixture-repo"
	@echo "                       (the target the lecture screencast records)"
	@echo "  make clean         - revert any edits the agent made in fixture-repo"
	@echo ""
	@echo "Direct script usage:"
	@echo "  cd ../fixture-repo && ../sdk-cli/release-notes.sh"

# Pre-requisites (checked inline, not as Make deps, so the screencast doesn't
# get polluted by setup chatter):
#   - ../fixture-repo/ must exist with a populated git history (tags + commits
#     since v1.1.0). Run `bash ../setup-fixture.sh` once before recording.
demo-fixture:
	@if [ ! -d ../fixture-repo/.git ]; then \
		echo "ERROR: fixture-repo not found. Run: bash ../setup-fixture.sh"; \
		exit 1; \
	fi
	@if [ ! -f ../fixture-repo/docs/CHANGELOG.md ]; then \
		echo "ERROR: ../fixture-repo/docs/CHANGELOG.md missing. Run: bash ../setup-fixture.sh --force"; \
		exit 1; \
	fi
	@cd ../fixture-repo && ../sdk-cli/release-notes.sh

# Revert any edits Claude left behind so the next run starts from a clean
# empty [Unreleased] section again.
clean:
	@if [ -d ../fixture-repo/.git ]; then \
		cd ../fixture-repo && git restore docs/CHANGELOG.md && echo "[clean] fixture-repo/docs/CHANGELOG.md restored"; \
	else \
		echo "[clean] fixture-repo not found — nothing to clean"; \
	fi
