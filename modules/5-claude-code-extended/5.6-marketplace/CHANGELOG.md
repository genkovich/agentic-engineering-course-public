# Changelog

All notable changes to this marketplace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-05-09

### Added

- `security-scan` plugin: `/security-scan:scan` command and `scanner` skill — pre-push audit for hardcoded secrets, dangerous `eval`/`shell=True` calls, vulnerable dependencies, unvetted network destinations, and privilege escalation. Approver: `@acme/security-team`. Marketplace entry uses `strict: true` and `category: "security"`.

## [1.0.0] - 2026-05-09

### Added

- Initial release of the team marketplace.
- `deploy-checklist` plugin: `/deploy-checklist:check` command and `deploy-validator` skill.
- `pr-review-rules` plugin: `review-checker` skill enforcing team PR conventions.
