# Demo: 10.4 Agent Teams

**Module:** 10 - Agent Teams
**Lecture:** 10.4 Agent Teams: команди агентів-пірів

## Що показує

Пісочниця для **одного наскрізного прогону** лекції 10.4: команда з трьох тіммейтів-пірів
(billing-owner / queue-owner / reports-owner) будує фічу «звіт по знижках» на монорепі
з 10.1. На цьому фікстурі знімаються всі п'ять `🎬`-епізодів лекції: спавн команди,
спільний список задач (і його JSON-файли на диску), peer-контракт через `SendMessage`,
quality gate на `TaskCompleted` і фінал із shutdown.

`make sandbox` будує той самий монореп, що в 10.1 (ті самі 5 seed-комітів із
`../10.1-subagents/template`), і додає 6-й **team-prep коміт** — усе, що лекція просить
покласти в пісочницю ЩЕ ДО спавну команди:

| Артефакт | Що робить |
|---|---|
| `.claude/settings.json` | env-флаг `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, реєстрація хуків, permissions.allow для тестів і git |
| `.claude/hooks/task-gate.sh` | quality gate з епізоду 4 лекції, дослівно: `node --test` зелений → exit 0; червоний → stderr-фідбек + exit 2, задача не закривається |
| `.claude/hooks/task-log.sh` | пасивний інспектор: складає stdin-payload подій `TaskCreated` / `TaskCompleted` / `TeammateIdle` у `.claude/logs/team-events.jsonl` |
| `packages/reports/__tests__/summary.test.js` | детермінована заміна навмисно flaky-тесту з 10.1 — інакше TaskCompleted-гейт мигав би випадковим червоним |
| `CLAUDE.md` | етикет монорепа 10.1 + командні правила (file-disjoint володіння, контракти через SendMessage, тести перед закриттям задачі) |

Три пакети — три власники: `billing` публікує подію `discount.applied`, `queue` її
доставляє, `reports` агрегує у звіт. Четвертий пакет `auth` лишається нейтральною
територією — ніхто з owner-ів його не чіпає.

## Pre-requisites

- Node 18+ (тільки вбудований `node:test`, **без `npm install`**).
- git.
- Claude Code із підтримкою Agent Teams (experimental; розроблено на v2.1.201) — для
  живого прогону. Базовий сетап (`make sandbox` / `test` / `gate-test`) працює без
  Claude Code і без API key.

## Як запустити

```bash
cd modules/10-agent-teams/10.4-agent-teams

make sandbox     # монореп 10.1 + team-prep коміт (хук, env-флаг, зелений сьют)
make test        # node --test у пісочниці: ВСІ пакети зелені (flaky нейтралізовано)
make gate-test   # обидві гілки task-gate.sh ізольовано: exit 0 і exit 2 + stderr
make reset       # clean + sandbox: перебудувати чисто між дублями
make clean       # прибрати sandbox/

cd sandbox
claude           # spawn-промпт зі screencast-prompts.md, епізод 1
```

Спостерігати за командою з другого термінала:

```bash
ls -a ~/.claude/tasks/<ім'я-команди>/         # JSON-файли задач, .lock, .highwatermark
cat ~/.claude/tasks/<ім'я-команди>/3.json     # status / blocks / blockedBy наживо
cat sandbox/.claude/logs/team-events.jsonl    # payload-и team-хуків
ls ~/.claude/teams/                           # конфіг команди (зникає після сесії)
```

## Мапа скринкастів

Storyboard усіх п'яти епізодів (копі-пейст промпти, Pre-state, що дивитись,
кадр-висновок) — у [`screencast-prompts.md`](./screencast-prompts.md). Коротка мапа:

| Епізод | Слайд | Механізм |
|---|---|---|
| #1 спавн команди | 3 | spawn природною мовою, file-disjoint план |
| #2 список задач | 4-5 | shared task list; JSON-файли у `~/.claude/tasks/` |
| #3 peer-контракт | 6 | `SendMessage`: пошта замість ефіру |
| #4 хук-гейт | 7 | `TaskCompleted` + exit 2 тримає планку |
| #5 фінал | 8 | shutdown consent; команда одноразова, список задач — ні |

## Чесні нотатки

Усе нижче звірено живим прогоном фічі «звіт по знижках» 2026-07-05 на Claude Code
v2.1.201 (лід Fable 5 + три тіммейти на Sonnet; ~21 хв, чотири задачі, три коміти,
хук-блок і закриття з другої спроби — повна хореографія п'яти епізодів лекції).

- Agent Teams — experimental: вмикається `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
  (тут — через env-блок settings.json пісочниці), поведінка й формати можуть змінитись
  будь-яким білдом. Перед записом звір флоу з live-доками.
- **Headless не працює.** `claude -p` команду не спавнить: запит на тіммейта деградує
  в одноразового субагента, каталоги в `~/.claude/teams|tasks` не з'являються. Прогін
  і запис — лише інтерактивна сесія.
- **Trust-діалог.** Без «Yes, I trust this folder» на першому старті Claude Code мовчки
  ігнорує `permissions.allow` із settings.json пісочниці (хуки й env-блок при цьому
  працюють) — і агенти впираються в permission-промпти.
- Формат файлів у `~/.claude/tasks/{team}/` не документований — читати можна, міняти
  краще через ліда. Звірено на диску: каталог `session-XXXXXXXX` (як на слайді 5),
  усередині `N.json` + `.lock` + `.highwatermark` (лічильник id); поля
  `id/subject/description/activeForm/owner/status/blocks/blockedBy`. Конфіг команди —
  `~/.claude/teams/{team}/config.json` + `inboxes/*.json` (пошта тіммейтів).
- **Життєвий цикл підтверджено:** після `/exit` каталог команди зникає, каталог задач
  лишається. Нюанс: лід під кінець може заархівувати завершені задачі — тоді в каталозі
  зостаються лише `.lock` і `.highwatermark`.
- `blockedBy` стримує самозахоплення (self-claim), а не роботу: явно призначену задачу
  тіммейт може вести й закрити ще до розблокування (у прогоні #3 закрилась раніше #1).
- `TaskCompleted` може спрацювати кілька разів на ту саму задачу (у прогоні — 12 подій
  на 4 задачі) — пиши гейт ідемпотентним; `node --test` у task-gate.sh таким і є.
- В `acceptEdits` спавн команди проходить без окремого підтвердження; кадр
  «підтвердження спавну» знімай у дефолтному режимі. `bypassPermissions` НЕ бери:
  він мовчки вимикає хуки — епізод 4 з ним не відбудеться.
- `CLAUDE_CODE_TASK_LIST_ID=discount-report` перевірено: звичайна сесія створює
  іменований каталог у `~/.claude/tasks/` і пише задачі туди. Чи підхоплює його команда
  замість session-derived каталогу — не перевіряли.
- Живі агент-сесії недетерміновані: фікстур гарантує стартовий стан, не однакові кроки
  агентів. Між дублями — `make reset`.
- У plan mode команда споживає ~7× токенів проти звичайної сесії; тіммейтів на запис
  сади на Sonnet (дешевше і швидше).
- Хук `task-gate.sh` ганяє ВЕСЬ сьют репозиторію — для крихітного монорепа це секунди.
  У великому монорепі звужуй гейт до пакета власника через `task_subject` + `jq`
  (лекція, епізод 4).

## Source

- Лекція 10.4 Agent Teams (`Module 10 / Lecture 4`).
- Fixtures = template з [`10.1-subagents`](../10.1-subagents) (seed-історія,
  `Co-Authored-By`), стабілізований під командний гейт. Хук-стиль — 5.4 (stdin-payload,
  логи в `.claude/logs/`), сам task-gate.sh — дослівно рецепт лекції 10.4.
