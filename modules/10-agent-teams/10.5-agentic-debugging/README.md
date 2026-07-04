# Demo: 10.5 Agentic Debugging

**Module:** 10 - Agent Teams
**Lecture:** 10.5 Agentic Debugging

## Що показує

Живий, **безтокенний** `git bisect run`, який знаходить винний коміт автоматично. У теці `sandbox/`
будується свіжий git-репозиторій із seed-історією рівно **16 комітів** крихітного Node-пакета
`billing` (обчислення інвойса: субтотал → знижка → податок → округлення). У коміт **#9** тихо
підсаджено регрес. `reproduce.sh` відтворює баг простим `exit 0/1`, а `git bisect run ../reproduce.sh`
за ~4 кроки (log2(16)=4) доходить рівно до коміту #9.

Це фікстур для `🎬`-скринкаста #3 лекції: агент пише мінімальний reproduce-скрипт і віддає його
`git bisect`, а не вручну перебирає коміти.

## Регрес (для викладача; у скринкасті НЕ спойлерити)

Коміт #9 «refactor: extract discount application» виносить inline-знижку в `src/discount.js`.
Винесена `applyDiscount` округлює **проміжну** суму зі знижкою до цілих центів
(`Math.round(discounted * 100) / 100`) — виглядає як «чисте валютне значення», але зрізає
суб-центову дрібку, яку далі бачив крок податку. Для інвойса з дробовою знижкою й дробовою
податковою ставкою фінальний total осідає на цент нижче.

- Тригер-кейс: `19.99 × 3` (субтотал 59.97), знижка 10%, податок 8.25%.
- До #9 (коміти 1-8): `total = 58.43` → `reproduce.sh` exit 0.
- З #9 (коміти 9-16): `total = 58.42` → `reproduce.sh` exit 1.

Коміти 10-16 — інші зміни (formatting helper, валідація, extract computeTax, CHANGELOG, CLI-тест,
доки), які баг **не лагодять і не маскують**. Наявні юніт-тести (`node --test`) зелені весь час:
вони навмисно не покривають цей граничний кейс — саме тому баг доводиться ловити бісекцією, а не
сьютом. Хеш винного коміту записується в `sandbox/.culprit` (git-ignored) лише для звірки в
`make bisect`.

## Pre-requisites

- Node 18+ (тільки вбудовані модулі, **без `npm install`**).
- git.
- Claude Code - для живого агент-take (скринкаст #3).

## Як запустити

```bash
cd modules/10-agent-teams/10.5-agentic-debugging

make setup     # свіжий sandbox-репо з 16 seed-комітами (детерміновані хеші)
make repro     # reproduce.sh на HEAD → exit 1 (баг присутній)
make bisect    # повний цикл: git bisect run + звірка з .culprit → PASS
make clean     # прибрати sandbox/ і .bisect.log
```

Буквальні команди бісекції (те, що бачить глядач), із кореня `sandbox/`:

```bash
cd sandbox
git bisect start HEAD $(git rev-list --max-parents=0 HEAD)   # bad=HEAD, good=перший коміт
git bisect run bash ../reproduce.sh                          # автопрогін
# → "<hash> is the first bad commit"  (коміт #9)
git bisect reset
```

## Структура пакета

| Файл | Що це |
|---|---|
| `setup.sh` | будує `sandbox/` як git-репо з 16 seed-комітами; регрес у #9; пише `.culprit` |
| `reproduce.sh` | мінімальний безтокенний тест: `buildInvoice` на тригер-кейсі, exit 0/1 |
| `Makefile` | `setup` / `repro` / `bisect` / `clean` |
| `screencast-prompts.md` | runbook скринкаста #3 (агентний промпт + очікувані кроки) |
| `sandbox/` | генерований git-репо (git-ignored, не комітиться) |

## Чому reproduce.sh працює на старих комітах

`reproduce.sh` смикає лише **стабільний публічний інтерфейс** `buildInvoice(lineItems, opts)`, що
існує з першого коміту. Внутрішня будова (inline-знижка → `applyDiscount` → `computeTax`) міняється
по ходу історії, але сигнатура й контракт `total` — ні. Тому `git bisect` може ганяти той самий
скрипт на будь-якому checkout: `exit 0` = good, `exit 1` = bad.

## Чесні нотатки

- `make bisect` детермінований: хеші комітів фіксовані (`GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE` +
  локальна identity), тож `.culprit` однаковий на кожній перебудові, і бісекція завжди зупиняється на #9.
- `make repro` навмисно завершується з кодом 1 (`make: *** [repro] Error 1`) — це і є доказ, що баг
  відтворюється на HEAD, а не помилка збірки.
- ANTHROPIC_API_KEY не потрібен: і сид-історія, і бісекція — це звичайний git + node. Агентна
  частина (агент сам пише `reproduce.sh` і запускає `git bisect run`) ведеться інтерактивно в
  Claude Code — див. `screencast-prompts.md`.

## Source

- Лекція 10.5 Agentic Debugging (`Module 10 / Lecture 5`).
- Фікстур успадковує стиль сусідніх пакетів `10.1-subagents` (seed-історія з `Co-Authored-By`,
  чистий `node` без npm) і `10.3-evals-regression` (Makefile-цілі, PASS/FAIL-звірка).
