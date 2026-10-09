---
description: "Run a security scan over the staged diff and dependency manifests"
---

Run the team's pre-push security scan. Walk the user through each check and stop on the first hard blocker.

- Secrets: grep the staged diff for high-entropy tokens, `sk-`, `AKIA`, `xoxb-`, `BEGIN PRIVATE KEY`, and `.env`-style assignments
- Dangerous calls: search the diff for `eval(`, `exec(`, `os.system(`, `subprocess.*shell=True`, and `child_process.exec(` — flag every hit with file path and line number
- Dependency audit: run `npm audit --production` or `pip-audit` on the manifest changed in this branch; surface any high or critical advisories
- Network destinations: list every new outbound URL or hostname introduced in the diff and confirm it is on the team allowlist
- Privilege check: flag any new `sudo`, file writes outside the project root, or shell hooks that touch `~/.bashrc`, `~/.zshrc`, or system paths

If any item is red, refuse to mark the branch as push-ready and tell the user the exact remediation step.
