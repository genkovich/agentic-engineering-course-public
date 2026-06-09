# hello-plugin-converted

**Module:** 5 — Claude Code extended
**Lecture:** 5.5 — Plugins (скринкаст 6)

After-state конвертації standalone → plugin. Початкова точка — `../standalone-before/.claude/`, результат — ця тека. Чотири кроки міграції:

1. Створено маніфест `.claude-plugin/plugin.json` з `name: "hello-plugin"`
2. `commands/greet.md` — байт-у-байт копія зі `standalone-before/.claude/commands/`, лише шлях змінився
3. `skills/welcomer/SKILL.md` — так само, копія без змін
4. Блок `hooks` зі `standalone-before/.claude/settings.json` став кореневим обʼєктом `hooks/hooks.json`

Перевірка без install:

```bash
claude --plugin-dir ./hello-plugin-converted
```

Команда `/greet` тепер живе як `/hello-plugin:greet` — namespace додався автоматично з поля `name` у маніфесті.
