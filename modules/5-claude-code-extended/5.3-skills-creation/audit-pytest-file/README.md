# Demo: audit-pytest-file skill

**Module:** 5 - Claude Code extended
**Lecture:** 5.3 - Створення власних Skills

## Що показує

Парний скіл до `audit-api-endpoint`, на тому ж патерні: один артефакт, один аудит. Тут артефакт — Python-тестовий файл, аудит — runtime probe через pytest.

- повний frontmatter (`name`, `description`, `allowed-tools`, `disable-model-invocation`, `context: fork`, `agent: Explore`, `argument-hint`)
- bundled script `audit_pytest.py` із PEP 723 заголовком (self-contained, без `requirements.txt`)
- delegation pattern: скіл не вшиває pytest, а викликає той, що стоїть у проєкті
- Gotchas section із runtime-specific підводними каменями (conftest, no-tests-as-finding, slow threshold, --report-log version)
- Output template (`templates/audit-report.md`)
- Checklist для multi-step workflow
- Mixed fragility (rigid pytest-команда vs flexible elicitation якщо файл не передано)

Скіл працює як runtime-only pytest probe: бере шлях до тесту, запускає pytest з `--report-log`, парсить JSON Lines і будує findings: failed tests, fixture errors, slow tests, empty files, all-skipped suites, collection errors.

`examples/` тримає bad/good пари — кожен `bad-*.py` спеціально ламає одну річ, кожен `good-*.py` має лише `info`-summary після probe.

## Pre-requisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) для PEP 723 self-contained запуску
- `pytest` 6.2+ + плагін `pytest-reportlog` (дає `--report-log`, без якого скіл не бачить структурного виводу). У `Makefile` дефолтний `PYTEST` — `uv run --with pytest --with pytest-reportlog pytest`, тож демо нічого додатково ставити не потребує. Для бойового вжитку додай `pytest-reportlog` у dev-deps проєкту або передай `--pytest "uv run pytest"` (якщо плагін уже є у твоєму venv).

## Як запустити

```bash
# демо за замовчуванням: probe на examples/good-fast-passing.py
make demo

# свій файл
make audit FILE=tests/test_users.py

# markdown-формат
make audit-markdown FILE=examples/bad-slow-test.py

# good приклади (мінімум findings)
make examples

# bad приклади (кожен ламає одну річ навмисне)
make examples-bad
```

Прямий запуск без Make:

```bash
uv run .claude/skills/audit-pytest-file/scripts/audit_pytest.py \
  --file tests/test_users.py
```

`uv` сам поставить залежності (їх тут немає, скрипт на stdlib) і запустить.

## Очікуваний output

JSON зі списком findings. Для `good-fast-passing.py` — лише info про summary. Для `bad-slow-test.py` — warning про повільний тест. Для `bad-failing-test.py` — error про failed assertion. Exit code: 0 якщо немає блокуючих findings (error/warning), 1 якщо є, 2 при помилці використання.

## Як ілюструє концепти лекції

| Концепт лекції | Де в demo |
|---|---|
| Bundled script | `scripts/audit_pytest.py` |
| PEP 723 self-contained | заголовок `# /// script` (stdlib only) |
| Wrap an existing tool | скіл делегує до проєктного `pytest`, не вшиває свою версію |
| `--help` як інтерфейс | `uv run scripts/audit_pytest.py --help` |
| Жодних інтерактивних промптів | usage error → exit 2 із підказкою на stderr |
| Корисні error messages | `bad-empty-file.py` → finding пояснює можливі причини |
| Структурований вивід | JSON Lines від pytest → JSON findings |
| Output truncation | `--full` для повного дампу, інакше топ-3 findings |
| Mixed fragility | flexible частина (запитати file якщо не передано) + rigid частина (точна команда у Step 3) |
| Templates | `templates/audit-report.md` |
| Checklist | блок Step 1..5 у `SKILL.md` |
| Validation loop | preflight → run probe → parse JSON → render |
| Plan-validate-execute | file existence + pytest --version у Step 2 перед probe у Step 3 |
| Gotchas | секція Gotchas у `SKILL.md` |

## Drop-in для свого проєкту

Скіл портативний — нічого з course-wrapper'а він не потребує. Скопіюй директорію скілу в personal scope:

```bash
cp -r .claude/skills/audit-pytest-file ~/.claude/skills/
```

Деталі — у `.claude/skills/audit-pytest-file/README.md` всередині скіл-директорії.

## Source

- Lecture 5.3 у курсі "Agentic Engineering з Claude"
- Claude Code Skills docs: https://code.claude.com/docs/en/skills
- pytest --report-log: https://docs.pytest.org/en/stable/how-to/output.html
- PEP 723: https://peps.python.org/pep-0723/
