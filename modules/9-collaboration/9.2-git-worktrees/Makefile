# Demo 9.2 — Git worktrees. Builds a throwaway sandbox git repo with a small
# seed history (git + >=1 commit) so the worktree screencasts have a real repo
# to branch from. Nothing here needs ANTHROPIC_API_KEY for the base setup: the
# demo is driven interactively through Claude Code, not an API script. Live
# agent sessions (claude --worktree, subagents) need Claude Code itself.

.PHONY: sandbox reset clean serve

# Build a clean sandbox/ with seed history, .worktreeinclude, .env, helper, subagent.
sandbox:
	bash setup.sh

# Rebuild a clean sandbox from scratch (between takes).
reset: clean sandbox

# Remove the sandbox, any w-helper worktree siblings, and the bare origin.
clean:
	rm -rf sandbox
	rm -rf sandbox-*
	rm -rf .sandbox-origin.git

# Run the env-driven service on PORT from sandbox/.env (proves port isolation).
serve:
	cd sandbox && python3 app.py
