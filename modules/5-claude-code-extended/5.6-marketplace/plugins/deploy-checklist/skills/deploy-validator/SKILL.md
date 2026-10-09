---
name: deploy-validator
description: >
  Use when validating that a service is ready to deploy. Triggers on
  "ready to deploy", "pre-deploy check", "can we ship", "deploy validation".
allowed-tools: Read, Bash, Grep
---

# Deploy Validator

Validate a service is safe to deploy before the engineer runs the release command.

## Workflow

1. Read `CHANGELOG.md` and confirm the top entry matches the version about to ship
2. Check the incidents tracker (or `INCIDENTS.md` if present) for open Sev1 or Sev2 affecting this service
3. Verify pending migrations have already been applied to staging — run `make migrate-status STAGE=staging` or equivalent
4. Confirm the rollback target image tag exists in the registry
5. Summarize findings as a green/yellow/red gate and list any blockers

If anything is red, refuse to approve the deploy and list the exact remediation steps.
