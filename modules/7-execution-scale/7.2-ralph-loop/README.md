# 7.2 · Ralph loop — demo + screencast

Demo-проект для лекції **7.2 Ralph loop: автономний примітив виконання**
(Module 7 · Execution & Scale).

Ralph loop — це найпростіший спосіб запустити агента «по колу»: один промпт, один
bash-цикл, один бінарний критерій «готово». Цей пакет дає (1) **runnable** канонічний
цикл на абстрактній задачі і (2) **скрінкаст-сценарії** запуску цього harness.

## Що показує

- Канонічний one-liner Huntley: `while [ ! -f DONE ]; do claude -p "$(cat PROMPT.md)"; done`.
- Три файли обвʼязки: `PROMPT.md` (одна задача + DoD), `DONE` (sentinel-вихід), `tasks/tracker.md`.
- Холодний старт (fresh context) щоітерації — увесь стан тримає git і файлова система, не памʼять моделі.
- Три запобіжники в `ralph.sh`: `MAX_ITER`, `cost.log`, `trap` на Ctrl-C.
- `/ralph-prep` — власний skill, що генерує тонкий `PROMPT.md` зі story-файлу.
- Нативний Ralph «у коробці»: офіційний плагін `ralph-wiggum` / `/ralph-loop` (теплий Stop-hook) проти cold-start bash.

Задача в self-contained демо навмисне **абстрактна** (`slugify` kata-рівня): урок про
сам цикл, а не про конкретну фічу.

## Setup

```bash
cd modules/7-execution-scale/7.2-ralph-loop

make verify          # RED на чистому checkout: ModuleNotFoundError (app/ ще нема) — це стартовий стан
```

`uv` підтягне `pytest` сам. Потрібен встановлений `claude` CLI для реального прогону.

## Як запустити

| Команда | Що робить |
|---|---|
| `make verify` | DoD-проба (pytest). Червоно на старті, зелено після успішного Ralph. |
| `make demo` | Канонічний цикл на абстрактній задачі. Реально кличе `claude -p` (недетерміновано, ~$1-5). |
| `make demo-plugin` | Друкує кроки для нативного `/ralph-loop` (плагін `ralph-wiggum`) на тій самій задачі. |
| `make prep` | Нагадування, як (пере)згенерувати `PROMPT.md` через `/ralph-prep`. |
| `make clean` | Прибрати `app/`, `DONE`, `cost.log`, кеші. |

> `make demo` витрачає токени і недетерміноване. Перед запуском перевір `MAX_ITER` у
> `ralph.sh` і ввімкни алерт на сплеск витрат в Anthropic Console.

## Очікуваний вивід (≈3 ітерації)

```
--- Iteration 1 ---   claude генерує app/text_utils.py;  pytest падає (ще не все правильно / import)
--- Iteration 2 ---   холодний старт; бачить червоний тест у git status; доправляє; pytest зелений
--- Iteration 3 ---   холодний старт; atomic commit feat:; tracker → done; touch DONE
=== DONE found ... total iterations: 3 ===
```

Перевірка результату:

```bash
make verify                 # зелено
git log --oneline -1        # feat: slugify text helper
grep -i done tasks/tracker.md
ls DONE
```

Якщо `cost.log` показує `Hit MAX_ITER` — обвʼязка спрацювала, Ralph не довів задачу:
декомпозуй story або поправ `PROMPT.md`. Це не баг, це запобіжник.

## Screencast #1 (~3 хв) — canonical bash

```bash
# Pre-state: чисте дерево, нема app/, DONE, cost.log
cd modules/7-execution-scale/7.2-ralph-loop
git status && make verify          # verify RED (ModuleNotFoundError) — стартова точка

# Step 0 (~20с) — згенерувати тонкий PROMPT.md зі story (skill)
claude
#   /ralph-prep story-t1
#   cat PROMPT.md                   # пауза на секції Контекст / Завдання / DoD

# Step 1 (~20с) — показати обвʼязку
cat ralph.sh                        # підкреслити MAX_ITER, cost.log, trap INT

# Step 2 (~90с) — запуск
./ralph.sh                          # 3 холодні ітерації: import error → green → commit + touch DONE

# Step 3 (~20с) — verify
git log --oneline -3 && ls DONE && cat cost.log
```

## Нативний Ralph: плагін `ralph-wiggum`

Той самий патерн «у коробці». Anthropic публікує офіційний плагін `ralph-wiggum`, що дає
команди `/ralph-loop` (запустити цикл) і `/cancel-ralph` (обірвати). Робить він рівно те,
що ми зібрали руками в `ralph.sh`, але з однією принциповою відмінністю — як він поводиться
з контекстом між обертами:

| | canonical bash (`ralph.sh`) | `/ralph-loop` (плагін) |
|---|---|---|
| Як крутиться | новий `claude -p` щоітерації | Stop-hook ловить спробу виходу і згодовує промпт назад у ту саму сесію |
| Контекст між обертами | **холодний старт** (fresh) — чистий щоразу | **теплий** (warm) — накопичується |
| Сильна сторона | нема гниття контексту на довгих прогонах | памʼятає попередні ходи, тримає момент |
| Ризик | перечитує стан з диска щоразу | гниття контексту (context rot) |
| Запобіжник | `MAX_ITER` у скрипті | `--max-iterations` (головний; дефолт — без ліміту) |

Той самий синтаксис на тій самій абстрактній задачі (`story-t1` / `slugify`):

```bash
make clean                              # reset baseline: прибрати app/, DONE, cost.log

claude
#   /plugin                             # встановити плагін ralph-wiggum (Anthropic Verified)
#   /ralph-loop "Make pytest -q green per tasks/story-t1.md" \
#       --max-iterations 5 --completion-promise "ALL TESTS PASSING"
#   # Stop-hook у дії: completion-promise зʼявляється у відповіді → плагін виходить
#   /cancel-ralph                       # обірвати достроково, якщо треба
git diff
```

`--completion-promise` працює на **точному** збігу рядка — тож задати можна лише одну умову
завершення, а не кілька. Головний запобіжник — `--max-iterations`: за замовчуванням ліміту
обертів немає, тож став його завжди.

Плагін наводиться на будь-який backlog так само, як bash-варіант — задача `/ralph-loop`
від абстрактного `slugify` не залежить. `make demo-plugin` друкує ці кроки (slash-команда
живе всередині `claude`, не в чистому shell).

## Покриття концептів лекції

| Концепт лекції | Де у демо |
|---|---|
| Канонічний one-liner + sentinel-вихід | `ralph.sh` (цикл `while [ ! -f DONE ]`) |
| Три файли обвʼязки | `PROMPT.md`, `DONE` (генерується), `tasks/tracker.md` |
| Холодний старт / fresh context | кожна ітерація `ralph.sh` = новий `claude -p` |
| Бінарний DoD | `tasks/story-t1.md` → `pytest -q` зелений |
| Три запобіжники | `MAX_ITER`, `cost.log`, `trap INT` у `ralph.sh` |
| Ralph «у коробці» (plugin) | розділ «Нативний Ralph» (`/ralph-loop`, `make demo-plugin`) |

## Як перенести у свій проєкт

1. Скопіюй `ralph.sh` і `.claude/skills/ralph-prep/`.
2. Додай тонкий `CLAUDE.md` (стек + конвенції + заборони) і `tasks/tracker.md` зі своїми stories.
3. `/ralph-prep <story-id>` → `./ralph.sh`. Тримай DoD бінарним і `MAX_ITER` притомним.

## Sources

- `ghuntley.com/ralph` — оригінальний патерн «Ralph Wiggum as software engineer».
- `github.com/snarktank/ralph` — структурована реалізація: свіжий контекст щоітерації, памʼять на диску (git + tracker + накопичені уроки), quality gates перед commit.
- `github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum` — офіційний плагін (`/ralph-loop`).
- Повний список — у `Sources.md` лекції 7.2.
