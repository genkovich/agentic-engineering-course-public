# Demo 9.1 — Git workflow. Builds a throwaway sandbox git repo with a seed
# history so the lecture screencasts have a real repo to run on. Nothing
# here needs ANTHROPIC_API_KEY: the demo is driven interactively through
# Claude Code, not an API script.

.PHONY: sandbox arm reset clean test

# Build a clean sandbox/ with seed Conventional-Commit history + good-baseline tag.
sandbox:
	bash setup.sh

# Throw mixed uncommitted edits on top of the sandbox (commit/chunk/diff demos).
arm:
	bash scripts/arm-working-tree.sh

# Rebuild a clean sandbox from scratch (between takes).
reset: clean sandbox

# Remove the sandbox.
clean:
	rm -rf sandbox

# Run the pagination test inside the sandbox.
# Red at HEAD (planted bug), green at good-baseline.
test:
	cd sandbox/src && python3 -m unittest tests.test_pagination
