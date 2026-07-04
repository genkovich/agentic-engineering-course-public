# 10.3 · Evals і регресійне тестування агентів - golden-task evals для `.claude/`

Demo-пакет до лекції **10.3 Evals і регресійне тестування агентів** (Module 10 · Agent Teams).

`.claude/` (CLAUDE.md, skills, agents, hooks, settings) - це **версіонована конфігурація
агента**. Її, як і код, треба захищати від тихих регресій. Пакет тримає три шари захисту:

| Шар | Команда | Ціна | Що ловить |
|---|---|---|---|
| 0 · статичний лінт | `make check` (`tests/agent/lint.py`) | 0 токенів, секунди | регресії ТЕКСТУ конфігурації: диф `+Write` у tools, битий settings.json, поламану структуру кейсів |
| 1 · власний харнес | `make evals` (`tests/agent/run.py`) | токени, хвилини | регресії ПОВЕДІНКИ: реальний `claude -p` на golden-задачах + детермінований грейдер |
| 2 · Promptfoo | `cd promptfoo && npx promptfoo@latest eval` | токени | те саме індустріальним інструментом: матриця, історія прогонів, llm-rubric, trajectory |

Канонічна структура кейса (від Simon S., переведена на Python):

```
tests/agent/cases/<case>/{prompt.md, case.json, check.py, expect.md}
tests/agent/run.py
```

## Центральна теза

Прогін агента **недетермінований**. Тому асертимо на **РЕЗУЛЬТАТ** (роут віддав 401?
секрет не витік? рівно 3 коміти? read-only агент не змінив файли?), а **не на текст**.
Детермінований **грейдер** над недетермінованим **агентом** - це і є eval конфігурації.

> Це інший рівень, ніж 7.6 (feedback loops перевіряють *код, що згенерував агент*) і 5.3
> (eval loop для skills). Тут eval не на продукт, а **на саму конфігурацію агента**.
> Кастомні subagents з 10.2 захищаються від регресій саме тут.

## Що лежить у дереві

- **`tests/agent/run.py`** - двигун: для кожного кейса збирає чисту пісочницю за
  `case.json` (fixture + renames + stage-конфіг + git + засаджений коміт), жене реальний
  `claude -p` headless (патерн із 7.2), викликає грейдер `check.py`, друкує
  PASS/FAIL-матрицю з cost. Тільки stdlib, ~170 рядків.
- **`tests/agent/lint.py`** - шар 0: парсить YAML-frontmatter агентів ручним парсером
  (без pip-залежностей), звіряє allowlist tools із контрактом `EXPECTED_AGENT_TOOLS`,
  валідить settings.json і структуру кейсів. Нуль токенів.
- **`tests/agent/lib/checks.py`** - спільні перевірки грейдерів: `clean_diff`,
  `http_status`, `transcript_text`, `git_log_count`, `parse_frontmatter`, …
- **`.claude/agents/ro-reviewer.md`** - read-only рев'юер із 10.2: конфігурація, яку
  захищає кейс `subagent-tools-allowlist`.
- **`promptfoo/`** - індустріальний шар, два конфіги (див. `promptfoo/README.md`).
- **`ci/evals.yml`** - приклад GitHub Actions: блокуючий lint на PR + non-blocking
  nightly evals із quality-gate по `results.json`.

## Setup

```bash
cd ~/sources/agentic-engineering-course/modules/10-agent-teams/10.3-evals-regression

make check        # шар 0 (без токенів) - має бути зелено одразу
```

Залежності навмисно мінімальні: `python3` (тільки stdlib), чистий `node` (вбудовані
`http` і `node:test`, без `npm install`), `git`. Для реального прогону - встановлений
`claude` CLI (`make evals` коштує токени, як 7.2).

## Як запустити

| Команда | Що робить |
|---|---|
| `make check` | **Шар 0: статичний лінт без токенів.** CI/pre-commit-шар. |
| `make evals` | Реальний `claude -p` на **всіх** кейсах. Коштує токени. |
| `make evals-one CASE=route-auth` | Один кейс. |
| `make evals-one CASE=subagent-tools-allowlist BREAK=1` | **Red-green:** підкласти зламаний конфіг → кейс має почервоніти. |
| `make demo` | Друкує сторіборд скринкастів. |
| `make demo-beerlms` | Друкує, як навести той самий suite на реальні агенти beer-lms (M6). |
| `cd promptfoo && bash setup.sh && npx promptfoo@latest eval` | **Promptfoo-шар.** Коштує токени. |
| `make clean` | Прибрати `tmp/` (пісочниці прогонів). |

## Кейси - кейс → який конфіг стереже

### Курс-специфічні (захищають конфіг із попередніх модулів)

| Кейс | Що тестує (конфіг) | `check.py` перевіряє (exit 0/1) | Лінія від |
|---|---|---|---|
| `subagent-tools-allowlist` | allowlist інструментів агента `ro-reviewer` | `git diff` по `src/` порожній (read-only не писав) **і** рев'ю з вердиктом згенеровано | 10.2 |
| `forbid-env-read` | guardrail protect-env (deny `Read(.env)` + PreToolUse-хук) | значення секрета **не** з'явилось у транскрипті | 5.4 protect-files |
| `gate-green` | скіл `verify-gate` + Stop-hook (гейт = `node --test`) | гейт зелений **і** `test/` незаймано **і** стаб замінено | 7.6 verify-gate |
| `tdd-three-commits` | скіл `/tdd` (RED-GREEN-REFACTOR на `node:test`) | рівно 3 коміти `test(`/`feat(`/`refactor(`, `test/` заморожено після RED, гейт зелений | 7.7 tdd |

### Портовні generic (шаблон для студента)

| Кейс | Завдання агенту | `check.py` перевіряє |
|---|---|---|
| `route-auth` | додати auth-перевірку на роут | живий сервіс: `/private` без auth → **401**, з Bearer → **200**, `/public` → 200 |
| `fix-n-plus-one` | прибрати N+1 у запиті | інструментований лічильник SQL ≤ 2 **і** результат коректний |

## Анатомія кейса

```
tests/agent/cases/<case>/
├── prompt.md      # завдання агенту (голден-задача)
├── case.json      # декларація пісочниці: fixture, stage-конфіг, broken, flags, seed
├── check.py       # грейдер: ДЕТЕРМІНОВАНІ перевірки фінального стану, exit 0/1
├── expect.md      # людською мовою: що означає PASS
└── broken/ | guard/ | config/   # (опц.) версії конфігурації для stage/BREAK
```

`run.py` дає `check.py` через env: `SANDBOX` (шлях до пісочниці), `TRANSCRIPT`
(ndjson-лог прогону), `CASE_DIR`, `LIB_DIR`. Спільні перевірки - у
`tests/agent/lib/checks.py`.

## Red-green - «зламай `.claude/` → eval червоніє»

```bash
make evals-one CASE=subagent-tools-allowlist            # allowlist на місці → PASS
make evals-one CASE=subagent-tools-allowlist BREAK=1    # staged broken-конфіг → FAIL
make evals-one CASE=subagent-tools-allowlist            # конфіг повернули → PASS
```

`BREAK=1` каже stage-кроку двигуна підкласти **зламану версію конфіга** (поле `broken`
у `case.json`) - регресія відтворювана однією командою, без брудного git. Те саме
для `forbid-env-read BREAK=1` (deny-правило прибрано → секрет тече → FAIL).

Той самий диф `+Edit, +Write` ловиться і ДЕШЕВШЕ - статичним лінтом:

```bash
cp tests/agent/cases/subagent-tools-allowlist/broken/ro-reviewer.md .claude/agents/ro-reviewer.md
make check     # ✗ ro-reviewer: tools == контракт - зайве: ['Edit', 'Write']
git checkout .claude/agents/ro-reviewer.md
```

Але лінт бачить лише ТЕКСТ конфігурації: Bash-обхід (`sed -i` без Edit), накази в body,
взаємодію з CLAUDE.md і недетермінізм моделі ловить тільки поведінковий шар.

> Для `route-auth`, `fix-n-plus-one`, `gate-green`, `tdd-three-commits` `BREAK` - no-op
> (generic/discipline-кейси без окремого guardrail-конфіга); двигун чесно про це скаже.

## Банк додаткових ідей (домашка / розширення)

Реалізовані 6 кейсів вище. Решта - як ідеї (кожна по тому ж шаблону
`prompt.md + case.json + check.py`):

| Ідея | Що доводить | ескіз грейдера |
|---|---|---|
| `respects-claude-md-rule` | правила CLAUDE.md направду кермують агентом (зв'язок із Module 4) | grep diff на порушення (напр. `: any` у TS / не-repository pattern) |
| `description-routing` | якість поля `description` (центральна теза 10.2) | парс транскрипта: делеговано саме потрібному subagent |
| `plan-mode-no-write` | plan mode не чіпає файли | `git status` чистий після плану |
| `no-secret-in-output` | агент не віддзеркалює секрет | пошук по транскрипту (як `forbid-env-read`) |
| `idempotent-skill` | другий прогін скіла - no-op | новий `git diff` порожній |
| `commit-message-format` | коміти conventional-commits | префікси `git log` |
| `migration-rollback` | у міграції робочий `down()` | apply + rollback чисто |
| `cost-ceiling` | bounded-задача під N turns/tokens | м'який чек через `transcript_stats` |

## Promptfoo-шар (`promptfoo/`)

Два конфіги: основний сьют на `anthropic:claude-agent-sdk` (детерміновані + python +
trajectory асерти, `defaultTest`, cost-стеля) і `review/` - кастомний `provider.py`,
що жене `ro-reviewer` тим самим двигуном, що харнес, + `llm-rubric` на якість рев'ю.
Деталі і чесні нотатки - `promptfoo/README.md`.

## CI/CD (`ci/evals.yml`)

Приклад GitHub Actions: job `lint` (шар 0, блокуючий, тригер по paths `.claude/**`) +
job `evals` (nightly + workflow_dispatch, non-blocking, secrets.ANTHROPIC_API_KEY,
кеш Promptfoo, quality-gate `jq '.results.stats.failures'`, upload артефакту).
У своєму репо файл їде в `.github/workflows/evals.yml`.

## beer-lms track - той самий suite на реальному M6

`make demo-beerlms` друкує кроки. Коротко: beer-lms (`~/sources/beer-lms`, GitLab) має
власну `.claude/` - її так само треба захищати. Портовні кейси: `subagent-tools-allowlist`
на реальному review-агенті, `respects-claude-md-rule` на реальному CLAUDE.md,
`gate-green` на `go test ./...`.

> **Чесна примітка.** agent-runs недетерміновані - деякі кейси можуть «мигати»
> (найперше `tdd-three-commits`: 3 атомарні коміти за один headless-прогін -
> найскладніше; у 7.7 це робить оркестратор із 3 агентів). Саме тому асерт - на
> **outcome**, а `make check` (без токенів) лишається завжди-зеленим CI-шаром.

## Як читати транскрипт

Кожен прогін лишає `tmp/run-*/transcript.jsonl` - ndjson-лог агента (stream-json,
як у 7.2). Швидкий зріз «що агент реально робив»:

```bash
python3 tests/agent/lib/checks.py tmp/run-subagent-tools-allowlist/transcript.jsonl
# Виклики інструментів:
#    4  Bash
#    2  Read
# cost=$0.0857  turns=8
```

Cost і кількість turns грейдер бере з фінального `result`-рядка (`total_cost_usd`,
`num_turns` - див. `transcript_stats` у `lib/checks.py`). Читай транскрипт, перш ніж
вірити вердикту: так ловляться і зламані задачі, і грейдери, що пропускають сміття.

## Флейкі-політика в CI

`make check` - **blocking** на кожен PR: без токенів, завжди зелений на чистому
checkout; падіння тут означає зламаний контракт конфігурації або харнес, не флейк.
`make evals` / promptfoo - **nightly, non-blocking**: одиничний FAIL недетермінованого
агента ще не факт регресії, тому червоний nightly створює алерт/issue, а не блокує
merge. Кейс, червоний дві-три ночі поспіль, - уже регресія: дивись diff `.claude/`
за ці дні.

Прогін друкує cost по кожному кейсу - тримай суму на оці як cost-стелю (у Promptfoo
це ще й асерт `type: cost`). Поки кейсів шість, nightly коштує центи; коли стануть
десятки - обмежуй nightly-вибірку або ганяй повний сьют лише перед merge змін `.claude/`.

## Як перенести у свій проєкт

1. Скопіюй `tests/agent/` (run.py, lint.py, lib/checks.py) і `Makefile`.
2. Пропиши контракт своїх агентів у `EXPECTED_AGENT_TOOLS` (lint.py).
3. Додай 1-2 кейси під свою `.claude/`: `prompt.md` (що просимо), `case.json`
   (пісочниця + конфіг, що тестуєш), `check.py` (детермінований грейдер на outcome).
4. Постав `make check` у pre-commit / CI (без токенів), evals - nightly
   (`ci/evals.yml` як заготовка).
5. Перший кейс роби найдешевшим guardrail-ом (як `forbid-env-read`) - швидко, наочно,
   ловить найдорожчі регресії (витік секрета).

## Sources

- Канонічна структура `tests/agent/cases/*` - Simon S. (Telegram, обговорення курсу).
- Зв'язок із 7.6 (feedback loops) і 5.3 (eval loop для skills) - інший рівень: eval конфігурації.
- `claude -p` headless - патерн із 7.2 `ralph.sh`.
- Promptfoo-факти (провайдер, асерти) - live-дока promptfoo.dev + context7 (2026-07-04).
- Повний список - у `Sources.md` лекції 10.3.
