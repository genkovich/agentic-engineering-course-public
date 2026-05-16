# Demo: pdf-form-filler skill

**Module:** 5 - Claude Code extended
**Lecture:** 5.2 - Agent Skills: що це і як працює

## Що показує

Один наскрізний skill, який ілюструє ключові концепти лекції 5.2:

- **SKILL.md з виразливим description** - front-loaded use case + pushy enumeration ("Use when... Use even if user does not mention X")
- **Progressive disclosure у файлах** - SKILL.md тримається <100 рядків, важка частина - у `references/api-reference.md` і `references/error-catalog.md` з explicit triggers ("read X if Y")
- **Bundled scripts** - PEP 723 self-contained Python (`scripts/analyze.py`) і bash з `--help` + structured JSON output (`scripts/validate.sh`)
- **Plan-validate-execute pattern** - skill веде LLM через 5 кроків: discover → plan → validate → fill → verify
- **Output template** - `assets/report-template.md` для consistent звіту
- **Project-specific gotchas** - 4 конкретні підводні камені (XFA vs AcroForm, checkbox case-sensitivity, signature fields, read-only)

Skill заточений під AcroForm-PDF-форми. Працює навколо двох бібліотек: `pdfplumber` (для inspection) і `pikepdf` (для write-back).

`examples/` тримає sample form schema і value mapping які лекція 5.2 використовує у скрінкастах.

## Pre-requisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) для PEP 723 self-contained запуску
- bash 4+

PDF-бібліотеки (`pdfplumber`, `pikepdf`) встановлюються автоматично через PEP 723 заголовок у `scripts/analyze.py`. Не треба окремо `pip install`.

## Як запустити

```bash
# демо за замовчуванням: проаналізувати sample form, валідувати mapping
make demo

# тільки валідація (без аналізу)
make validate

# показати --help для validate.sh
make validate-help

# показати --help для analyze.py
make analyze-help
```

Прямий запуск без Make:

```bash
# Аналіз PDF (потребує справжню PDF-форму на вході)
uv run .claude/skills/pdf-form-filler/scripts/analyze.py examples/sample-form.pdf > form_fields.json

# Валідація mapping проти schema
bash .claude/skills/pdf-form-filler/scripts/validate.sh \
  examples/form_fields.json examples/field_values.json
```

## Очікуваний output

`analyze.py` друкує JSON-масив на stdout: `[{"name": "...", "type": "Tx|Btn|Ch|Sig", "required": false, "read_only": false, "options": null}, ...]`. Exit code 0 на успіх, 2 якщо PDF не fillable, 3 якщо потрібен пароль, 4 якщо XFA.

`validate.sh` мовчить при exit 0 (всі values map до known fields). При exit 2 друкує JSON-звіт `{"errors": [{"field": "...", "code": "...", "message": "..."}]}` з конкретними кодами помилок (`unknown_field`, `missing_required`, `type_mismatch`, `signature_field`, `read_only`, `option_not_in_list`).

## Як ілюструє концепти лекції

| Концепт лекції 5.2 | Де в demo |
|---|---|
| Skill = пакет експертизи (frontmatter + instructions) | `SKILL.md` з `name`, `description`, `allowed-tools` |
| Виразливий description | front-loaded "Fill PDF forms..." + pushy "Use when... when CI fails... when /usr/bin/env reports..." |
| Progressive disclosure у файлах | SKILL.md ~93 рядки, `references/api-reference.md` ~167 рядків, `references/error-catalog.md` ~79 рядків |
| Explicit triggers для references | "Read references/error-catalog.md if you see..." у SKILL.md |
| Bundled scripts | `scripts/analyze.py`, `scripts/validate.sh` |
| PEP 723 self-contained | `# /// script` блок у `analyze.py`, без `requirements.txt` |
| `--help` як інтерфейс | `bash scripts/validate.sh --help` показує structured help |
| Структурований вивід | JSON на stdout, errors на stderr |
| Meaningful exit codes | 0 success, 1 invalid args, 2 validation failed, 3 password needed, 4 XFA |
| Plan-validate-execute | Steps 1-5 у SKILL.md: analyze → map → validate → fill → verify |
| Project-specific gotchas | 4 gotchas у SKILL.md (XFA, checkbox, signature, read-only) |
| Output template | `assets/report-template.md` |
| Checklist | блок Steps 1-5 з `- [ ]` у SKILL.md |
| Validation loop | Step 3 → fix → rerun у SKILL.md |
| LLM-invoked skill | description з explicit phrases для auto-trigger |

## Як перенести у власний проєкт

```bash
# Як personal skill (доступний скрізь)
cp -r .claude/skills/pdf-form-filler ~/.claude/skills/

# Або як project skill у конкретному репо
cp -r .claude/skills/pdf-form-filler /path/to/your/project/.claude/skills/
```

Після цього у новому Claude Code session запусти `/skills` - побачиш `pdf-form-filler` у listing з його description.

## Source

- Lecture 5.2 у курсі "Agentic Engineering з Claude"
- Claude Code Skills docs: https://code.claude.com/docs/en/skills
- Agent Skills open standard: https://agentskills.io
- pdfplumber: https://github.com/jsvine/pdfplumber
- pikepdf: https://pikepdf.readthedocs.io/
- PEP 723: https://peps.python.org/pep-0723/
