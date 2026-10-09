# Скіли до лекції 11.5

Тут лежать скіли, які використовуються в демонстраціях уроку. Це **сторонній код**, не частина
SDLC-плагіна курсу.

## `work-with-design-systems`

| | |
|---|---|
| Автор | Nataliia Bukhtiiarova |
| Джерело | https://github.com/natdexterra/work-with-design-systems |
| Ліцензія | MIT (текст у `work-with-design-systems/LICENSE`) |
| Знімок від | коміт `e94da52a21fddef9ffa122d5a64a70f1c84a2123` (2026-06-13) |
| Змінено для курсу | нічого, побайтова копія без каталогу `.git` |

Скіл працює з дизайн-системами у Figma і має два режими. **Inspect** робить read-only аудит:
WCAG-перевірки, скоринг готовності компонентів, пошук detached instances, генерація handoff-доків.
**Build** створює компоненти з привʼязкою до variables, веде slot-композицію замість detach-патернів,
пише структуровані описи, валідує результат і за окремим запитом експортує `tokens.css` та файл
AI-правил у твою кодову базу.

### Установка у власний проєкт

Копія з цього пакета:

```bash
cp -r skills/work-with-design-systems <твій-проєкт>/.claude/skills/work-with-design-systems
```

Або свіжа версія напряму від автора, вона може бути новішою за знімок вище:

```bash
git clone https://github.com/natdexterra/work-with-design-systems.git \
  .claude/skills/work-with-design-systems
```

Викликається командою `/work-with-design-systems`.

### Передумови

- підключений Figma MCP, рекомендований маршрут з лекції — remote server;
- скіл `figma-use`, він приїжджає разом із Figma-плагіном для Claude Code.

### Оновлення

Копія в цьому репозиторії заморожена на коміті вище і автоматично не оновлюється. Автор розвиває скіл
далі, тому за актуальною версією йди в першоджерело. Історія змін — `work-with-design-systems/CHANGELOG.md`.
