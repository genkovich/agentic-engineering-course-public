# Demo 11.1 — Security red-team (exfiltration through the agent + egress guard).
#
# One injected ticket, one code surface, two configs. The attack/defend targets
# run a DETERMINISTIC stand-in (scripts/agent_sim.py) that mirrors what live
# `claude` does and honours the SAME PreToolUse hook contract (JSON on stdin,
# exit 2 = block). No ANTHROPIC_API_KEY needed — every outcome is reproducible.
# The demo-* targets only PRINT the recording runbook; they never launch claude.

.PHONY: sandbox reset clean redteam attack defend harden demo-exfil demo-harden help

# Build a clean sandbox/ (over-permissioned config + generated fake secret).
sandbox:
	bash setup.sh

reset: clean sandbox

clean:
	rm -rf sandbox

# Practice: run YOUR config through the "how could this be broken?" checklist.
redteam:
	@test -d sandbox || bash setup.sh >/dev/null
	@cd sandbox && bash scripts/redteam-scan.sh .

# Money-shot A: over-permissioned agent obeys the injected ticket and leaks the key.
attack:
	@test -d sandbox || bash setup.sh >/dev/null
	@cd sandbox && python3 scripts/agent_sim.py

# Copy the hardened structural-safety config into the sandbox (egress guard hook).
harden:
	@test -d sandbox || bash setup.sh >/dev/null
	@cp fixtures/hardened/.claude/settings.json sandbox/.claude/settings.json
	@echo "applied hardened .claude/settings.json (egress guard wired)"

# Money-shot B: SAME attack, hardened config — the egress guard blocks the leak.
defend: harden
	@cd sandbox && python3 scripts/agent_sim.py

# Screencast #1 — live exfiltration through `claude` (PRINTS runbook only).
demo-exfil:
	@echo "SCREENCAST #1 — exfiltration through the agent (over-permissioned)"
	@echo "  live, in sandbox/:"
	@echo "    claude   # then: 'триаж нового тикета у issues/incoming'"
	@echo "  the over-permissioned agent obeys the hidden note, reads .env,"
	@echo "  and issues an outbound curl with the key in the URL."
	@echo ""
	@echo "  deterministic stand-in (no tokens): make attack"

# Screencast #2 — same attack, hardened config (PRINTS runbook only).
demo-harden:
	@echo "SCREENCAST #2 — structural safety on egress blocks the same attack"
	@echo "  live, in sandbox/ after: make harden"
	@echo "    claude   # same prompt as #2"
	@echo "  the PreToolUse egress guard denies the outbound call (exit 2)."
	@echo "  read-deny alone would NOT have held (bash bypass, 3.6/3.7)."
	@echo ""
	@echo "  deterministic stand-in (no tokens): make defend"

help:
	@echo "targets:"
	@echo "  sandbox      build sandbox/ (over-permissioned config + fake secret)"
	@echo "  redteam      audit the config against the red-team checklist"
	@echo "  attack       exfiltration through the agent -> EXFILTRATED"
	@echo "  harden       apply the hardened structural-safety config"
	@echo "  defend       same attack, hardened config -> BLOCKED"
	@echo "  demo-exfil   Screencast #2 runbook (PRINTS ONLY)"
	@echo "  demo-harden  Screencast #3 runbook (PRINTS ONLY)"
	@echo "  reset/clean  rebuild / remove sandbox/"
