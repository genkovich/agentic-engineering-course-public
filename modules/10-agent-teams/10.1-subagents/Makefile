# Demo 10.1 — Subagents. Builds a throwaway sandbox monorepo with a small seed
# history (git + commits carrying a Co-Authored-By: Claude trailer) so the
# subagent screencasts have a real, multi-surface repo to delegate exploration
# across. Nothing here needs ANTHROPIC_API_KEY for the base setup: the demo is
# driven interactively through Claude Code, not an API script. Live agent
# sessions (Agent tool, Explore subagents, ro-reviewer) need Claude Code itself.

.PHONY: sandbox reset clean test

# Build a clean sandbox/ monorepo with seed history and four search surfaces.
sandbox:
	bash setup.sh

# Rebuild a clean sandbox from scratch (between takes).
reset: clean sandbox

# Remove the sandbox repo.
clean:
	rm -rf sandbox

# Run the test suite inside the sandbox: billing/queue/auth pass, reports is
# intentionally flaky (the "find flaky tests" surface).
test:
	cd sandbox && node --test
