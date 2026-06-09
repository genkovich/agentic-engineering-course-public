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

Ефемерний запуск — плагін живе тільки в цій сесії, нічого не встановлюється:

```bash
cd /path/to/5.5-plugins
claude --plugin-dir ./hello-plugin
```

В сесії: `/hello-plugin:greet` — побачиш namespace у дії.

## Локальне встановлення

Встановлення йде через marketplace, навіть для локальної теки — два кроки:

```bash
# 1. Зареєструвати теку як локальний marketplace
claude plugin marketplace add ./hello-plugin

# 2. Встановити плагін з нього
claude plugin install hello-plugin
```

Перевірити: `claude plugin list`. Видалити: `claude plugin uninstall hello-plugin`.

## Що показано в скринкастах

- **Скринкаст 1** (структура плагіна) — walk-through `plugin.json` і компонентів у file explorer
- **Скринкаст 2** (`--plugin-dir` + namespace) — поле `name` у маніфесті стає префіксом `/hello-plugin:greet`
