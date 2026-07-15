---
name: prepare-vps-deploy
description: Prepare and verify the repository files required to deploy this Next.js project to one Ubuntu VPS with Docker Compose and a GitHub self-hosted runner. Use when creating or reviewing Dockerfile.production, compose.vps.yml, the health route, persistent SQLite storage, or deploy-vps.yml before a VPS release.
---

# Prepare VPS Deploy

Treat the repository as the source of truth. Do not connect to the VPS, register
a runner, push a branch, or start a deployment.

## Workflow

1. Read `package.json`, `next.config.*`, `lib/db.ts`, the production Dockerfile,
   Compose file, health route, and deploy workflow.
2. Confirm SQLite uses `process.env.DB_PATH` with a local fallback.
3. Confirm the Compose volume is mounted at the same directory used by
   `DB_PATH` and that the healthcheck calls `/api/health`.
4. Confirm the workflow runs only on trusted `main` or `workflow_dispatch`, uses
   the `course-vps` runner label, pins third-party actions by full commit SHA,
   and performs a deterministic healthcheck.
5. Confirm images use explicit versions and that no secret or `.env.vps` file is
   committed.
6. Run `bash .claude/skills/prepare-vps-deploy/scripts/verify-deploy.sh`.
7. If a check fails, make the smallest repository-only fix and run it again.
8. Return changed files, checks run, and remaining manual VPS steps.

## Safety boundaries

- Never run `docker compose down -v`.
- Never add a `pull_request` trigger to the production deploy job.
- Never request or print the root password or runner registration token.
- Never grant the AI Docker socket, SSH credentials, or automatic rollback.
- Stop after repository verification; a human reviews and merges the workflow.
