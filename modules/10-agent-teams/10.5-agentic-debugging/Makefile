# Demo 10.5 — Agentic Debugging. Builds a throwaway git repo (sandbox/) with 16
# seed commits of a tiny Node billing package. A regression is seeded at commit
# #9; reproduce.sh reproduces it with a plain exit 0/1, and `git bisect run`
# walks to the culprit in ~4 steps. Pure node + git, no ANTHROPIC_API_KEY, no npm
# install. The live agent take (writing reproduce.sh, driving the bisect) is
# recorded interactively in Claude Code — see screencast-prompts.md.

.PHONY: setup repro bisect clean

# Rebuild a clean sandbox/ with the 16-commit seed history.
setup:
	bash setup.sh

# Run reproduce.sh against HEAD. Expected: exit 1 (the bug is present on HEAD).
repro:
	@test -d sandbox || bash setup.sh >/dev/null
	@cd sandbox && bash ../reproduce.sh; ec=$$?; \
	  echo ""; \
	  if [ $$ec -eq 1 ]; then \
	    echo "reproduced on HEAD (exit 1) — this is the script to hand to git bisect"; \
	  else \
	    echo "expected exit 1 on HEAD, got $$ec"; \
	  fi; \
	  exit $$ec

# Full cycle: rebuild sandbox, git bisect run reproduce.sh, verify the found
# commit against the seeded .culprit, then reset. Prints PASS/FAIL.
bisect: setup
	@echo ""
	@echo "git bisect run over sandbox/ (16 commits, HEAD is bad, root is good)"
	@cd sandbox && \
	  first=$$(git rev-list --max-parents=0 HEAD); \
	  git bisect start HEAD $$first -- >/dev/null; \
	  git bisect run bash ../reproduce.sh 2>&1 | tee ../.bisect.log; \
	  found=$$(git rev-parse refs/bisect/bad); \
	  git bisect reset >/dev/null; \
	  steps=$$(grep -c "^running " ../.bisect.log); \
	  culprit=$$(cat .culprit); \
	  echo ""; \
	  echo "bisect iterations : $$steps"; \
	  echo "found  : $$(git rev-parse --short $$found)  $$(git log -1 --format=%s $$found)"; \
	  echo "seeded : $$(git rev-parse --short $$culprit)  $$(git log -1 --format=%s $$culprit)"; \
	  if [ "$$found" = "$$culprit" ]; then \
	    echo "PASS — git bisect found the seeded culprit (#9)"; \
	  else \
	    echo "FAIL — found commit does not match the seeded culprit"; \
	    exit 1; \
	  fi

# Remove the sandbox and the bisect log.
clean:
	rm -rf sandbox .bisect.log
