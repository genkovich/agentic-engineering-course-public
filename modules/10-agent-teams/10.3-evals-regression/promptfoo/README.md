# Promptfoo-шар · 10.3

Той самий принцип, що в python-харнесі поруч (`tests/agent/`) - детермінований
грейдер над недетермінованим агентом, - але індустріальним інструментом:
декларативний YAML, матриця тестів, історія прогонів, веб-переглядач, готові
типи асертів, паралельність і кеш.

## Два конфіги

| Конфіг | Агент під тестом | Що демонструє |
|---|---|---|
| `promptfooconfig.yaml` | coding-агент через `anthropic:claude-agent-sdk` | перший кейс + масштабування: `defaultTest`, `contains`/`is-json`, python-асерт `check_route.py`, trajectory (`tool-used`, `step-count`), `cost`-стеля, матриця `vars` |
| `review/promptfooconfig.yaml` | `ro-reviewer` через кастомний `provider.py` | розширюваність: провайдер = python-файл, що жене `claude -p --agent ro-reviewer` тим самим двигуном, що `tests/agent/run.py`; `llm-rubric` на якість тексту рев'ю |

## Місток «свій харнес → Promptfoo»

- `check_route.py` імпортує помічники з `tests/agent/lib/checks.py` - грейдер
  не переписується, а перевикористовується (`type: python`, `file://`).
- `review/provider.py` імпортує двигун `tests/agent/run.py`: та сама пісочниця,
  той самий кейс `subagent-tools-allowlist`, навіть `BREAK=1` працює.

## Запуск

```bash
cd promptfoo
bash setup.sh                       # чиста пісочниця workdir/ (копія fixtures/route)
npx promptfoo@latest eval --no-cache
npx promptfoo@latest view           # веб-переглядач прогону

cd review                           # другий конфіг: ro-reviewer + llm-rubric
npx promptfoo@latest eval --no-cache
BREAK=1 npx promptfoo@latest eval --no-cache   # зламаний конфіг -> асерти червоні
```

Потрібні: `node`, `ANTHROPIC_API_KEY` в env (для `review/` - ще й `claude` CLI).
Прогони коштують токени (як `make evals`).

## Встановлення Promptfoo

- Разово: `npx promptfoo@latest init` (скелет конфіга) / `npx promptfoo@latest eval`.
- Глобально: `npm install -g promptfoo`.

## Чесні нотатки

- Точні назви trajectory-асертів звірені з live-докою Promptfoo (2026-07-02,
  ре-верифіковано через context7 2026-07-04): `trajectory:step-count` /
  `tool-used` / `tool-args-match` / `tool-sequence` - усі на
  `promptfoo.dev/docs/configuration/expected-outputs/deterministic`.
- Провайдер `anthropic:claude-agent-sdk` МАЄ `setting_sources: ['project']`
  (підхоплює CLAUDE.md/skills з working_dir) і програмні `agents:`
  (субагенти для делегування), але запустити НАЗВАНОГО агента з
  `.claude/agents/` головним потоком не вміє - саме тому `review/` їде через
  кастомний `provider.py`. Це не милиця, а штатна точка розширюваності.
- Trajectory-асерти потребують агентного провайдера, що емить tool-спани;
  на plain-text провайдері їм нема що перевіряти.
- `trajectory:tool-sequence` (точна послідовність) навмисно НЕ використаний:
  найкрихкіший асерт - агенти регулярно знаходять валідні шляхи, яких автор
  eval-у не передбачив. Тримай його для контрактів, де порядок і є вимогою.
- Обидва тести головного конфіга ділять один `workdir/`: другий прогін бачить
  уже полагоджений сервіс. Для повної ізоляції ганяй `bash setup.sh` між
  прогонами або тримай по workdir на тест.
- `is-json`-тест просить агента відповісти ТІЛЬКИ JSON-об'єктом - агент може
  не послухатись (недетермінізм), тоді червоніє саме формат, не поведінка.
  Це навмисний навчальний приклад різниці «контракт на текст» vs «на outcome».

## Runbook перед записом скринкастів

- [ ] `export ANTHROPIC_API_KEY=...` і один живий `npx promptfoo@latest eval`
      у `promptfoo/` - звірити, що обидва тести проходять (2026-07-04 прогін
      не виконувався: ключа в env не було; механіка обох конфігів перевірена
      offline - python-асерти, provider-імпорти, YAML-парс).
- [ ] `npx promptfoo@latest view` - переглядач відкривається, асерти розгортаються.
- [ ] `cd review && npx promptfoo@latest eval` + `BREAK=1 ...` - red-green.
