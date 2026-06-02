# 7.7 · TDD як execution discipline — demo + screencast

Demo-проект для лекції **7.7 TDD як execution discipline**
(Module 7 · Execution & Scale).

## Що це

Мінімальний snippets-stub для повного TDD-циклу через
**orchestrator-skill `/tdd` + 3 ізольовані agents**:

- **orchestrator** (`.claude/skills/tdd/SKILL.md`) — одна команда. Pre-flight checks, далі послідовно викликає 3 agents через Agent tool. Між фазами — automatic bash-gates (git log, pytest exit code, `git diff -- tests/`). На failure будь-якого gate — STOP з actionable error.
- **tdd-test-writer** (`.claude/agents/`) — окремий context. Читає AC, пише failing tests, фіксує red, комітить, ВИХОДИТЬ.
- **tdd-implementer** (`.claude/agents/`) — окремий context. Бачить лише failing tests і інтерфейс, пише мінімальну реалізацію, доводить до green.
- **tdd-refactorer** (`.claude/agents/`) — окремий context. Green tests + сирий код → витягає helpers, тести лишаються зеленими.

Спільний substrate — одна story `S-24 · SM-2 algorithm`. На відміну від 7.2 (де Ralph виконує абстрактний `slugify`), тут agent рахує наступний інтервал повторення за класичним SuperMemo-2.

Чому agents, а не skills: skill виконується inline у тому самому context window головного агента. Agent tool створює окреме context window. Тільки другий варіант дає реальний isolation, який лікує context pollution — головний аргумент Section 4 лекції 7.7.

У репозиторії `src/sm2.py` свідомо порожній (тільки `NotImplementedError`). Перший прогін `pytest` падає на всіх 11 кейсах — це teaching moment red-фази.

## SM-2 у двох реченнях

SM-2 (SuperMemo 2) — алгоритм spaced repetition, що приймає поточний стан картки (`repetitions`, `ease_factor`, `interval`) і оцінку відповіді користувача (0-5), а повертає новий стан з оновленим інтервалом у днях до наступного повтору. Якщо учень помилився (grade < 3) — інтервал скидається до 1 дня; якщо згадав (grade >= 3) — інтервал зростає за формулою `previous_interval * ease_factor`.

## Setup

```bash
cd modules/7-execution-scale/7.7-tdd-discipline
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest -q            # expected: 11 failures, всі на NotImplementedError
```

`NotImplementedError` — by design. Якщо хочеш bootstrap репо для запису з чистого state — нічого окремо робити не треба.

> Для `make mutation` і `make test-fast` потрібен dev-extra: `pip install -e ".[dev]"` (mutmut, pytest-watch, coverage). На Python 3.14 mutmut може бути несумісним — для запису скринкасту достатньо `pip install -e .`.

## Як запустити

| Команда | Що робить |
|---|---|
| `make test` | DoD-проба (`pytest -q`). Червоно на чистому checkout (NotImplementedError) — це стартовий стан. |
| `make demo` | Друкує кроки запуску синтетичного `/tdd story-24-sm2` через `claude` (slash-команда живе всередині `claude`, тож не авто-ран). |
| `make test-fast` | Re-run on file change (потрібен `pip install -e ".[dev]"`). |
| `make coverage` | Coverage report. |
| `make mutation` | Mutation testing через mutmut як sanity check. |
| `make clean` | Прибрати кеші (`.pytest_cache`, `.mutmut-cache`, `htmlcov`, `__pycache__`). |
| `make help` | Список таргетів. |

## Як записати Screencast #1 (~5 хв) — повний RGR цикл однією командою

```bash
# Pre-state: git status — чисте дерево, tests/ написані але red, src/sm2.py = NotImplementedError.
cd modules/7-execution-scale/7.7-tdd-discipline
git status
pytest -q             # 11 failing (8 example + 3 PBT) — усі на NotImplementedError
bat tasks/story-24-sm2.md   # показуємо AC (8 cases + 3 PBT invariants)

claude

# Step 1 (~30 сек) — одна команда.
/tdd story-24-sm2

# Step 2 (~3-4 хв) — orchestrator проганяє pipeline у своєму output:
#   Phase 1: tdd-test-writer (isolated context)…
#     → Agent tool call, прогрес test-writer-а
#     → Gate 1 check: git log shows test(sm2): commit; pytest exits 1 → PASS
#   Phase 2: tdd-implementer (isolated context)…
#     → Agent tool call, прогрес implementer-а
#     → Gate 2 check: pytest green; git diff -- tests/ empty → PASS
#   Phase 3: tdd-refactorer (isolated context)…
#     → Agent tool call, прогрес refactorer-а
#     → Gate 3 check: pytest green; tests/ untouched; ≥ 2 helpers → PASS
#   Pipeline complete. 3 commits: <SHA1> test, <SHA2> feat, <SHA3> refactor.

# Step 3 (~30 сек) — verify outcome.
git log --oneline -3
pytest -q                         # all green
git diff HEAD~3 HEAD -- tests/    # тести з RED фази не змінювались після GREEN/REFACTOR
```

Команди: `/tdd <story-id>` (orchestrator skill); внутрішньо викликаються `tdd-test-writer`, `tdd-implementer`, `tdd-refactorer` (agents у `.claude/agents/`).

**Augmented coding варіант** (Section 9 лекції): `/tdd story-24-sm2 --review-tests` — pipeline зупиняється після Gate 1, чекає на user перегляд `git show <RED_SHA>` і `continue` / `abort`.

> **Чесна примітка про стек.** `/tdd` skill із цього демо заточений під pytest/Python:
> його bash-gates перевіряють `pytest -q` exit code, а `tdd-test-writer` пише
> `tests/*.py` з Hypothesis. На іншому стеку (Go, TS, …) патерн **той самий**
> (red → green → refactor, `tests/` як незмінний контракт, 3 atomic commits
> `test:`/`feat:`/`refactor:`), але прогін тестів інший — треба замінити test-команду
> у gates skill-а (`pytest -q` → твій runner) і переписати test-writer під відповідний
> test-фреймворк. Це адаптація, а не запуск pytest-координатора «as is».

## Структура

```
7.7-tdd-discipline/
├── README.md                  # цей файл — огляд + setup
├── CLAUDE.md                  # конвенції: стек, тестовий контракт, mutmut
├── PROMPT.md                  # 3-section промпт для test-writer (Контекст / Завдання / DoD)
├── pyproject.toml             # Python 3.12, pytest, hypothesis, mutmut
├── Makefile                   # test, demo, coverage, mutation, clean, help
├── .gitignore                 # .venv/, __pycache__, .mutmut-cache
├── .claude/
│   ├── agents/                            # справжні isolated-context agents
│   │   ├── tdd-test-writer.md             # RED phase
│   │   ├── tdd-implementer.md             # GREEN phase
│   │   └── tdd-refactorer.md              # REFACTOR phase
│   └── skills/
│       └── tdd/SKILL.md                   # orchestrator /tdd <story-id>
├── tasks/
│   └── story-24-sm2.md        # AC + interface + GWT для SM-2
├── src/
│   ├── __init__.py
│   └── sm2.py                 # NotImplementedError stub
└── tests/
    ├── __init__.py
    ├── test_sm2.py            # example-based — 8 кейсів, initially failing
    └── test_sm2_properties.py # PBT з Hypothesis — 3 інваріанти, initially failing
```

## Гарантії

DoD циклу RGR:

- `pytest tests/` зелений після фази GREEN.
- `pytest tests/` лишається зеленим після фази REFACTOR.
- 3 atomic commits у `git log`: `test(...)`, `feat(...)`, `refactor(...)` — у цьому порядку.
- `tests/` не змінювалися після фази RED (перевір `git diff HEAD~2 HEAD -- tests/` — має бути пусто).

При запуску через `/tdd <story-id>` orchestrator перевіряє всі чотири пункти автоматично як Gate 1/2/3 — pipeline зупиняється з actionable error, якщо щось порушено. Ручна перевірка нижче потрібна лише якщо ти прогоняв agents окремо.

Як перевірити вручну після прогону:

```bash
pytest -q
git log --oneline -3
git diff HEAD~2 HEAD -- tests/    # лишається пустим
make mutation                      # optional: всі mutants killed
```

Якщо всі чотири — RGR-дисципліна збережена. Якщо `git diff` показує зміни в `tests/` після REFACTOR — refactorer порушив контракт, тести міняти не можна.

## Покриття концептів лекції

| Концепт лекції | Де у демо |
|---|---|
| RGR як одна команда | `/tdd story-24-sm2` (orchestrator skill) |
| Isolated context per phase | 3 agents у `.claude/agents/` (окремі context windows) |
| Tests як незмінний контракт | Gate 2/3: `git diff -- tests/` має бути пустим |
| 3 atomic commits як observability | `test(sm2):` → `feat(sm2):` → `refactor(sm2):` |
| PBT як safety net | `tests/test_sm2_properties.py` (Hypothesis, 3 інваріанти) |
| Mutation testing як sanity check | `make mutation` (mutmut проти `src/sm2.py`) |
| Augmented coding (human-in-the-loop) | `/tdd ... --review-tests` (STOP після Gate 1) |

## Як перенести у свій проєкт

1. Скопіюй `.claude/skills/tdd/` і `.claude/agents/tdd-*`.
2. Додай тонкий `CLAUDE.md` (стек + тестовий контракт + заборона міняти `tests/`) і story-файл із AC/GWT у `tasks/`.
3. `/tdd <story-id>`. Тримай DoD бінарним, а `tests/` — read-only для implementer/refactorer.
4. Інший стек (Go, TS, …) — заміни test-команду у gates skill-а і перепиши test-writer під відповідний test-фреймворк (див. «Чесну примітку про стек» вище).

## Sources

- SuperMemo SM-2 (Wozniak, 1985) — оригінальний алгоритм spaced repetition.
- Повний список — у `Sources.md` лекції 7.7.
