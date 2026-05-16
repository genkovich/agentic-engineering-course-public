# Demo: audit-api-endpoint skill

**Module:** 5 - Claude Code extended
**Lecture:** 5.3 - Створення власних Skills

## Що показує

Один наскрізний skill, який ілюструє ключові концепти лекції 5.3:

- повний frontmatter (`name`, `description`, `allowed-tools`, `disable-model-invocation`, `context: fork`, `agent: Explore`, `argument-hint`)
- inline команда `curl` поряд із bundled script
- bundled script `audit_endpoint.py` із PEP 723 заголовком (self-contained, без `requirements.txt`)
- Gotchas section із runtime-specific підводними каменями (TLS, auth, non-2xx-as-correct)
- Output template (`templates/audit-report.md`)
- Checklist для multi-step workflow
- Validation loop (script запускається, перевіряє свій вивід, проектує наступний крок)
- Mixed fragility (rigid command vs flexible URL elicitation)

Skill працює як runtime-only HTTP probe: бере повний URL і робить один GET. Перевіряє статус, `Content-Type`, валідність body, cache-заголовки, патерн uptime-only health. Мова- і фреймворк-агностично — на тому ж UI агент може аудитити Go, Node, Python, Rust або будь-який інший HTTP-сервер.

`examples/` тримає bad/good пари, які лекція 5.3 використовує у секції про дизайн скриптів для агента.

## Pre-requisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) для PEP 723 self-contained запуску
- HTTP-сервер що відповідає на якийсь URL (наприклад `starters/go-chi/` запущений локально на `:3000`, або будь-який публічний endpoint)

## Як запустити

```bash
# демо за замовчуванням: probe http://localhost:3000/health
make demo

# свій URL
make audit URL=https://api.github.com/zen
make audit URL=http://localhost:8080/health

# markdown-формат
make audit-markdown URL=https://example.com

# good приклади (працюють)
make examples

# bad приклади (зламані навмисне)
make examples-bad
```

Прямий запуск скрипта без Make:

```bash
uv run .claude/skills/audit-api-endpoint/scripts/audit_endpoint.py \
  --url https://api.example.com/health
```

`uv` сам поставить залежності (їх тут немає, скрипт на stdlib) і запустить.

## Очікуваний output

JSON зі списком findings. Для `https://example.com` — лише info про latency. Для `/health`-стилю endpoint, що повертає `OK` — info про uptime-only health. Exit code: 0 якщо немає блокуючих findings (error/warning), 1 якщо є, 2 при помилці використання.

## Як ілюструє концепти лекції

| Концепт лекції | Де в demo |
|---|---|
| Inline команда у SKILL.md | `curl -sf -m 5 -o /dev/null -w "%{http_code}\n" "$0"` у Step 2 |
| Bundled script | `scripts/audit_endpoint.py` |
| PEP 723 self-contained | заголовок `# /// script` у тому ж файлі |
| Жодних інтерактивних промптів | `examples/bad-interactive.py` vs `examples/good-cli-flags.py` |
| `--help` як інтерфейс | `uv run scripts/audit_endpoint.py --help` |
| Корисні error messages | `examples/bad-error-message.txt` vs `good-error-message.txt` |
| Структурований вивід | `examples/bad-prose-output.py` vs `good-structured.py` |
| Output truncation | `--full` для повного дампу, інакше топ-3 findings |
| Mixed fragility | flexible частина (запитати URL якщо не передано) + rigid частина (точна команда у Step 3) у `SKILL.md` |
| Templates | `templates/audit-report.md` |
| Checklist | блок Step 1..5 у `SKILL.md` |
| Validation loop | parse JSON → group → render → iterate |
| Plan-validate-execute | `curl` reachability check у Step 2 перед повним probe у Step 3 |
| Gotchas | секція Gotchas у `SKILL.md` |

## Drop-in для свого проєкту

Скіл портативний — нічого з course-wrapper'а він не потребує. Скопіюй директорію скілу в personal scope:

```bash
cp -r .claude/skills/audit-api-endpoint ~/.claude/skills/
```

Деталі — у `.claude/skills/audit-api-endpoint/README.md` всередині скіл-директорії.

## Source

- Lecture 5.3 у курсі "Agentic Engineering з Claude"
- Claude Code Skills docs: https://code.claude.com/docs/en/skills
- Subagents docs: https://code.claude.com/docs/en/sub-agents
- Agent Skills open standard: https://agentskills.io
- PEP 723: https://peps.python.org/pep-0723/
