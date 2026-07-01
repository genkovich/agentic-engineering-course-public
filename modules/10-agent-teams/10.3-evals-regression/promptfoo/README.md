# Promptfoo-шар · 10.3 (Скринкаст #4)

Той самий принцип, що в bash-харнесі поруч (`tests/agent/`), але індустріальним
інструментом: **Promptfoo** з декларативним YAML, матрицею тестів і trajectory-асертами.

## Що доводить

- **trajectory:tool-used (Bash)** — агент справді виконував команди (піднімав сервіс,
  ганяв `curl`), а не лише написав «готово». Поведінковий контракт на проміжний шлях.
- **trajectory:step-count** — бюджет кроків: захист від нескінченного блукання.
- **contains '401'** — детермінований шар по фінальному тексту.

Провайдер — Tier 1 «Coding agent SDK» (`anthropic:claude-agent-sdk`): реальний
coding-агент у `workdir/` (чиста копія `fixtures/route`).

## Запуск

```bash
cd promptfoo
bash setup.sh                       # чиста пісочниця workdir/
npx promptfoo@latest eval --no-cache
npx promptfoo@latest view           # веб-переглядач прогону
```

Потрібні: `node`, `ANTHROPIC_API_KEY` в env. Прогін коштує токени (як `make evals`).

## Чесні нотатки

- Точні назви асертів і структура `value` звірені з live-докою Promptfoo (2026-07-02):
  `trajectory:step-count` / `tool-used` / `tool-args-match` / `tool-sequence` — усі на
  `promptfoo.dev/docs/configuration/expected-outputs/deterministic`.
- Trajectory-асерти потребують агентного провайдера (Tier 1/2), що емить tool-спани;
  на Tier 0 (plain text) їм нема що перевіряти.
- `trajectory:tool-sequence` (точна послідовність) навмисно НЕ використаний: у лекції це
  «найкрихкіший асерт» — тримай його для контрактів, де порядок і є вимогою.
- Прогін недетермінований: агент може розв'язати задачу різними шляхами — асерти
  сформульовані на контракт (виконував команди, вклався в бюджет, підсумував 401).
