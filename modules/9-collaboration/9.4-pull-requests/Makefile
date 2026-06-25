# Demo 9.4 — Pull Requests. Builds a throwaway sandbox git repo with a seed
# history + a real `origin` on GitHub, so the lecture screencasts have a live
# repo to open PRs against. Nothing here needs ANTHROPIC_API_KEY: the demo is
# driven interactively through Claude Code, not an API script. It DOES need
# `gh auth login` for the remote modes (see README — one-time bootstrap).
#
# Set GH_DEMO_REPO= (empty) on any target for a network-free local build:
#   GH_DEMO_REPO= make sandbox

.PHONY: sandbox rules perms reset clean cleanup-prs test

# SC#1 — base repo + pushed feat/token-refresh + demo issue; no PR rules yet.
sandbox:
	bash setup.sh sandbox

# SC#2 — sandbox + PR template + `## Pull requests` in CLAUDE.md + fix-issue
#        skill + a 2nd branch feat/rate-limit (for the contrasting "second PR").
rules:
	bash setup.sh rules

# SC#3 — sandbox + .claude/settings.json (allow gh pr create / ask gh pr merge).
perms:
	bash setup.sh perms

# Rebuild a clean base sandbox from scratch (between takes).
reset: clean sandbox

# Remove the local sandbox/ (leaves the remote demo repo alone).
clean:
	rm -rf sandbox

# Close demo PRs + delete remote demo branches (reset the GitHub side).
cleanup-prs:
	bash cleanup.sh

# Run the token tests inside the sandbox (green on every branch).
test:
	cd sandbox/src && python3 -m unittest discover -s tests
