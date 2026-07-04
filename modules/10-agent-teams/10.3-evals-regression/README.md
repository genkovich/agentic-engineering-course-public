# 10.3 · Evals і регресійне тестування агентів

Demo-пакет до лекції **10.3** (Module 10 · Agent Teams). Це маленький проєкт
(`src/discount.js` - модуль знижок), у якому лекція БУДУЄ агента з нуля,
пише для нього перші тести руками, а потім віддає все індустріальному
інструменту - Promptfoo.

## Центральна теза

Прогін агента **недетермінований**. Тому асертимо на **РЕЗУЛЬТАТ** (git diff
порожній? роут віддав 401? секрет не витік?), а не на текст. Детермінований
**грейдер** над недетермінованим **агентом** - це і є eval конфігурації.

`.claude/` (agents, hooks, skills, settings) - версіонована конфігурація
агента. Її, як і код, треба захищати від тихих регресій.

## Шлях лекції по дереву пакета

| Крок | Файл | Що це |
|---|---|---|
| 1. Агент з нуля | `.claude/agents/ro-reviewer.md` | read-only рев'юер (10.2), предмет тестування |
| 2. Перший тест руками | `eval/check.sh` (~10 рядків) | прогін у проєкті + `git diff` + вердикт; БЕЗ пісочниці |
| 3. Лінт за нуль токенів | `eval/lint.py` (~30 рядків) | frontmatter проти контракту `EXPECTED_TOOLS` |
| 4. Пісочниця руками | `eval/sandbox.sh` (~10 рядків) | копія проєкту + свіжий git; готового тула нема - і не треба |
| 5. Суддя руками | `eval/judge.sh` + `eval/rubric.md` | ще один `claude -p`: бал {score, reason} за рубрикою |
| 6. Той самий кейс у Promptfoo | `promptfoo/promptfooconfig.yaml` | regex + python + llm-rubric; провайдер `provider.py` |
| 7. Сьют: решта 5 кейсів | `promptfoo/suite/promptfooconfig.yaml` | claude-agent-sdk + власний провайдер + trajectory |
| 8. CI | `ci/evals.yml` | lint блокуючий на PR; evals nightly non-blocking |

`eval/broken/ro-reviewer.md` - зламана версія агента (+Write, +Edit, body
командує виправляти) для red-green руками і `BREAK=1`.

## Setup

```bash
cd ~/sources/agentic-engineering-course/modules/10-agent-teams/10.3-evals-regression

make lint                # 0 токенів - має бути зелено одразу
cd promptfoo && npm ci   # разово: @anthropic-ai/claude-agent-sdk для сьюту
```

Залежності: `python3` (stdlib), `node` (вбудовані `http` і `node:test`), `git`,
`claude` CLI. Авторизація - локальна сесія Claude Code (`apiKeyRequired: false`
у конфігах) АБО `ANTHROPIC_API_KEY`. Прогони агента коштують токени.

## Як запустити

| Команда | Що робить | Ціна |
|---|---|---|
| `bash eval/check.sh` | перший тест: рев'ю є, `src/` незайманий, `git restore` прибирає сліди | токени |
| `make lint` | статичний лінт конфігурації агентів | 0 |
| `bash eval/sandbox.sh` | зібрати пісочницю `tmp/sandbox` | 0 |
| `bash eval/judge.sh` | суддя: JSON-бал за `eval/rubric.md` для `review.md` | токени |
| `make eval-one` | головний кейс у Promptfoo (`BREAK=1 make eval-one` - red-green) | токени |
| `make evals` | сьют: 5 кейсів | токени |
| `npx promptfoo@latest view` | веб-переглядач прогонів (з `promptfoo/` або `promptfoo/suite/`) | 0 |
| `make clean` | прибрати пісочниці і артефакти | 0 |

## Red-green руками - «зламай конфіг → тест червоніє»

```bash
bash eval/check.sh                                        # PASS
cp eval/broken/ro-reviewer.md .claude/agents/ro-reviewer.md
bash eval/check.sh                                        # FAIL: агент ЗМІНИВ код
git checkout .claude/agents/ro-reviewer.md
bash eval/check.sh                                        # знову PASS
```

Той самий диф `+Edit, +Write` ловиться і дешевше - `make lint` (нуль токенів,
секунда). Але лінт бачить лише ТЕКСТ конфігурації: Bash-обхід (`sed -i` без
Edit), накази в body і недетермінізм моделі ловить тільки поведінковий шар.

## Promptfoo-шар

**Головний конфіг** (`promptfoo/promptfooconfig.yaml`) - той самий перший кейс,
без самопису: провайдер `provider.py` (наш sandbox.sh + `claude -p --agent
ro-reviewer`, загорнуті у функцію), асерти = regex-вердикт + `check_clean.py`
(git diff порожній) + `llm-rubric` (рубрика з `eval/rubric.md` дослівно,
поріг 0.7).

**Сьют** (`promptfoo/suite/promptfooconfig.yaml`) - решта 5 кейсів:

| Кейс | Провайдер | Грейдер перевіряє |
|---|---|---|
| `route-auth` (×2 формати) | `anthropic:claude-agent-sdk` | живий сервіс: 401/200/200 + trajectory + cost |
| `fix-n-plus-one` | `anthropic:claude-agent-sdk` | інструментований лічильник: запитів ≤2 |
| `forbid-env-read` | `provider.py` | секрет не з'явився у транскрипті |
| `gate-green` | `provider.py` | `node --test` зелений, `test/` незайманий, стаб замінено |
| `tdd-three-commits` | `provider.py` | 3 коміти test→feat→refactor, тести заморожені |

Generic-кейси їдуть через готовий провайдер `anthropic:claude-agent-sdk`
(потрібен npm-пакет `@anthropic-ai/claude-agent-sdk` поруч); кейси з
`.claude`-конфігурацією під тестом - через `suite/provider.py` (узагальнення
головного: пісочниця за vars fixture/config/broken/rename).

### Чесні нотатки (звірено живими прогонами)

- Провайдер `anthropic:claude-agent-sdk` НЕ запускає названого агента з
  `.claude/agents/` головним потоком - тому головний кейс їде через кастомний
  `provider.py`. Це не милиця, а штатна точка розширюваності Promptfoo.
- Trajectory-асерти потребують блока `tracing.otlp.http` у конфігу + env
  `CLAUDE_CODE_ENABLE_TELEMETRY`/`OTEL_*` у провайдера; без них - «No trace
  data available». Кроки у trace маркуються `tool:Bash`, `tool:Read`, ... -
  тож `trajectory:step-count` бере `type: tool`.
- Модель-суддя для `llm-rubric` - `claude-haiku-4-5-20251001`: грейдер шле
  `temperature: 0`, а моделі 5-го покоління цей параметр відхиляють (400).
- `trajectory:tool-sequence` (точна послідовність) навмисно не використаний:
  найкрихкіший асерт - агенти регулярно знаходять валідні шляхи, яких автор
  eval-у не передбачив.
- Два route-тести ділять `workdir-route`, тому `maxConcurrency: 1`; другий
  прогін бачить уже полагоджений сервіс - для повної ізоляції ганяй
  `bash setup.sh` між прогонами.
- `is-json`-тест може почервоніти, якщо агент не втримав формат: червоніє
  контракт на ТЕКСТ, не поведінка. Навмисна ілюстрація різниці.

## CI/CD (`ci/evals.yml`)

Job `lint` - блокуючий на кожен PR по paths `.claude/**`/`eval/**`/`promptfoo/**`,
нуль токенів. Job `evals` - nightly + workflow_dispatch, non-blocking
(`continue-on-error`), обидва promptfoo-конфіги, quality-gate
`jq '.results.stats.failures'`, артефакт results.json. Кейс, червоний дві-три
ночі поспіль, - уже регресія: дивись diff `.claude/` за ці дні.

## Банк додаткових ідей (домашка / розширення)

| Ідея | Що доводить | Ескіз грейдера |
|---|---|---|
| `respects-claude-md-rule` | правила CLAUDE.md направду кермують агентом | grep diff на порушення |
| `description-routing` | якість поля `description` (10.2) | транскрипт: делеговано потрібному subagent |
| `plan-mode-no-write` | plan mode не чіпає файли | `git status` чистий після плану |
| `idempotent-skill` | другий прогін скіла - no-op | новий `git diff` порожній |
| `commit-message-format` | коміти conventional-commits | префікси `git log` |
| `migration-rollback` | у міграції робочий `down()` | apply + rollback чисто |
| `cost-ceiling` | bounded-задача під N turns | `type: cost` / turns із транскрипта |

## beer-lms track

`make demo-beerlms` друкує, як навести ті самі evals на реальну `.claude/`
beer-lms (M6): read-only рев'юер + правило CLAUDE.md + gate-green на
`go test ./...`.

## Sources

- Promptfoo-факти (провайдер, trajectory, tracing, суддя) - live-дока
  promptfoo.dev + живі прогони 2026-07-05.
- `claude -p` headless - патерн із 7.2.
- Повний список - у `Sources.md` лекції 10.3.
