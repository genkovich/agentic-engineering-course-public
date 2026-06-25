# Demo: 9.5 Code review (локальний, у сесії)

**Module:** 9 - Collaboration
**Lecture:** 9.5 Code review з Claude — локальний прохід у сесії

## Що показує

Це fixture-демо: самодостатній крихітний Python-task-tracker (CLI поверх
JSON-файла, тільки stdlib) із власною git-історією. На гілці `feat/reminders`
лежить **PR-in-progress** із трьома навмисними дефектами — кожен націлений на
свій інструмент рев'ю. На цьому фікстурі знімаються обидва `🎬`-скринкасти
лекції 9.5.

`main` — чиста база (тест зелений). `feat/reminders` додає desktop-сповіщення
й дорогою заносить три дефекти (тест червоний). Локальний bare `origin` із
`main` робить гілку схожою на відкритий PR без мережі.

## Три навмисні дефекти (дифф `main...feat/reminders`)

| # | Дефект | Файл | Для якого інструмента | Пріоритет |
|---|---|---|---|---|
| 1 | **Off-by-one**: `due_within` бере строге `<` замість інклюзивного `<= days`, тож завдання рівно на межі вікна тихо випадає | `src/tasks/reminders.py` (`def due_within`) | `/code-review` | P1 |
| 2 | **Дублювання**: `format_short` — копія `format_line` із тим самим вкладеним if/elif-ладдером для рядка "when" | `src/tasks/model.py` (`def format_short`) | `/simplify` | P2 |
| 3 | **Command injection**: `notify_desktop` підставляє `task["title"]` прямо в `os.system("notify-send ... '%s'")` — назва завдання тече в шелл | `src/tasks/reminders.py` (`def notify_desktop`) | `/security-review` | P0 |

Дефект 1 ловить і `make test` (червоний). Дефекти 2 і 3 тест не бачить — їх
видно лише на рев'ю, тому вони й існують у цьому фікстурі.

## Pre-requisites

- Python 3.10+ (тільки stdlib, без pip-залежностей).
- git.
- [`codex`](https://github.com/openai/codex) CLI — **пререк запису** для кроку
  Codex-плагіна у SC#1 (`/codex:review` у сесії). Самій фікстурі для build/run
  не потрібен.

ANTHROPIC_API_KEY **не потрібен** для build/run: рев'ю виконує лектор
інтерактивно через Claude Code, не через API-скрипт.

## Як запустити

```bash
cd modules/9-collaboration/9.5-code-review

make sandbox        # base main (green) + feat/reminders (PR-in-progress, red)
make test           # RED на feat/reminders (off-by-one), GREEN на clean-baseline
make test-baseline  # довести, що clean-baseline зелений
make reset          # clean + sandbox: перебудувати чисто між дублями
make clean          # прибрати sandbox/ + bare origin
```

## Команди рев'ю (файли проєкту, не inline-промпти)

`template/.claude/` несе рев'ю як версіоновані артефакти проєкту:

- `commands/code-review.md` — проєктна обгортка над вбудованим `/code-review`
  (прохід коректності, P1).
- `commands/security-review.md` — **кастомізована копія** вбудованого
  `/security-review` під threat-model репо; її редагування показуємо в SC#2.
- `commands/codereview.md` — багатопрохідний оркестратор (без дефіса): гонить
  коректність → спрощення → безпеку й зводить за пріоритетом.
- `skills/code-reviewer-subagent/` — рев'юер у чистому контексті (адаптований з
  7.6): бачить лише `git diff` + AC PR, повертає ACCEPT/WARN/PARTIAL/REJECT.

Вбудовані `/code-review`, `/simplify`, `/security-review` Claude Code лектор
кличе як є; файли вище показують, що їх можна тримати й кастомізувати у проєкті.

## Мапа скринкастів

| Скринкаст | Секція лекції | Режим | Що показує |
|---|---|---|---|
| #1 Тур локального стеку + handoff | Секція 2 | `make sandbox` | `/code-review --comment` (постить у PR) · `/simplify` застосовує фікс → `git diff` · `/codex:review` (Codex-плагін у сесії) · свіжий прохід підбирає коментарі PR і застосовує `--fix` |
| #2 `/security-review` глибше | Секція 3 | `make sandbox` | `/security-review` ловить command injection; кастомізація через копію `security-review.md`; чесна межа — LLM-рев'ю не заміняє SAST/секрет-скан, їх комбінують |

## Recording runbook

1. `make reset` перед кожним дублем, щоб стартувати з ідентичного стану.
2. `cd sandbox` і запускай `claude` уже з кореня пісочниці, щоб агент брав
   `.claude/` і `CLAUDE.md` саме звідти. Активна гілка — `feat/reminders`.
3. Для `/code-review --comment` потрібен відкритий PR. Локальний bare origin не
   приймає `gh pr` — щоб показати інлайн-коментарі, або зведи `--comment` до
   стдаут-демо, або підстав реальний GitHub origin (як у 9.4) для цього кадру.
4. `make test` лишай у кадрі як «детермінований шар»: він ловить off-by-one
   (P1), але мовчить про injection (P0) і дублювання (P2) — звідси й потреба в
   рев'ю поверх тестів.

## Source

- Лекція 9.5 Code review (`Module 9 / Lecture 5`).
- Anthropic best practices: `/code-review`, `/simplify`, `/security-review`;
  субагент-рев'юер у чистому контексті.
- OWASP: command injection; принцип «LLM-рев'ю доповнює, не заміняє SAST».
