# scope-project-after

**Module:** 5 — Claude Code extended
**Lecture:** 5.5 — Plugins (скринкаст 3)

Це commit-ready state після `claude plugin install hello-plugin --scope project`.

Флаг `--scope project` записує плагін у `.claude/settings.json` проєкту — файл комітиться в git, і плагін вмикається у всієї команди. Без флагу install іде в `~/.claude/` — тільки для тебе.
