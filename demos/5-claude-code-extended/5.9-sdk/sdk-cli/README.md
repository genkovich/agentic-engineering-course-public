# sdk-cli — release notes generator через `claude -p`

**Module:** 5 — Claude Code extended
**Lecture:** 5.7 — Claude Agent SDK
**Demo:** Claude отримує git-репо з кількома релізними тегами і автоматично заповнює `## [Unreleased]` секцію у `docs/CHANGELOG.md` на основі комітів з останнього тегу.

Найпростіший спосіб задіяти повний agent loop із SDK — `claude -p` як subprocess. Цей demo показує не text generation, а реальну агентну роботу: модель сама читає існуючий CHANGELOG, читає git log між тегами, читає README для tone, редагує `docs/CHANGELOG.md` і повертає structured JSON.

## Що демонструє

- `claude -p "..."` — non-interactive виклик Claude Code з реальним 3-5 turn loop'ом (Read → Bash → Read → Edit → optional Read)
- `--allowed-tools "Bash(git log *)" "Read(docs/**)" "Edit(docs/**)"` — **три виміри prefix matching** в одному виклику: Bash, Read, Edit (показова security feature зі Slide 8)
- `--max-turns 6` — production guardrail для агентного loop'у (Slide 13)
- `--output-format json` + `--json-schema` — structured output валідований проти JSON Schema, не парситься з прози
- `--model claude-haiku-4-5` явно — release-notes pipeline це структурна задача (read → transform → write по schema), Haiku справляється і коштує в рази менше дефолтних Sonnet/Opus. Це Slide 13 practice у production-коді
- Trust model: агент редагує `docs/CHANGELOG.md` у working tree як *suggestion*. Скрипт **не** робить commit і **не** push. Reviewer вирішує `git restore`, `git commit` або `git apply` в іншу гілку
- Винесення промпта у `prompts/generate-release-notes.md` — редагування з підсвіткою синтаксису

## Структура

```
sdk-cli/
├── README.md
├── Makefile                                # ціль `demo-fixture` запускає agent на fixture-repo
├── release-notes.sh                        # головний скрипт з claude -p + allowed-tools + json-schema
├── prompts/
│   └── generate-release-notes.md           # задача для агента (workflow + constraints + JSON format)
└── examples/
    └── sample-changelog.diff               # типовий diff який агент створює на fixture
```

## Запуск

Потрібно: `claude` CLI у PATH, активна аутентифікація (`claude auth login` OAuth локально, або `ANTHROPIC_API_KEY` env var для CI/CD), `jq`, готовий `fixture-repo/` із git історією і тегами `v1.0.0` + `v1.1.0`.

```bash
# 1. Створити fixture (один раз)
bash ../setup-fixture.sh

# 2. Запустити agent — побачиш live agent loop у fixture-repo
make demo-fixture
```

`make clean` відновлює `docs/CHANGELOG.md` до початкового стану (`git restore`), щоб наступний запуск знову починався з порожньої `## [Unreleased]` секції.

Ручний виклик на власному проєкті:

```bash
cd /path/to/your/repo            # має бути git tags + docs/CHANGELOG.md

# Локально через OAuth-сесію:
claude auth login                # один раз, відкриє браузер
../sdk-cli/release-notes.sh

# Або через env var (наприклад, у CI):
ANTHROPIC_API_KEY=sk-... ../sdk-cli/release-notes.sh
```

## Recording the screencast

Цей demo записує Screencast 2 у `Lecture 5.7 - Claude Agent SDK.md` (Slide 10). Pre-flight перед першим take'ом:

```bash
# 1. Створити fixture (один раз)
cd ~/sources/agentic-engineering-course/demos/5-claude-code-extended/lecture-7/
bash setup-fixture.sh --force

# 2. Підтвердити стан fixture — обов'язкова перевірка перед записом
cd fixture-repo
git log v1.1.0..HEAD --oneline
# Очікуємо: 6 комітів (feat/feat/fix/fix/refactor/chore)
grep -A 1 "^## \[Unreleased\]" docs/CHANGELOG.md
# Очікуємо: один заголовок + порожня стрічка перед "## [1.1.0]"

# 3. Перевірити auth і env
# Або OAuth-сесія (локально), або ANTHROPIC_API_KEY (CI/CD) — скрипт приймає обидва шляхи
claude auth status --json | grep loggedIn      # очікуємо "loggedIn": true (локально)
# або:
echo $ANTHROPIC_API_KEY | cut -c1-7             # має почати з sk-ant (CI/CD)
claude --version
jq --version

# 4. Запустити demo
cd ../sdk-cli && make demo-fixture
```

`stderr` під час запуску містить:
- однорядковий summary з `cost`, `duration`, `turns`, `is_error`
- фінальний `git diff -- docs/CHANGELOG.md` — що саме агент змінив у working tree

`stdout` — structured JSON відповідно до схеми: `{version, release_date, sections: [{title, items}]}`.

> Variance — нормальна поведінка агентного систему. Trajectory (порядок tool calls, точне формулювання bullets) відрізнятиметься між запусками. Фінальний стан — заповнена `## [Unreleased]` секція з ~6 bullets — стабільний.

## Логіка агента (а не скрипта)

Скрипт сам по собі тривіальний: ~50 рядків guard'ів + один виклик `claude -p`. Цікаве відбувається **усередині** виклику — це 3-5 turn agent loop:

1. Агент сам читає `docs/CHANGELOG.md` (Read tool) → бачить що останній реліз `v1.1.0` і яким стилем оформлено секції
2. Запускає `git log v1.1.0..HEAD --oneline` (Bash tool) → отримує список з 6 комітів
3. Читає `docs/README.md` (Read tool) → розуміє що проєкт — CLI для URL-shortening, формулює bullets у відповідній лексиці
4. Edit `docs/CHANGELOG.md` (Edit tool) → додає Added/Changed/Fixed секції під `## [Unreleased]`
5. (Опційно) ще раз читає `docs/CHANGELOG.md` для self-verify
6. Повертає JSON відповідно до schema

Кожен з цих кроків — окремий **turn**. `--max-turns 6` дає буфер навіть якщо агент зробить додатковий read.

## Три виміри `--allowed-tools`

```
--allowed-tools "Bash(git log *)" "Read(docs/**)" "Edit(docs/**)"
```

Це не один параметр — це три **незалежні** allowlist'и:

| Dimension | Pattern         | Що дозволено                     | Що заблоковано                                  |
|-----------|-----------------|----------------------------------|-------------------------------------------------|
| **Bash**  | `git log *`     | `git log`, `git log --oneline`   | `git tag`, `git push`, `rm`, `curl`             |
| **Read**  | `docs/**`       | `docs/CHANGELOG.md`, `docs/README.md` | `src/main.py`, `.env`, `~/.ssh/id_rsa`     |
| **Edit**  | `docs/**`       | `docs/CHANGELOG.md`              | `src/main.py`, `pyproject.toml`, `.github/*`    |

Якби це був `Bash(git *)` — агент міг би push'нути на remote. Якби `Read(**)` — міг би прочитати `.env`. Кожна стрічка цього allowlist обмежує agent поведінку незалежним способом.

## JSON Schema validation

Замість `"сподіваємось що Claude поверне правильний формат"` — контракт на рівні CLI:

```bash
--output-format json \
--json-schema '{"type":"object","properties":{
  "version":      {"type":"string"},
  "release_date": {"type":"string"},
  "sections":     {"type":"array","items":{"type":"object","properties":{
                    "title":{"type":"string","enum":["Added","Changed","Fixed","Removed"]},
                    "items":{"type":"array","items":{"type":"string"}}
                  },"required":["title","items"]}}
},"required":["version","release_date","sections"]}'
```

Якщо Claude не зможе виконати завдання у відповідь structured JSON — `is_error=true` і `result` буде помилкою замість сирого тексту. У CI це різниця між «парсимо regex по природній мові» і «парсимо валідований JSON».

## Чому це важливо для CI/CD

Та сама структура виклику — `claude -p` + три-вимірний `--allowed-tools` + `--max-turns` + `--json-schema` — це готовий step для GitHub Actions / GitLab CI. У pipeline'і `on: push: tags: v*`:

1. Запускаєш `release-notes.sh` після створення тегу
2. Парсиш JSON у `gh release create` або `gh pr create` body
3. `git diff docs/CHANGELOG.md` постиш як PR comment для review
4. Reviewer apply'ить або вручну редагує

Повна інтеграція через `anthropics/claude-code-action` — у M9. Цей demo — фундаментальна одиниця, на якій будується вся ця інтеграція.

## Authentication

Скрипт приймає **обидва** шляхи аутентифікації — спершу перевіряє `ANTHROPIC_API_KEY`, потім падає на OAuth-сесію через `claude auth status --json`:

- **Локально (recommended for local dev):** `claude auth login` через OAuth із Max / Pro / Team підпискою. Один раз пройти браузерний flow — і скрипт працює без env var. Перевірка стану: `claude auth status --json` повертає `"loggedIn": true`.
- **CI/CD:** `ANTHROPIC_API_KEY` через GitHub Secrets / GitLab CI Variables / AWS Secrets Manager. OAuth тут неможливий — у headless runner'і нема браузера для login flow.

**Ніколи** не хардкодити `ANTHROPIC_API_KEY` у YAML чи в коді — build logs зберігають env vars.

## Adapter pattern для інших мов

Той самий subprocess контракт працює з будь-якої мови:

- **Go:** `exec.Command("claude", "-p", prompt, "--output-format", "json", "--json-schema", schema, "--allowed-tools", "Bash(git log *)", "--allowed-tools", "Read(docs/**)", "--allowed-tools", "Edit(docs/**)", "--max-turns", "6")`
- **Rust:** `std::process::Command::new("claude").args(["-p", prompt, ...])`
- **Ruby:** `` `claude -p '#{prompt}' --output-format json --json-schema '#{schema}'` ``
- **PHP:** `proc_open("claude -p ... --output-format json", ...)`

Контракт один — stdin/stdout/exit code. SDK існує для зручності у Python/TS, але CLI mode універсальний.

## Lecture link

`Own Brand/AI Course/Claude Course/Module 5/Lecture 7/Lecture 5.7 - Claude Agent SDK.md` — слайди 2, 8, 9, 10, 13, 14.
