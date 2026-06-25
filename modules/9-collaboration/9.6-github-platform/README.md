# Demo: 9.6 GitHub platform (рев'ю на платформі)

**Module:** 9 - Collaboration
**Lecture:** 9.6 Code review на платформі: GitHub App, екосистема рев'юерів

## Що показує

На відміну від 9.1-9.5, це **не runnable sandbox**: інтеграція з платформою
вимагає живого GitHub-репо зі встановленими застосунками (Claude GitHub App,
Codex, Copilot). Тому 9.6 — **набір валідних шаблонів конфігів + runbook
запису**. Лектор кладе ці файли у власне репо й знімає на ньому чотири
`🎬`-скринкасти.

## Файли-шаблони

| Файл | Призначення | Хто читає |
|---|---|---|
| `.github/workflows/claude.yml` | GitHub Action: (a) `@claude` mention-режим + (b) авто-рев'ю PR (`prompt: /code-review`) | Claude GitHub App |
| `AGENTS.md` | Спільні правила рев'ю з пріоритетами P0/P1/P2 | Codex + Copilot (+ Claude) |
| `.github/copilot-instructions.md` | Кастомні інструкції Copilot | Copilot |
| `.coderabbit.yaml` | Конфіг CodeRabbit (`profile`, `path_filters`, `path_instructions`, `knowledge_base.learnings`) | CodeRabbit |
| `CLAUDE.md` | Правила проєкту для Claude (локально + в Action) | Claude |
| `planted-bug/` | Короткий файл з навмисним SQL-injection + опис, щоб відкрити PR під рев'ю | усі рушії |

## Pre-requisites (одноразовий bootstrap, робить лектор)

1. **Claude GitHub App.** У локальній сесії Claude Code виконай
   `/install-github-app` — це поставить App і додасть секрет
   `CLAUDE_CODE_OAUTH_TOKEN` у репо. (Альтернатива — `ANTHROPIC_API_KEY` у
   Settings → Secrets і відповідний інпут у workflow.)
2. **Copilot як рев'юер.** Переконайся, що `@copilot` доступний як reviewer у
   репо (Copilot enabled для організації/репозиторію).
3. **Codex automatic reviews.** Увімкни тумблер «Automatic reviews» у Codex для
   цього репо (щоб `@codex review` і авто-прохід працювали).
4. **CodeRabbit** (опційно, для контрасту 4-го рушія) — встанови застосунок на репо.

Жоден із цих кроків не потрібен для читання шаблонів; вони потрібні лише для
живого запису.

## Мапа скринкастів

| Скринкаст | Секція лекції | Що показує |
|---|---|---|
| #1 Setup + `@claude` | Секція 2 | `/install-github-app`; потім `@claude` у PR діє, і паралельно відпрацьовує review-job (`prompt: /code-review`) |
| #2 Контраст GitLab | Секція 3 | короткий `claude` CI-job у GitLab як вказівник; GitLab — окрема тема, тут лише легкий контраст |
| #3 Екосистема рев'юерів | Секція 4 | `@codex review` + `@copilot` на ТОМУ САМОМУ PR; спільний `AGENTS.md`; контраст із рев'ю Claude |
| #4 Безпека `@claude` | Секція 5 | дефолтні запобіжники: користувач без write не тригерить; PR відкривається за лінком |

Точні команди, pre-state і voice notes — у `screencast-prompts.md`.

## Чому не sandbox

`make sandbox` тут був би брехнею: `@claude`, `@codex review`, `@copilot` і
review-jobs живуть на стороні GitHub і потребують установлених застосунків +
секретів. Локально перевіряється лише те, що шаблони — валідні (YAML парситься,
ключі звірені зі схемами). Самі рев'ю записуються на живому репо за runbook.

## Source

- Лекція 9.6 GitHub platform (`Module 9 / Lecture 6`).
- `anthropics/claude-code-action@v1` (mention-режим + `prompt: /code-review`,
  `claude_args`, `claude_code_oauth_token`).
- `AGENTS.md` як спільний крос-туловий стандарт; Copilot custom instructions;
  CodeRabbit config schema v2.
