# Demo: hooks-toolkit

**Module:** 5 — Claude Code extended
**Lecture:** 5.4 — Hooks

## Що показує

Один проєкт, де **кожен hook з лекції живе в окремому файлі** — щоб у скринкасті можна було швидко переходити по них, посилаючись на слайди. Покриває:

- 4 must-know рецепти з лекції (auto-format, file-protection, secrets-scan, session-context);
- observability triade — tool trace, subagent lifecycle, prompt transcript (slide 8);
- analytics POST на mock FastAPI-style receiver через `curl` (slide 8);
- secrets stripping як shared sanitizer перед записом/відправкою;
- Telegram/macOS notification на permission/idle prompt;
- Stop quality gate як ілюстрація `decision: "block"` (вимкнено за замовчуванням);
- MCP allowlist через `mcp__.*__write.*` regex matcher (slide 11).

## Структура

```
hooks-toolkit/
├── README.md                       — цей файл
├── Makefile                        — make analytics / tail-trace / strip-demo / ...
├── .gitignore                      — logs + settings.local.json
├── .claude/
│   ├── settings.json               — ВСІ hooks увімкнені, кожен з _slide коментарем
│   ├── settings.local.json.example — шаблон env (ANALYTICS_URL, TELEGRAM_*)
│   └── hooks/
│       ├── recipe-1-auto-format.sh         (slide 6.1)
│       ├── recipe-2-protect-files.sh       (slide 6.2)
│       ├── recipe-3-secrets-scan.py        (slide 6.3, command-type → python3)
│       ├── recipe-4-session-context.sh     (slide 6.4)
│       ├── debug-tool-trace.sh             (slide 8 — async, pre/post)
│       ├── debug-subagent-lifecycle.sh     (slide 8 — async)
│       ├── debug-prompt-transcript.sh      (slide 8 — async, user/stop)
│       ├── secrets-strip.py                (shared sanitizer)
│       ├── analytics-send.sh               (slide 8 — async POST)
│       ├── notify-telegram.sh              (Notification → TG/macOS fallback)
│       ├── stop-quality-gate.sh            (slide 11 — ілюстрація decision:block)
│       └── mcp-allowlist.sh                (slide 11)
└── examples/
    ├── analytics-server/    — stdlib http.server :8090
    ├── debug-viewer/        — tail-* обгортки для логів
    ├── secrets-strip-demo/  — input-dirty.json + output-clean.json
    └── trigger-scenarios/   — копі-паст промпти для скринкасту
```

## Pre-requisites

- Claude Code CLI (`claude` у PATH)
- Python 3.10+
- `jq` (опціонально — красивіший tail; без нього просто JSONL рядки)
- `curl` (для analytics-send / Telegram)
- Optional: `prettier`, `black`, `gofmt`, `rustfmt` — щоб recipe-1-auto-format мав що викликати

## Quickstart — 4 рецепти за 30 секунд

Спочатку — без Claude. Перевір, що всі hook'и здорові:

```bash
cd hooks-toolkit
make test-hooks      # 8 fixtures × 5 hooks → кольорова PASS/FAIL матриця
make recipes-tour    # 4 рецепти з headers Recipe N/4, payload, hook, exit code
```

Якщо `make test-hooks` каже `All 8 tests passed.` і `make recipes-tour` — `Tour complete: 4/4 recipes pass.` — значить, скрипти, payload-и, формати — все ок. Можна йти у живу сесію:

```bash
claude
# усередині — копі-паст один з examples/trigger-scenarios/trigger-*.md
# (auto-format, protect, secret-scan, session-context, if-field)
```

Третій сценарій — pre-commit gate (Slide 7 + Slide 12 Variant D, копі-паст у власний репо):

```bash
make pre-commit-demo   # друкує крок-за-кроком інструкції для examples/pre-commit-demo/
                       # → cd examples/pre-commit-demo && npm install && git init
                       # → happy path і fail path на CRUD-сутності
```

Slide 5.5 «Test your hook in isolation» = `make test-hooks`. Slide 6 «4 ключові рецепти» = `make recipes-tour`. Slide 7 «Pre-commit paradox» + Slide 12 Variant D = `make pre-commit-demo` → `examples/pre-commit-demo/`. Slide 4 «matcher vs if» = `examples/trigger-scenarios/trigger-if-field.md`.

## Quick start

```bash
cd hooks-toolkit

# 1) (опція) налаштуй env для analytics + Telegram
cp .claude/settings.local.json.example .claude/settings.local.json
export ANALYTICS_URL=http://localhost:8090/events
# export TELEGRAM_BOT_TOKEN=...
# export TELEGRAM_CHAT_ID=...

# 2) термінал A — receiver
make analytics

# 3) термінал B — live trace
make tail-trace

# 4) термінал C — Claude
claude
# усередині сесії:
#   /hooks                    ← побачиш список усіх зареєстрованих
#   виконай будь-яку задачу   ← у А полетять events, у B — лінії tool-trace
```

## Прив'язка слайд → файл (для скринкасту)

| Slide | Тема | Файли |
|-------|------|-------|
| 2 | 6 hook events | `.claude/settings.json` (всі видні в одному файлі) |
| 3 | 4 типи hooks | секція "4 типи" нижче + `recipe-3-secrets-scan.py` (command/python), `analytics-send.sh` (command/curl) |
| 4 | Matchers + if | `.claude/settings.json`: `Edit\|Write`, `Edit\|Write\|MultiEdit`, `mcp__.*__write.*`, `permission_prompt\|idle_prompt`, `compact` |
| 5 | Exit codes + structured JSON | `recipe-2-protect-files.sh` (exit 2) vs `mcp-allowlist.sh` (exit 0 + JSON `permissionDecision: deny`) |
| 6.1 | Auto-format | `recipe-1-auto-format.sh` |
| 6.2 | File-protection | `recipe-2-protect-files.sh` |
| 6.3 | Secrets-scan | `recipe-3-secrets-scan.py` |
| 6.4 | Session re-inject | `recipe-4-session-context.sh` |
| 8 | Observability | `debug-tool-trace.sh` + `debug-subagent-lifecycle.sh` + `debug-prompt-transcript.sh` + `analytics-send.sh` + `examples/analytics-server/` + `examples/debug-viewer/` |
| 9 | Context economy | коментарі у `settings.json` (`async: true` для observability, без async для security gates); `stop-quality-gate.sh` як приклад anti-pattern якщо лізеш у quality gates через PostToolUse |
| 10 | Async + env vars | усі `.sh` використовують `"$CLAUDE_PROJECT_DIR"/.claude/hooks/...` |
| 11 | MCP allowlist | `mcp-allowlist.sh` + `mcp__.*__write.*` блок у settings.json |
| extra | Notification → TG | `notify-telegram.sh` |
| extra | Stop hook decision:block | `stop-quality-gate.sh` (вимкнений у settings, увімкнути для демо) |
| extra | Secrets stripping | `secrets-strip.py` + `examples/secrets-strip-demo/` |

## 4 типи hooks (slide 3)

`type` у настройках Claude Code приймає різні значення; цей демо ілюструє два найпоширеніші:

1. **command (shell)** — `recipe-1-auto-format.sh`, `recipe-2-protect-files.sh`, etc.
2. **command (interpreter)** — `python3 .../recipe-3-secrets-scan.py` (той самий type=command, але запускає Python).
3. **prompt-based hooks** — у цьому демо не використовуються, але можуть бути додані як `type: "prompt"` (Claude перевіряє через окремий промпт). Див. plugin-dev:hook-development skill.
4. **HTTP hook** — еквівалент того, що робить `analytics-send.sh` (curl POST). Показуємо як command + curl, бо це найбільш переносний варіант через `$CLAUDE_PROJECT_DIR`.

## Workflow для скринкасту

1. Відкрив `.claude/settings.json` — пройшовся по `_slide` коментарях.
2. Відкрив `recipe-2-protect-files.sh` → запустив `examples/trigger-scenarios/trigger-protect.md` → exit 2 у дії.
3. Відкрив `recipe-3-secrets-scan.py` → `trigger-secret-scan.md` → security warning у дії.
4. У трьох терміналах: receiver + tail-trace + claude → виконав `Edit foo.ts` → побачив events live.
5. Відкрив `secrets-strip.py` → `make strip-demo` → показав before/after.
6. Відкрив `mcp-allowlist.sh` → пояснив structured JSON output (slide 5 + 11).
7. Закрив `notify-telegram.sh` → попросив Claude дозвіл на щось → notification приходить.

## Verification (перед скринкастом)

1. `ls -l .claude/hooks/` — усі `.sh`/`.py` мають `+x`.
2. `cat .claude/settings.json | python3 -m json.tool` — валідний JSON.
3. `make strip-demo` — токени відсутні у виводі.
4. `python3 examples/analytics-server/server.py &` потім `echo '{"test":1}' | bash .claude/hooks/analytics-send.sh` → у консолі сервера зʼявляється pretty JSON.
5. `claude` всередині `hooks-toolkit/`, `/hooks` → бачимо:
   - SessionStart × 1 (recipe-4)
   - UserPromptSubmit × 1 (debug-prompt-transcript)
   - PreToolUse × 4 (protect-files, secrets-scan, debug-tool-trace, mcp-allowlist)
   - PostToolUse × 3 (auto-format, debug-tool-trace, analytics-send)
   - Stop × 1 (debug-prompt-transcript; stop-quality-gate disabled by default)
   - Notification × 1 (notify-telegram)
   - SubagentStart × 1, SubagentStop × 1
6. trigger-protect.md → exit 2 + Blocked.
7. trigger-secret-scan.md → Security Warning.
8. У другому терміналі `make tail-trace` під час сесії → JSON події летять live.

## Як адаптувати під свій проект

- Скопіюй `.claude/settings.json` + `.claude/hooks/` у свій репо.
- Видали те, що не потрібно (`stop-quality-gate.sh`, `mcp-allowlist.sh` якщо MCP не використовуєш).
- У `recipe-1-auto-format.sh` залиш тільки той форматер, який реально стоїть.
- Додай свої правила у `recipe-3-secrets-scan.py` `PATTERNS` (BC violations, internal API leaks, тощо).
- Включи `stop-quality-gate.sh` обережно — для більшості проєктів краще pre-commit hook (slide 9).

## See also

- Лекція 5.4 у Obsidian vault: `Own Brand/AI Course/Claude Course/Module 5/Lecture 4/Lecture 5.4 - Hooks.md`
- Lecture-3 demo (skills): `../../lecture-3/audit-api-endpoint/`
- Anthropic docs: `https://docs.anthropic.com/en/docs/claude-code/hooks`
