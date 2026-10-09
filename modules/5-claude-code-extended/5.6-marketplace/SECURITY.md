# Security Policy

Plugins published in this marketplace run with the user's full shell privileges. There is no sandbox. Treat every plugin as code you would merge into production.

## Review Policy

- Every plugin has a single named maintainer-approver listed in the plugin's `author` field.
- A pull request that adds or modifies a plugin requires that maintainer's approval before merge.
- Marketplace-level changes (`.claude-plugin/marketplace.json`, CI, this file) require any two maintainers.

## PR Checklist

Reviewers must confirm before approval:

- [ ] Hooks reviewed — every shell command and prompt is intentional and documented
- [ ] MCP destinations approved — any new MCP server endpoint is on the allowlist
- [ ] `bin/` audited — every binary or script is read end-to-end, no obfuscated payloads
- [ ] Env vars documented — every variable the plugin reads is listed in the plugin README
- [ ] Network calls justified — every outbound URL is named and the data sent is documented

## No Sandboxing

Plugins execute with the same privileges as the user running Claude Code. They can read any file the user can read, run any command the user can run, and reach any network the user can reach. Review accordingly.

## Reporting a Vulnerability

Email `security@your-org.example` with a description and reproduction steps. Do not open a public issue. Expect acknowledgment within two business days.

## Maintainer rotation

The platform team rotates marketplace maintainers quarterly. The current
maintainer list is published in the team handbook and mirrored in each
plugin's CODEOWNERS file. Rotation does not invalidate approvals on
in-flight PRs.
