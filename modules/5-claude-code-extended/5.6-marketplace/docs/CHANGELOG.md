# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-05-09

### Added

- Initial release of the team marketplace
- `deploy-checklist` plugin: `/deploy-checklist:check` command and `deploy-validator` skill for standardizing pre-deploy checks
- `pr-review-rules` plugin: `review-checker` skill enforcing team PR conventions
- `security-scan` plugin: `/security-scan:scan` command and `scanner` skill for pre-push secret and dependency audit
- GitHub Actions workflow `validate-plugins.yml` running marketplace schema check and per-plugin smoke install on every PR
