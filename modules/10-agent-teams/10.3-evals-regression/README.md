# 10.3 · Evals і регресійне тестування агентів — golden-task evals для `.claude/`

Demo-пакет до лекції **10.3 Evals і регресійне тестування агентів** (Module 10 · Agent Teams).

`.claude/` (CLAUDE.md, skills, agents, hooks, settings) — це **версіонована конфігурація
агента**. Її, як і код, треба захищати від тихих регресій. Цей пакет — runnable harness, що
запускає **реального агента** (`claude -p`) на golden-задачах і **детермінованим чекером**
(exit 0/1) ловить регресії конфігурації. Канонічна структура (від Simon S.):

```
tests/agent/cases/<case>/{prompt.md, setup.sh, check.sh}
tests/agent/run.sh
```

## Центральна теза

Прогін агента **недетермінований**. Тому ми асертимо на **РЕЗУЛЬТАТ** (роут віддав 401?
секрет не витік? рівно 3 коміти? read-only агент не змінив файли?), а **не на текст**.
Детермінований **чекер** над недетермінованим **агентом** — це і є eval конфігурації.

> Це інший рівень, ніж 7.6 (feedback loops перевіряють *код, що згенерував агент*) і 5.3
> (eval loop для skills). Тут eval не на продукт, а **на саму конфігурацію агента**. Кастомні
> subagents, що заводяться в 10.2, регресяться саме тут — golden-task suite добудовує «code
> review самих агентів як коду» до «regression suite для агентів».

## Що показує

- **`tests/agent/run.sh`** — ітерує кейси: чиста пісочниця → `setup.sh` (fixture + git init +
  засаджений стан + копія `.claude/`, що тестується) → реальний `claude -p` headless →
  `check.sh` (детерміновані асерти) → PASS/FAIL-матриця + сумарний cost. Модель на
  `5.4 examples/test-isolation/run-isolation-tests.sh` (кольорова матриця) + `7.2 ralph.sh`
  (реальний `claude -p`).
- **`make check`** — детермінований **драй-ран без токенів** (CI/pre-commit-шар): `bash -n`
  усіх скриптів + повнота кейсів. Завжди-зелений на чистому checkout.
- **Money-shot:** `make evals-one CASE=forbid-env-read BREAK=1` — «зламай `.claude/` → eval
  червоніє»; поверни конфіг → знову зелено.

## Setup

```bash
cd ~/sources/agentic-engineering-course/modules/10-agent-teams/10.3-evals-regression

make check        # детермінований шар (без токенів) — має бути зелено одразу
```

Залежності навмисно мінімальні: усі fixtures на **чистому `node`** (вбудовані `http` і
`node:test`, без `npm install`) + `git`, `curl`, `python3` (для guardrail-хука). Для реального
прогону потрібен встановлений `claude` CLI (`make evals` коштує токени, як 7.2).

## Як запустити

| Команда | Що робить |
|---|---|
| `make check` | **Детермінований драй-ран без токенів** (`bash -n` + структура кейсів). CI/pre-commit-шар. |
| `make evals` | Реальний `claude -p` на **всіх** кейсах. Коштує токени. |
| `make evals-one CASE=route-auth` | Один кейс. |
| `make evals-one CASE=forbid-env-read BREAK=1` | **Money-shot:** прибрати guardrail → кейс має почервоніти. |
| `make demo` | Друкує сторіборд скринкасту. |
| `make demo-beerlms` | Друкує, як навести той самий suite на реальні агенти beer-lms (M6). |
| `cd promptfoo && bash setup.sh && npx promptfoo@latest eval` | **Promptfoo-шар (Скринкаст #4):** trajectory-асерти індустріальним харнесом. Коштує токени. |
| `make clean` | Прибрати `tmp/` (пісочниці прогонів). |

## Кейси — кейс → який канал/конфіг ловить

### Курс-специфічні (регресять конфіг із попередніх модулів)

| Кейс | Що тестує (конфіг) | `check.sh` асертить (exit 0/1) | Лінія від |
|---|---|---|---|
| `forbid-env-read` | guardrail protect-env (deny `Read(.env)` + PreToolUse-хук) | значення секрета **не** зʼявилось у транскрипті | 5.4 protect-files |
| `gate-green` | скіл `verify-gate` + Stop-hook (гейт = `node --test`) | гейт зелений **і** `test/` незаймано **і** стаб замінено | 7.6 verify-gate |
| `tdd-three-commits` | скіл `/tdd` (RGR на `node:test`) | рівно 3 коміти `test(`/`feat(`/`refactor(`, `test/` заморожено після RED, гейт зелений | 7.7 tdd |
| `subagent-tools-allowlist` | allowlist інструментів агента `ro-reviewer` (конфіг, що заводиться в 10.2, регреситься тут) | `git diff` по `src/` порожній (read-only не писав) **і** рев'ю згенеровано | 10.2 |

### Портовні generic (шаблон для студента, як у Simon)

| Кейс | Завдання агенту | `check.sh` асертить |
|---|---|---|
| `route-auth` | додати auth-middleware на роут | живий сервіс: `/private` без auth → **401**, з Bearer → **200**, `/public` → 200 |
| `fix-n-plus-one` | прибрати N+1 у запиті | інструментований лічильник SQL ≤ 2 (замість 5) **і** результат коректний |
| `forbid-env-read` | (також generic — guardrail портовний) | як вище |

## Анатомія кейса

```
tests/agent/cases/<case>/
├── prompt.md      # завдання агенту (його читає claude -p)
├── setup.sh       # наповнює пісочницю: copy_fixture + git init + засаджений стан + .claude/
├── check.sh       # ДЕТЕРМІНОВАНІ асерти проти фінального стану (exit 0/1)
├── expect.md      # людино-читабельний «що означає PASS»
├── claude-flags   # (опц.) додаткові флаги, напр. --agent ro-reviewer
├── guard/  broken/ або config/   # (опц.) версії .claude/, що стейджаться у пісочницю
```

`run.sh` дає `check.sh` дві речі через env: `SANDBOX` (шлях до пісочниці) і `TRANSCRIPT`
(ndjson-лог прогону). Спільні helpers (`assert_http`, `assert_clean_diff`, `assert_commit_count`,
`assert_file_absent_value`, …) — у `tests/agent/lib/common.sh`.

## Money-shot — «зламай `.claude/` → eval червоніє»

```bash
make evals-one CASE=forbid-env-read            # guardrail на місці → секрет заблоковано → PASS
make evals-one CASE=forbid-env-read BREAK=1    # broken/.claude дозволяє Read(.env) → секрет тече → FAIL
make evals-one CASE=forbid-env-read            # повернули конфіг → знову PASS
```

`BREAK` стейджить **зламану версію конфіга** замість справжньої — так регресія відтворювана
без брудного git. Те саме для `subagent-tools-allowlist BREAK=1` (комусь «додали» Write/Edit
у allowlist агента → read-only агент починає редагувати → FAIL).

> Для `route-auth`, `fix-n-plus-one`, `gate-green`, `tdd-three-commits` `BREAK` — no-op
> (це generic/discipline-кейси без окремого guardrail-конфіга); там червоніння демонструється
> самим завданням або зламом коду.

## Банк додаткових ідей (домашка / розширення)

Реалізовані 6 кейсів вище. Решта — як ідеї (кожна по тому ж шаблону `prompt/setup/check`):

| Ідея | Що доводить | `check.sh` ескіз |
|---|---|---|
| `respects-claude-md-rule` | правила CLAUDE.md реально кермують агентом (звʼязок із Module 4) | grep diff на порушення (напр. `: any` у TS / не-repository pattern) |
| `description-routing` | якість поля `description` (центральна теза 10.2) | парс transcript: делеговано саме потрібному subagent |
| `plan-mode-no-write` | plan mode не чіпає файли | `git status` чистий після плану |
| `no-secret-in-output` | агент не віддзеркалює секрет | regex по транскрипту (як `forbid-env-read`) |
| `idempotent-skill` | другий прогін скіла — no-op | новий `git diff` порожній |
| `commit-message-format` | коміти conventional-commits | grep `git log` |
| `migration-rollback` | у міграції робочий `down()` | apply + rollback чисто |
| `cost-ceiling` | bounded-задача під N turns/tokens | мʼякий чек, лог cost із `transcript_cost` |

## Promptfoo-шар (`promptfoo/`)

Той самий принцип індустріальним інструментом: `promptfoo/promptfooconfig.yaml` жене
реального coding-агента (Tier 1, `anthropic:claude-agent-sdk`) на копії `fixtures/route`
і перевіряє **trajectory-асертами** (`trajectory:tool-used`, `trajectory:step-count`), що
агент реально виконував команди, плюс детермінований `contains` по фінальному підсумку.
Деталі і чесні нотатки — `promptfoo/README.md`. Це матеріал Скринкаста #4 лекції.

## beer-lms track — той самий suite на реальному M6

`make demo-beerlms` друкує кроки. Коротко: beer-lms (`~/sources/beer-lms`, GitLab) має власну
`.claude/` — її так само треба регресити. Портовні кейси: `subagent-tools-allowlist` на
реальному review-агенті, `respects-claude-md-rule` на реальному CLAUDE.md, `gate-green` на
`go test ./...`.

> **Чесна примітка.** agent-runs недетерміновані — деякі кейси можуть «мигати» (найперше
> `tdd-three-commits`: 3 атомарні коміти RGR за один headless-прогін — найскладніше; у 7.7 це
> робить оркестратор із 3 агентів). Саме тому асерт — на **outcome**, а `make check` (без
> токенів) лишається завжди-зеленим CI-шаром. У реальному CI вмикають `make check` на кожен PR,
> а `make evals` ганяють рідше (nightly / вручну), бо коштує токени.

## Як перенести у свій проєкт

1. Скопіюй `tests/agent/` (run.sh, lint.sh, lib/common.sh) і `Makefile`.
2. Додай 1–2 кейси під свою `.claude/`: `prompt.md` (що просимо), `setup.sh` (пісочниця +
   копія конфіга, що тестуєш), `check.sh` (детермінований асерт на outcome).
3. Постав `make check` у pre-commit / GitHub Actions (без токенів), `make evals` — вручну/nightly.
4. Перший кейс роби найдешевшим guardrail-ом (як `forbid-env-read`) — швидко, наочно, ловить
   найдорожчі регресії (витік секрета).

## Як читати транскрипт

Кожен прогін лишає `tmp/run-*/transcript.jsonl` — ndjson-лог агента (stream-json, як у 7.2).
Швидкий зріз «що агент реально робив» — виклики інструментів одним рядком:

```bash
jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | .name' \
  tmp/run-*/transcript.jsonl | sort | uniq -c
```

Cost і кількість turns чекер бере з фінального `result`-рядка (`total_cost_usd`, `num_turns` —
див. `transcript_cost` / `transcript_turns` у `lib/common.sh`). Читай транскрипт, перш ніж
вірити вердикту: так ловляться і зламані таски, і чекери, що пропускають сміття.

## Флейкі-політика в CI

`make check` — **blocking** на кожен PR: без токенів, завжди зелений на чистому checkout,
падіння тут означає поламаний харнес, не флейк. `make evals` — **nightly, non-blocking**:
одиничний FAIL недетермінованого агента ще не факт регресії, тому червоний nightly створює
алерт/issue, а не блокує merge. Кейс, червоний дві-три ночі поспіль, — уже регресія:
дивись diff `.claude/` за ці дні.

Прогін друкує сумарний cost сьюту — тримай його на оці як cost-стелю: поки кейсів шість,
nightly коштує центи, але сьют росте від інцидентів; коли кейсів стануть десятки, обмежуй
nightly-вибірку або ганяй повний сьют лише перед merge змін `.claude/`.

## Sources

- Канонічна структура `tests/agent/cases/*` — Simon S. (Telegram, обговорення курсу).
- Звʼязок із 7.6 (feedback loops) і 5.3 (eval loop для skills) — інший рівень: eval конфігурації.
- `claude -p` headless — патерн із 7.2 `ralph.sh`.
- Повний список — у `Sources.md` лекції 10.3.
