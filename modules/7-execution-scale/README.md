# Module 7 - Execution & Scale

Як агент виконує роботу і як це масштабувати: Ralph loop, `/goal`, динамічні workflows, фонове виконання й розклад, цикли зворотного зв'язку, TDD. Сім clone-and-run демо, кожне показує один патерн виконання на спільному наскрізному прикладі - нейтральному сервісі `snippets` (менеджер код-сніпетів на Python 3.12 + pytest, без зовнішніх залежностей). Демо 7.6 додатково має Node/Vite фронтенд для браузерного каналу перевірки.

## Лекції модуля

- 7.1 Execution map - мапа «яка форма задачі → який патерн виконання» + seed-домен `snippets`
- 7.2 Ralph loop - найпростіший автономний примітив: один промпт, bash-цикл, бінарний DoD
- 7.3 `/goal` - автономний фініш (Ralph «у коробці»): стійка умова завершення + модель-оцінювач
- 7.4 Dynamic workflows - Ralph, переписаний у скрипт: `agent()` / `parallel()` / `pipeline()`
- 7.5 Фонове виконання і розклад - матриця трьох рівнів (`/loop`, desktop scheduled, cloud `/schedule`)
- 7.6 Feedback loops - канали «дія → сигнал → корекція»: детермінований гейт + браузер через Playwright
- 7.7 TDD як execution discipline - RGR однією командою через orchestrator-skill + 3 ізольовані agents

## Демо модуля

| Лекція | Тема | Demo |
|---|---|---|
| 7.1 | Мапа патернів виконання + seed-домен `snippets` | [7.1-execution-map](./7.1-execution-map) |
| 7.2 | Ralph loop (автономний примітив) | [7.2-ralph-loop](./7.2-ralph-loop) |
| 7.3 | `/goal` (автономний фініш) | [7.3-goal](./7.3-goal) |
| 7.4 | Dynamic workflows (оркестрація субагентів) | [7.4-dynamic-workflows](./7.4-dynamic-workflows) |
| 7.5 | Фонове виконання і розклад | [7.5-background](./7.5-background) |
| 7.6 | Цикли зворотного зв'язку (feedback loops) | [7.6-feedback-loops](./7.6-feedback-loops) |
| 7.7 | TDD як execution discipline | [7.7-tdd-discipline](./7.7-tdd-discipline) |

## Як запустити

Кожне демо - окрема директорія з власним `Makefile` і `README.md`. Загальний цикл:

```bash
cd modules/7-execution-scale/<demo>     # напр. 7.2-ralph-loop
make verify                             # DoD-проба
make help                               # список таргетів цього демо
```

`make verify` на **чистому checkout** навмисно **червоний** для код-демо (7.1, 7.2, 7.3, 7.4, 7.7): стартовий стан - заглушки з `NotImplementedError`, які відповідний патерн доводить до зеленого. Це by design, а не зламаний клон.

Винятки:

- **7.5** - `make verify` **зелений** на checkout: тут немає задачі «з червоного в зелене», демо про те, **де** і **коли** крутиться агент (матриця рівнів + рецепти). Зелений `pytest` - конкретна ціль, яку опитує `/loop`-рецепт.
- **7.6** - спершу `npm install` (фронтенд на Vite), тоді `make verify`. Один тест (`queue.test.ts`) зелений навмисно - це teaching point про сліпий юніт-канал.

`make demo` у більшості демо **нічого не запускає сам**: він друкує кроки slash-команд (`/goal`, `/workflows`, `/tdd`), бо вони живуть усередині `claude`, не в чистому shell. Там, де `make demo` справді кличе `claude -p` (7.2), це **недетерміновано і витрачає токени** - перед запуском перевір ліміти й увімкни алерт на сплеск витрат в Anthropic Console.

## Convention

- **Один наскрізний приклад.** Усі runnable-демо стоять на домені `snippets` (Python 3.12, стандартна бібліотека + pytest). Видно цілком, запускається одним `pytest`, нічого нізвідки клонувати.
- **RED-on-checkout як стартова точка.** Код-демо починаються червоними навмисно - кожна лекція «зеленить» свій модуль своїм патерном. 7.5 - зелений (вісь «де/коли», не задача).
- **`.claude/` всередині демо.** Skills, agents, hooks і workflows лежать у `.claude/` кожного демо - можна склонувати демо як окремий проєкт і запустити Claude Code там, не торкаючись свого основного `~/.claude/`.
- **`make` як єдиний вхід.** `make verify` (DoD), `make demo` (кроки/прогін патерну), `make help` (таргети). Детермінований доказ - завжди окремий таргет (`make gate`, `make check-workflow`, `make matrix`), його можна ганяти в CI.
- **Безпека автономних прогонів.** Реальні прогони патернів тримай у `acceptEdits` (не `--dangerously-skip-permissions`), з ліцензованим лімітом ітерацій / бюджетом токенів і алертом на витрати. Тверда стеля витрат - на тобі.

## Pre-requisites

- Claude Code локально (див. Module 3 starters)
- [uv](https://docs.astral.sh/uv/) для self-contained Python-демо (підтягне `pytest` сам)
- `node` - для 7.4 (`make check-workflow`) і 7.6 (фронтенд + `playwright-cli`)
- ANTHROPIC_API_KEY у `.env` (або OAuth через `claude auth login`) - для прогонів, що кличуть `claude`

## Sources

Лекції, теорія і повні списки джерел - у LMS курсу. Кожне демо тримає свій `Sources.md`-відсилання у README.
