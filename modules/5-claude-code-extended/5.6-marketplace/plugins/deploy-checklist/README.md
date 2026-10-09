# deploy-checklist

## Purpose

Standardize the pre-deploy gate across all services so every engineer runs the same checklist before shipping. Removes ambiguity and prevents the "I forgot to run migrations" class of incidents.

## Install

```
/plugin install deploy-checklist@team-marketplace
```

## Commands

- `/deploy-checklist:check <service>` — runs the five-item pre-deploy checklist for the named service.

## Skills

- `deploy-validator` — auto-triggers when the user says things like "ready to deploy" or "pre-deploy check". Reads CHANGELOG, checks incidents, verifies migrations on staging, confirms rollback target, returns a go/no-go gate.

## Hooks

—
