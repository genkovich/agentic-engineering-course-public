# sdk-python — Python orchestration around a Claude Agent SDK release-notes pipeline

**Module:** 5 — Claude Code extended
**Lecture:** 5.7 — Claude Agent SDK
**Demo:** Python скрипт обгортає той самий release-notes pipeline, що в sdk-cli, але додає pre-check git history, streaming progress, schema validation, commit-coverage check і apply'абельні artifacts — речі, де Python виборює над bash

Якщо `sdk-cli/release-notes.sh` — це чистий agent invocation, то цей скрипт — приклад **orchestration навколо** invocation. Pre-check git tags, streaming `AssistantMessage` events як live progress у stderr, post-processing (`git diff docs/CHANGELOG.md` → patch + release-notes.md), commit coverage check (чи всі коміти між тегами потрапили у release notes), mock `gh release create`.

## Що демонструє

- `from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage` — типобезпечні message events
- `ClaudeAgentOptions(allowed_tools=["Bash(git log *)", "Read(docs/**)", "Edit(docs/**)"], max_turns=6, model="claude-haiku-4-5")` — той самий sandbox що `--allowed-tools` у CLI, **три виміри prefix matching**
- `model="claude-haiku-4-5"` явно — release-notes pipeline це структурна задача (read → transform → write по schema), Haiku справляється і коштує в рази менше дефолтних Sonnet/Opus. Це Slide 13 practice у production-коді
- `async for message in query(...)` — streaming generator: бачиш агентні turns у real-time, а не блокуюче чекаєш фінал
- `isinstance(message, AssistantMessage)` vs `isinstance(message, ResultMessage)` — switch без рядкових порівнянь
- Python-side orchestration навколо виклику: pre-check `git tag`, `subprocess.run(["git", "diff"])`, persistence у `release-artifacts/<timestamp>/`, mock `gh release create`
- Trust-but-verify: JSON schema validation + commit-coverage check **після** агента, ловить випадки коли модель «забула» окремий коміт або порушила схему

## Структура

```
sdk-python/
├── README.md
├── Makefile                              # ціль `demo-fixture` запускає generate_release_notes.py
├── pyproject.toml                        # одна залежність: claude-agent-sdk
├── generate_release_notes.py             # головний модуль (async + orchestration)
└── examples/
    └── sample-release-artifacts.md       # приклад того що залишається у release-artifacts/ після запуску
```

Після запуску у fixture-repo з'являється:

```
fixture-repo/release-artifacts/
└── 2026-05-11-HHMMSS/
    ├── changelog.patch       # raw git diff (apply'абельний `git apply`)
    ├── release-notes.md      # human-readable rollup для `gh release create --notes-file`
    └── summary.md            # full report: метадані + JSON + diff в одному файлі
```

## Запуск

Потрібно: Python 3.11+, `claude` CLI у PATH, активна аутентифікація (`claude auth login` OAuth локально, або `ANTHROPIC_API_KEY` env var для CI/CD), готовий `fixture-repo/` з тегами `v1.0.0`, `v1.1.0` і unreleased комітами.

```bash
# 1. Створити sdk-python venv (один раз)
make install

# 2. Створити fixture (один раз)
bash ../setup-fixture.sh

# 3. Запустити демо
make demo-fixture
```

`make clean` відновлює `docs/CHANGELOG.md` і чистить `release-artifacts/`, щоб наступний запуск знову починався з порожньої `## [Unreleased]` секції.

## Windows

Makefile-таргети розраховані на macOS/Linux. На Windows ті самі кроки виконуються напряму — venv, install, запуск скрипта:

```powershell
# 1. Створити venv і встановити SDK (один раз; з теки sdk-python)
py -m venv .venv
.venv\Scripts\pip install claude-agent-sdk

# 2. Створити fixture (один раз)
python ..\setup_fixture.py

# 3. Запустити демо з fixture-repo як cwd
cd ..\fixture-repo
..\sdk-python\.venv\Scripts\python ..\sdk-python\generate_release_notes.py
```

Замість `make clean` — два кроки вручну (з `fixture-repo`):

```powershell
git restore docs/CHANGELOG.md
Remove-Item -Recurse -Force release-artifacts
```

Загальний гайд по Windows-середовищах для всього курсу — [WINDOWS.md](../../../WINDOWS.md) у корені репо.

## Recording the screencast

Цей demo записує Screencast 3 у `Lecture 5.7 - Claude Agent SDK.md` (Slide 11). Pre-flight перед першим take'ом:

```bash
# 1. Свіжий fixture
cd ~/sources/agentic-engineering-course/modules/5-claude-code-extended/5.7-sdk/
bash setup-fixture.sh --force

# 2. Підтвердити стан fixture — обов'язкова перевірка
cd fixture-repo
git log v1.1.0..HEAD --oneline
# Очікуємо: 6 комітів (feat/feat/fix/fix/refactor/chore)

# 3. sdk-python venv + sanity check
cd ../sdk-python && make install
.venv/bin/python -c "import claude_agent_sdk; print(claude_agent_sdk.__name__)"
# Auth: або OAuth-сесія (локально), або ANTHROPIC_API_KEY (CI/CD)
claude auth status --json | grep loggedIn   # очікуємо "loggedIn": true (локально)
# або:
echo $ANTHROPIC_API_KEY | cut -c1-7          # має почати з sk-ant (CI/CD)

# 4. Запустити demo
make demo-fixture
```

`stderr` під час запуску показує:
- `[pre-check] latest tag=v1.1.0, commits since=6` — підтверджуємо що є що описати
- `[agent] invoking Claude Agent SDK (max_turns=6)...`
- `[t=1] <80-char preview>` … `[t=N] <preview>` — кожен агентний turn з'являється по черзі (це **і є** видима частина agent loop'у)
- `[verify] schema OK`
- `[verify] all 6 commits represented` (або список missing, якщо щось пропущено)
- `[saved] patch    → release-artifacts/.../changelog.patch`
- `[saved] notes    → release-artifacts/.../release-notes.md`
- `[saved] summary  → release-artifacts/.../summary.md`
- `[would-run] gh release create v1.2.0 --notes-file ... --draft` — mock notification

`stdout` — structured JSON (`{version, release_date, sections}`) для downstream pipe'ів.

> Variance — нормальна поведінка агентного систему. Кількість `[t=N]` рядків і їх вміст відрізнятимуться між запусками. Фінальний стан і вміст `release-artifacts/<timestamp>/` — стабільні (sections структура, кількість bullets ±1).

## Логіка orchestration

1. **Pre-check** (`git tag --sort=-creatordate` + `git log <tag>..HEAD`) — якщо немає тегів або немає комітів з останнього тегу, виходимо без виклику Claude. Економимо токени.
2. **Agent loop** (`async for message in query(...)`) — streaming generator. Кожен `AssistantMessage` → `[t=N] <preview>` у stderr. `ResultMessage` → запам'ятовуємо `.result` як JSON string + metadata (`total_cost_usd`, `duration_ms`, `num_turns`).
3. **Parse + validate** — `json.loads()` на raw_result (агент може загорнути у ```json блок), потім `validate_against_schema()` перевіряє required fields і enum titles.
4. **Commit coverage check** — для кожного коміту з `git log <tag>..HEAD` перевіряємо чи його subject згаданий у JSON або у новому CHANGELOG. Catches "agent silently dropped commit #5".
5. **Persistence** (`release-artifacts/<timestamp>/changelog.patch + release-notes.md + summary.md`) — apply'абельний patch + ready-for-`gh-release` markdown + повний rollup.
6. **Notification** (`print("[would-run] gh release create v1.2.0 ...")`) — точка інтеграції. У production: `subprocess.run(["gh", "release", "create", ...])`.

## Чим Python виборює над bash

- **Streaming progress.** `AssistantMessage` events з'являються у real-time. У bash через `claude -p --output-format json` ти блокуючи чекаєш фінальний JSON.
- **Type safety.** `isinstance(message, AssistantMessage)` — IDE підказує доступні поля. У bash — `jq`-magic і сподівання.
- **Композиція.** Pre-check + parse + schema validation + commit coverage + persistence + mock notify — 6 кроків навколо одного agent call'у. У bash це можна, але код стає shell-heavy і важко тестується.
- **Stdlib навколо.** `pathlib`, `subprocess.run`, `datetime`, `json` — все вже є. Інтегрувати справжній `gh release create` це додавання `subprocess.run(["gh", ...])` на одну стрічку.

## TypeScript аналог

Той самий патерн, інший рантайм:

```typescript
import { query, AssistantMessage, ResultMessage } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: PROMPT,
  options: {
    allowedTools: ["Bash(git log *)", "Read(docs/**)", "Edit(docs/**)"],
    maxTurns: 6,
  },
})) {
  if (message.type === "assistant") {
    process.stderr.write(`[t=${++turn}] ${preview(message)}\n`);
  } else if (message.type === "result") {
    rawResult = message.result;
  }
}
```

Один нюанс: TS option keys у camelCase (`allowedTools`, `maxTurns`), Python — snake_case (`allowed_tools`, `max_turns`). Якщо команда на Node.js — використовуй TS SDK. Якщо Python — Python SDK. Якщо Go/Rust/Ruby — `claude -p` через subprocess (див. `sdk-cli/`).

## Authentication

Скрипт приймає **обидва** шляхи аутентифікації — спершу перевіряє `ANTHROPIC_API_KEY`, потім падає на OAuth-сесію через `claude auth status --json`:

- **Локально (recommended for local dev):** `claude auth login` через OAuth із Max / Pro / Team підпискою. `claude-agent-sdk` Python пакет викликає локальний `claude` бінарник через subprocess — тому той самий OAuth keychain доступний і у Python pipeline.
- **CI/CD:** `ANTHROPIC_API_KEY` через GitHub Secrets / GitLab CI Variables / AWS Secrets Manager. У headless runner'і нема браузера для OAuth login flow.

**Ніколи** не хардкодити `ANTHROPIC_API_KEY` у YAML чи у коді — build logs зберігають env vars.

## Lecture link

`Own Brand/AI Course/Claude Course/Module 5/Lecture 7/Lecture 5.7 - Claude Agent SDK.md` — слайди 5, 11, 13.
