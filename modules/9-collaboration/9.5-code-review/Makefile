# Demo 9.5 — Code review. Builds a throwaway sandbox git repo whose feature
# branch `feat/reminders` carries a PR-in-progress diff with three planted
# defects, so the lecture screencasts have a real PR to review. Nothing here
# needs ANTHROPIC_API_KEY: the review is driven interactively through Claude
# Code (the `codex` CLI is a recorder prerequisite for the Codex-plugin step).

.PHONY: sandbox reset clean test test-baseline

# Build a clean sandbox/: baseline main (green) + feat/reminders (red) + bare origin.
sandbox:
	bash setup.sh

# Rebuild a clean sandbox from scratch (between takes).
reset: clean sandbox

# Remove the sandbox + its bare origin.
clean:
	rm -rf sandbox .sandbox-origin.git

# Run the reminders test on the current branch (feat/reminders by default).
# RED on feat/reminders (planted off-by-one), GREEN on clean-baseline.
test:
	cd sandbox/src && python3 -m unittest tests.test_reminders

# Prove the baseline is green: run the same test on the clean-baseline tag,
# then return to the feature branch. Single shell so the trap always restores.
test-baseline:
	@cur=$$(git -C sandbox rev-parse --abbrev-ref HEAD); \
	git -C sandbox checkout -q clean-baseline; \
	( cd sandbox/src && python3 -m unittest tests.test_reminders ); \
	rc=$$?; \
	git -C sandbox checkout -q "$$cur"; \
	exit $$rc
