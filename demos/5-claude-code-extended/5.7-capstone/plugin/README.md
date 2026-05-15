# {your-plugin-name}

Plugin екстракнутий з повторюваностей Phase A capstone. Автоматизує vertical slice фічі у scaffold з M4.12.

## Purpose

2-3 речення про конкретний pain point твого SaaS-scaffold, який цей плагін закриває.

## Install

```bash
claude plugins add github.com/<you>/<plugin-repo>
```

## Commands

- `/feature-plan <entity>` — generate plan for vertical slice
- `/feature-scaffold <entity>` — migration + handler + repo + tests stub
- `/feature-tests <entity>` — generate tests from handler signature
- `/feature-ship <entity>` — run tests, lint, prepare commit

## Skills

- `feature-scaffold` — triggered by «створи vertical slice для X» / «scaffold endpoint X»
- `feature-tests` — triggered by «згенеруй тести для handler X»

## Hooks

- `PreToolUse:Edit` — blocks imports across bounded contexts (BC integrity)
- `PostToolUse:Edit` — runs tests for the touched module
