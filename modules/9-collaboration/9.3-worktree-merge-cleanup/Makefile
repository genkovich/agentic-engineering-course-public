# Demo 9.3 — Worktree merge + cleanup. Builds a throwaway sandbox git repo with
# two parallel worktree branches that edit the same line (so the second merge
# conflicts) plus one forgotten worktree for the cleanup demo. Nothing here needs
# ANTHROPIC_API_KEY for the base setup: the demo is driven interactively through
# Claude Code, not an API script. Live agent sessions need Claude Code itself.

.PHONY: sandbox reset clean serve

# Build the clean start state: seed history + bare origin + two conflicting
# worktree branches + one forgotten worktree + .worktreeinclude/.env.
sandbox:
	bash setup.sh

# Rebuild a clean start state from scratch (between takes).
reset: clean sandbox

# Remove the sandbox, the worktree siblings, and the bare origin.
clean:
	rm -rf sandbox
	rm -rf sandbox-*
	rm -rf .sandbox-origin.git

# Run the env-driven service on PORT from sandbox/.env.
serve:
	cd sandbox && python3 app.py
