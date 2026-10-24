---
paths:
  - "infra/**/*.tf"
---

# Terraform rules

Завантажується для будь-якого `.tf` файлу під `infra/`. Покриває resource definitions, modules, state management.

## State and backends

- State lives in S3 with versioning enabled and a DynamoDB lock table. Local state is forbidden in main and release branches.
- Backend config is in `infra/backend.tf`. Never hardcode bucket names or regions in resource files.
- Workspaces map to environments: `dev`, `staging`, `prod`. Never run `terraform apply` against `prod` without a peer review.

## Resource naming and tags

- Every resource has these tags: `environment`, `owner`, `managed_by = "terraform"`, `cost_center`. Defined once in `locals.tf` and merged everywhere.
- Resource names use the pattern `{project}-{env}-{purpose}`: `claude-rules-demo-prod-api`, `claude-rules-demo-dev-db`.
- Logical resource addresses in `.tf` files use snake_case: `aws_s3_bucket.user_uploads`.

## Module structure

- Reusable modules live in `infra/modules/`. Environment-specific roots in `infra/envs/{dev,staging,prod}/`.
- Modules expose a minimal interface. Inputs only for things that genuinely vary per call - everything else is hardcoded inside.
- No `count` for optional resources when `for_each` would be clearer. `count = var.create ? 1 : 0` is a smell.

## Versioning

- Pin provider versions in `versions.tf`. Use `~>` for minor-version flexibility, exact pin for security-sensitive providers.
- Terraform CLI version pinned in `.terraform-version` for `tfenv`. CI uses the same version.

## What to avoid

- No `local-exec` provisioners. If you need imperative steps, write a separate script and run it outside Terraform.
- No secrets in `.tfvars` files. Pull from AWS Secrets Manager or SSM Parameter Store at runtime.
- No `ignore_changes` without a comment explaining why and pointing at the issue tracking the underlying drift.
