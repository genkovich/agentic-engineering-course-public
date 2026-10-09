# `_templates/` - переносні шаблони патернів Module 7

Стек-агностик заготовки патернів виконання з Module 7 (Execution & Scale). Кожен файл -
узагальнена версія відповідного демо: реальні значення замінені на плейсхолдери
`<UPPER_SNAKE>`, які ти підставляєш під свій стек. Жодної привʼязки до конкретного
проекту чи мови - переносиш у власний репозиторій і заповнюєш.

## Як користуватись (4 кроки)

1. **Скопіюй** потрібний файл у свій репозиторій (шлях призначення - у колонці нижче й у
   шапці кожного файлу).
2. **Заміни** всі плейсхолдери `<…>` під свій стек (повний список - у таблиці плейсхолдерів).
3. **Перевір синтаксис**: для bash - `bash -n <файл>`, для JS-workflow - `node --check <файл>`.
4. **Запусти**: Ralph - `./ralph.sh`; TDD - `/tdd <STORY_ID>`; workflow - через `/workflows`;
   hook спрацьовує сам на `git commit`; gate - `./verify-gate.sh`.

## Шаблони

| Файл | Патерн (лекція) | Що замінити |
|---|---|---|
| `ralph/ralph.sh` | Ralph loop (7.2) | нічого - стек-агностик, читає `PROMPT.md` |
| `ralph/PROMPT.template.md` | Ralph loop (7.2) | `<STACK>`, `<CODE_DIR>`, `<TEST_DIR>`, `<STORY_ID>`, `<TEST_CMD>` |
| `ralph/CLAUDE.template.md` | Ralph loop (7.2) | `<STACK>`, `<CODE_DIR>`, `<TEST_DIR>`, `<TEST_CMD>` |
| `goal/completion-condition.template.md` | `/goal` умова завершення (7.3) | `<TEST_PATH>`, `<TEST_CMD>`, `<N>` |
| `workflow/ship.template.mjs` | Dynamic workflows (7.4) | `<SCOPE>`, `<TEST_CMD>`, `<CODE_DIR>`, `<TEST_DIR>`, `<EXT>` |
| `tdd/SKILL.template.md` | TDD discipline (7.7) | `<TEST_CMD>`, `<TEST_DIR>`, `<CODE_DIR>` |
| `tdd/agents/test-writer.template.md` | TDD discipline (7.7) | `<TEST_CMD>`, `<TEST_DIR>`, `<CODE_DIR>`, `<SCOPE>` |
| `tdd/agents/implementer.template.md` | TDD discipline (7.7) | `<TEST_CMD>`, `<TEST_DIR>`, `<CODE_DIR>`, `<SCOPE>` |
| `tdd/agents/refactorer.template.md` | TDD discipline (7.7) | `<TEST_CMD>`, `<TEST_DIR>`, `<CODE_DIR>`, `<SCOPE>` |
| `verify/pre-commit.template.sh` | Feedback loops (7.6) | `<LINT_CMD>`, `<TEST_CMD>` |
| `verify/verify-gate.template.sh` | Feedback loops (7.6) | `<TEST_CMD>`, `<TEST_DIR>` |

## Плейсхолдери

| Плейсхолдер | Що це | Приклади |
|---|---|---|
| `<STACK>` | стек проекту | `Python 3.12 + pytest`, `Go 1.26`, `Node 22 + vitest` |
| `<TEST_CMD>` | команда тестів (повертає код 0 на зеленому) | `pytest -q`, `go test ./...`, `npm test` |
| `<LINT_CMD>` | команда лінтера | `ruff check .`, `golangci-lint run`, `npm run lint` |
| `<CODE_DIR>` | тека коду | `app`, `src`, `internal` |
| `<TEST_DIR>` | тека тестів | `tests`, `internal` |
| `<TEST_PATH>` | конкретний тестовий файл або тека | `tests/test_tags.py`, `src/tags.test.ts` |
| `<STORY_ID>` | ідентифікатор історії | `story-1`, `S-1` |
| `<SCOPE>` | domain-префікс (commit scope, назва набору) | `tags`, `auth` |
| `<EXT>` | розширення файлу твоєї мови | `py`, `go`, `ts` |
| `<N>` | стеля кількості ходів для `/goal` | `12` |

## Структура папок призначення

Коли переносиш у власний репозиторій, файли лягають так:

```
.
├── ralph.sh                 ← ralph/ralph.sh
├── PROMPT.md                ← ralph/PROMPT.template.md
├── CLAUDE.md                ← ralph/CLAUDE.template.md
├── .git/hooks/pre-commit    ← verify/pre-commit.template.sh (chmod +x)
├── scripts/verify-gate.sh   ← verify/verify-gate.template.sh (chmod +x)
└── .claude/
    ├── skills/tdd/SKILL.md           ← tdd/SKILL.template.md
    ├── agents/tdd-test-writer.md     ← tdd/agents/test-writer.template.md
    ├── agents/tdd-implementer.md     ← tdd/agents/implementer.template.md
    ├── agents/tdd-refactorer.md      ← tdd/agents/refactorer.template.md
    └── workflows/ship-<SCOPE>.mjs    ← workflow/ship.template.mjs
```

Умова завершення (`goal/completion-condition.template.md`) - це текстова довідка: бери
з неї готовий рядок `/goal …` і вставляй у термінал (окремий файл коду тут не потрібен).
