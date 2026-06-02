# 7.4 · Dynamic workflows - demo

Demo-проект для лекції **7.4 Dynamic workflows: Ralph, переписаний у скрипт**
(Module 7 · Execution & Scale).

Dynamic workflow (англ. *dynamic workflow*, динамічний робочий процес) - це
JavaScript-скрипт, який Claude пише сам під твою задачу; середовище виконання
(англ. *runtime*) крутить його у фоні, поки твоя сесія лишається відзивною.
Скрипт тримає план у коді й оркеструє десятки субагентів. Цей пакет дає
(1) **runnable** підкладку з трьома незалежними сторіс і (2) два **валідні
скрипти оркестрації** у `.claude/workflows/`, на яких видно `agent()`,
`parallel()`, `pipeline()` і перевірку через збіжність.

## Що показує

- **Хто тримає план.** У субагента план тримає сам Claude, хід за ходом; у
  workflow план переїжджає у код - цикл, розгалуження і проміжний стан живуть у
  змінних скрипта, а в контекст Claude повертається тільки фінальна відповідь.
- **Три примітиви + звичайний JS.** `agent()` (один субагент), `parallel()`
  (барʼєр - чекає всіх), `pipeline()` (без барʼєра - кожен елемент тече крізь
  стадії незалежно), а цикл і гілка - це plain `while`/`for`/`if`.
- **Незалежність як передумова паралелізму.** Три сторіс пишуть кожна у свій
  файл (`search.py` / `dedupe.py` / `export.py`); перетин множин порожній - саме
  тому їх безпечно паралелити.
- **Перевірка через збіжність (convergence).** На кожну реалізовану сторіс -
  кілька незалежних рецензентів; лишається тільки те, на чому вони збіглись.
- **Модель під роль, вартість ~15x, `/workflows`, `ultracode`.** Способи запуску
  й межі - у таблиці покриття нижче.

Задачі у self-contained демо навмисно **абстрактні** (пошук / дедуп / експорт
сніпетів): урок про незалежність і паралелізм, а не про конкретну фічу.

## Snippets - наскрізний приклад

Пакет `src/snippets/` має працюючу основу і три заглушки-задачі:

| Файл | Стан | Що це |
|---|---|---|
| `models.py` | працює | dataclass `Snippet(id, title, body, language, tags)` |
| `store.py` | працює | `SnippetStore` (add/get/all) - залежність |
| `tags.py` | працює | `normalize_tag` - залежність для пошуку за тегом |
| `search.py` | **заглушка** | SNIP-3: `search_by_tag`, `search_by_text` |
| `dedupe.py` | **заглушка** | SNIP-4: `find_duplicates` |
| `export.py` | **заглушка** | SNIP-5: `to_markdown` |

Три заглушки піднімають `NotImplementedError` - на чистому checkout `pytest`
червоний навмисно. Це стартовий стан: workflow доводить усі три до зеленого
паралельно, кожен агент - у своєму файлі.

## Незалежність → паралелізм

Серце демо. Три сторіс безпечно паралелити рівно тому, що множини файлів, у які
вони пишуть, **не перетинаються**:

| Story | Пише у (write) | Читає (read-only) | Тест |
|---|---|---|---|
| SNIP-3 · search | `src/snippets/search.py` | `models.Snippet`, `tags.normalize_tag` | `tests/test_search.py` |
| SNIP-4 · dedupe | `src/snippets/dedupe.py` | `models.Snippet` | `tests/test_dedupe.py` |
| SNIP-5 · export | `src/snippets/export.py` | `models.Snippet` | `tests/test_export.py` |

Перетин write-множин: **порожній**. Спільне (`models.Snippet`) - тільки на
читання, і його ніхто не змінює. Тому це не «можна паралелити для швидкості», а
«паралелити безпечно, бо немає спільного запису». Якби дві сторіс писали в один
файл - був би race на запис: другий агент мовчки перетер би роботу першого, і ти
дізнався б про це не одразу. Тоді є рівно два чесні виходи: координація через
спільне місце для домовленостей або розбити роботу так, щоб перетину не було.

## Setup

```bash
cd modules/7-execution-scale/7.4-dynamic-workflows

make verify          # RED на чистому checkout: NotImplementedError у search/dedupe/export - стартовий стан
make check-workflow  # GREEN: обидва .claude/workflows/*.mjs парсяться як валідний JS
```

`uv` підтягне `pytest` сам. Для `check-workflow` потрібен встановлений `node`.
Для реального прогону - `claude` CLI (v2.1.154+; dynamic workflows - research
preview, рання доступна версія).

## Як запустити

| Команда | Що робить |
|---|---|
| `make verify` | DoD-проба (`pytest -q`). Червоно на старті (три `NotImplementedError`), зелено після успішного прогону. |
| `make check-workflow` | `node --check` на обох `.mjs` - детермінований доказ, що скрипти оркестрації синтаксично валідні. Можна ганяти в CI. |
| `make demo` | Друкує, як **тригерити** workflow (слово «workflow» у промпті) і дивитись фази через `/workflows`. НЕ авто-ран: недетерміновано + ~15x токенів. |
| `make clean` | Прибрати кеші (`__pycache__`, `.pytest_cache`). |

> `make demo` нічого не запускає сам. Реальний прогін недетермінований і палить
> приблизно у пʼятнадцять разів більше токенів за звичайний чат - тому тригериш
> його свідомо, з `budget` у токенах і ввімкненим алертом на сплеск витрат.

## Скрипт оркестрації

Два готові скрипти у `.claude/workflows/` показують той самий код, який Claude
згенерував би сам зі словесної задачі. Це не шаблони для копіпасту - це приклад
форми, у якій живе план workflow.

**`ship-snippets.mjs`** - доставляє три сторіс і перевіряє кожну:

- `export const meta` - чистий літерал з назвою, описом і фазами
  (`Implement`, `Verify`); рантайм читає його ще до запуску тіла, щоб показати
  фази у `/workflows`.
- Фаза `Implement` через **`parallel()`** - барʼєр: запускає по одному `agent()`
  на сторіс **одночасно** і чекає, поки завершаться всі гілки. Кожен агент
  доводить свій тест до зеленого, змінюючи рівно свій файл.
- Фаза `Verify` через **`pipeline()`** + **збіжність**: на кожну реалізовану
  сторіс спавнить **двох незалежних рецензентів** (`parallel()` усередині), що
  наосліп звіряють «тести зелені» і «`tests/` незаймані». Сторіс лишається,
  тільки якщо **обидва** згодні - згода двох незалежних і є сигналом, вартим
  довіри.
- У коментарі прямо сказано, де барʼєр `parallel()`, а де потокова
  `pipeline()`, і чому за замовчуванням для довшої хвилі береться `pipeline()`.

**`audit-independence.mjs`** - менший convergence-аудит **до** будь-якого запису:
на кожну сторіс спавнить N незалежних аудиторів, що звіряють «файли не
перетинаються з іншими». Згода всіх (збіжність) - підстава паралелити; будь-який
перетин кидає помилку `re-split before parallel run`, бо це гонка за запис.

Обидва скрипти: тіло - async top-level plain JS; доступні глобали -
`agent(prompt, opts?)`, `parallel(thunks)`, `pipeline(items, ...stages)`,
`log(msg)`, `phase(title)`. Сам скрипт **не** читає й не пише файлів - усю роботу
роблять агенти; скрипт лише координує (HARD RULE у `CLAUDE.md`).

## Очікуваний вивід

`make check-workflow` (детерміновано, без `claude`):

```
node --check .claude/workflows/ship-snippets.mjs && node --check .claude/workflows/audit-independence.mjs
OK: both .mjs parse as valid JS
```

Реальний прогін `ship-snippets` через `/workflows` (недетерміновано):

```
Phase Implement   3 агенти водночас:
  SNIP-3 → пише src/snippets/search.py, pytest tests/test_search.py -q → green
  SNIP-4 → пише src/snippets/dedupe.py, pytest tests/test_dedupe.py -q → green
  SNIP-5 → пише src/snippets/export.py, pytest tests/test_export.py -q → green
Phase Verify      на кожну сторіс 2 незалежні рецензенти (збіжність):
  SNIP-3  review-1 ✓ / review-2 ✓ → confirmed
  SNIP-4  review-1 ✓ / review-2 ✓ → confirmed
  SNIP-5  review-1 ✓ / review-2 ✓ → confirmed
3/3 сторіс підтверджено збіжністю: SNIP-3, SNIP-4, SNIP-5
```

Перевірка результату після прогону:

```bash
make verify                  # зелено
git diff --stat              # зміни у трьох НЕпересічних файлах: search.py / dedupe.py / export.py
git diff -- tests/           # пусто - тести з RED-фази не чіпали
```

## Покриття концептів лекції

| Концепт лекції | Де у демо |
|---|---|
| Хто тримає план (субагент vs workflow) | `CLAUDE.md` HARD RULE + скрипт тримає план у коді, агенти лише діють |
| `agent()` - один субагент зі `schema` | обидва `.mjs`: кожен виклик `agent(prompt, { schema })` |
| `parallel()` - барʼєр | `ship-snippets.mjs` фаза `Implement`; `audit-independence.mjs` |
| `pipeline()` - без барʼєра | `ship-snippets.mjs` фаза `Verify` (потокова перевірка по сторіс) |
| Перевірка через збіжність (convergence) | `ship-snippets.mjs` (2 рецензенти, згода обох) + `audit-independence.mjs` (N аудиторів) |
| Незалежність як передумова | `tracker.md` колонка «Files touched» (нуль перетину) + розділ вище |
| Модель під роль | опція `model` у `agent(prompt, opts)` (дорога робота → потужніша, масова → дешевша) |
| Вартість ~15x токенів | `make demo` + примітки README (свідомий тригер, `budget`) |
| `/workflows` | `make demo` + «Очікуваний вивід» (фази, лічильники, drill-in) |
| `ultracode` | словник нижче: `xhigh` + автоматичний workflow; вмикати свідомо під важку задачу |
| Слово «workflow» як тригер | `make demo` промпт зі словом-тригером |

**Про `ultracode` коротко.** `/effort` - це скільки міркування Claude вкладає в
**один хід** (рівні для Opus 4.8: `low`, `medium`, `high`, `xhigh`, `max`). А
`ultracode` (через `/effort ultracode`) поєднує `xhigh` плюс автоматичну
оркестрацію через workflow - Claude сам спускає workflow на кожну серйозну
задачу без слова-тригера. Вмикай свідомо під важку роботу (велика міграція,
складний аудит) і вимикай назад через `/effort high`: на простій фічі він спустить
кілька workflows там, де вистачило б одного ходу.

## Як перенести у свій проєкт

1. Скопіюй `.claude/workflows/` як приклад форми (`meta` + `agent`/`parallel`/`pipeline`).
   У реальній роботі скрипт пише Claude зі словесної задачі - ці файли тут як референс.
2. Додай тонкий `CLAUDE.md` (стек + HARD RULE «координатор лише делегує, код
   пишуть виконавці» + «виконавці не торкаються чужих файлів») і `tasks/tracker.md`
   з колонкою «Files touched».
3. **Доведи незалежність по файлах перед паралеллю** (як `audit-independence.mjs`):
   нуль перетину write-множин. Перетин - спершу re-split або координація.
4. Тригер - слово «workflow» у промпті; постав `budget` у токенах; дивись фази у
   `/workflows`. `ultracode` - тільки на важких задачах.

## Sources

- Module 7 · Lecture 4 «Dynamic workflows: Ralph, переписаний у скрипт».
- `claude.com/blog/introducing-dynamic-workflows-in-claude-code` - анонс динамічних workflows.
- `code.claude.com/docs/en/workflows` - довідка: `agent()` / `parallel()` / `pipeline()`, `/workflows`, межі runtime.
- Повний список - у `Sources.md` лекції 7.4.
