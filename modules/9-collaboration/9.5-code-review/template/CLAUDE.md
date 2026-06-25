# CLAUDE.md

Project etiquette for this repo. Claude reads this on startup.

## Що це

Крихітний task-tracker (CLI поверх JSON-файла) — стек stdlib-Python, без
залежностей. Існує лише як полотно для рев'ю: на гілці `feat/reminders` лежить
PR-in-progress із трьома навмисними дефектами, які мають зловити рев'ю-команди.

## Git
- Коміти у форматі Conventional Commits: `type(scope): description`
  (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`).
- Гілки: `feat/<short-name>` або `fix/<short-name>`.
- Трейлер `Co-Authored-By: Claude <noreply@anthropic.com>` у комітах, які ти робиш.
- Ніколи не комітити `.env`. У репо лишається тільки `.env.example`.

## Review guidelines
- Пріоритети знахідок: **P0** — безпека й корупція даних; **P1** — логічні баги
  й регресії; **P2** — дублювання, читабельність, дрібні ризики.
- Перед мерджем мають бути чисті P0/P1. P2 — на розсуд автора.
- Секрети в коді — завжди P0. Неперевірений ввід у shell/SQL/шлях — завжди P0.
- Рев'ю LLM доповнює, а не заміняє детерміновані перевірки (тести, секрет-скан, SAST).
