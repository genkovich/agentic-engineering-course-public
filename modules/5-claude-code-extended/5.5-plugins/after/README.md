# hello-plugin

**Module:** 5 — Claude Code extended
**Lecture:** 5.5 — Plugins: встановлення та використання

Мінімальний демо-плагін, який покриває все що обговорюється в лекції 5.5: маніфест, command, skill, hook, виконуваний `bin/`.

## Структура

```
hello-plugin/
├── .claude-plugin/
│   └── plugin.json         — маніфест: name, version, description, author
├── commands/
│   └── greet.md            — /hello-plugin:greet (plugin namespace)
├── skills/
│   └── welcomer/
│       └── SKILL.md        — universal onboarding skill
├── hooks/
│   └── hooks.json          — безпечний PreToolUse hook (локальний echo)
├── bin/
│   └── hello-bin           — приклад виконуваного файлу в $PATH
└── README.md
```

## Запуск без install (для розробки)

```bash
cd /path/to/lecture-5
claude --plugin-dir ./hello-plugin
```

В сесії: `/hello-plugin:greet` — побачиш namespace у дії.

## Локальне встановлення

```bash
cd hello-plugin
claude plugins add .
claude plugins list
```

## Що показано в скринкастах

- **Скринкаст 1** (структура плагіна) — `tree` + walk-through `plugin.json` і компонентів
- **Скринкаст 2** (локальне встановлення + namespace) — `claude plugins add .` і виклик `/hello-plugin:greet`
- **Скринкаст 3** (installation scopes) — `--scope project` + git diff на `.claude/settings.json`
- **Скринкаст 4** (`--plugin-dir` + `/reload-plugins`) — edit-test loop без рестарту
