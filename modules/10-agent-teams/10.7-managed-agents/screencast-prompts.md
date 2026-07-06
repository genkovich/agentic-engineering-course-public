# Screencast-сценарії · 10.7 Managed Agents: агентний harness як API

Один hosted code-reviewer ревʼює `review-target/` - маленький course-репо з
посіяним багом подвійного округлення (58.42 замість 58.43). Усі чотири
скринкасти працюють на ЦЬОМУ репозиторії, не на абстрактних снипетах.

**Спільна передумова:**

```bash
cp .env.example .env          # встав свій ANTHROPIC_API_KEY
make install                  # pip install anthropic
make setup                    # раз: створює агента+оточення, пише .env (ПЛАТНО)
```

> ⚠️ Кожен `python *.py` б'є в hosted Managed Agents API і коштує токенів. Вихід
> недетермінований - запис може взяти кілька дублів. Якщо прогін збоїть або дасть
> не той результат, у кадр іде `fallback/<script>.txt` - детермінований транскрипт
> того самого сценарію. Прогони, які виходять чисто, дублюємо записом
> session-viewer на platform.claude.com.

`Тригеримо`-промпти нижче байт-у-байт збігаються з `Тригеримо` в тілі лекції.

---

## 🎬 Сценарій #1 — hosted code-reviewer ревʼює course-репо

**Скрипт:** `run.py` · **Фолбек:** `fallback/run.txt`

- **Pre-state:** `cat review-target/src/invoice.js` і `cat review-target/src/discount.js` - подвійне округлення на екрані; `.env` з `AGENT_ID`/`ENV_ID` після `make setup`.
- **Тригеримо:** `python run.py` (усередині - `user.message`: «Зроби код-рев'ю модуля рахунків нижче. Шукай помилки коректності, особливо в грошовій математиці. Тести зелені - не довіряй їм наосліп.»)
- **Дивимось:** сесія стартує в статусі idle, `user.message` запускає роботу; стрім сипле `[Using tool: read]`/`[Using tool: bash]`; знахідка - подвійне округлення, доказ 58.42 vs 58.43. Паралельно та сама сесія видно в session-viewer на platform.claude.com.
- **Кадр-висновок:** твій агент рев'ює твій репозиторій, а loop і sandbox тримає Anthropic.

## 🎬 Сценарій #2 — перебити рев'ю посеред і перенаправити

**Скрипт:** `interrupt.py` · **Фолбек:** `fallback/interrupt.txt`

- **Pre-state:** `.env` готовий; рев'ю з #1 щойно бачили.
- **Тригеримо:** `python interrupt.py` (усередині - `user.interrupt` + `user.message`: «Стоп. Форматування і стиль не чіпай. Зосередься тільки на одному: чи коректно рахується сума в src/invoice.js та src/discount.js. Дай один найважливіший баг округлення з доказом на конкретних числах.»)
- **Дивимось:** `user.interrupt` зупиняє агента посеред ходу; новий `user.message` звужує напрямок; агент підтверджує і повертає лише баг округлення.
- **Кадр-висновок:** сесія жива й керована - її можна перебити і повернути на курс, не перезапускаючи.

## 🎬 Сценарій #3 — define-outcome: рубрика замість інструкції (КЛІМАКС #1)

**Скрипт:** `outcome.py` · **Рубрика:** `rubric.md` · **Фолбек:** `fallback/outcome.txt`

- **Pre-state:** `cat rubric.md` - вимірювані критерії «спіймати цент».
- **Тригеримо:** `python outcome.py` (усередині - `user.define_outcome` з `description` «Дай код-рев'ю, яке ловить баг подвійного округлення» + `rubric` (текст `rubric.md`) + `max_iterations: 5`).
- **Дивимось:** grader в окремому контексті оцінює рев'ю; ітерація 1 - FAIL (баг не названо), ітерація 2 - PASS (58.42 vs 58.43 з доказом); агент ітерував сам до критеріїв.
- **Кадр-висновок:** ти описав, що таке «done», а не як його досягти - grader зробив решту.

## 🎬 Сценарій #4 — координатор розкидає рев'ю на треди (КЛІМАКС #2)

**Скрипт:** `multiagent.py` · **Фолбек:** `fallback/multiagent.txt`

- **Pre-state:** `.env` готовий.
- **Тригеримо:** `python multiagent.py` (створює 3 спеціалістів bug/test/docs + координатора з роль-ростером `multiagent`, потім `user.message` із рев'ю-запитом).
- **Дивимось:** координатор спавнить три session threads (спільний sandbox, ізольовані контексти); кожен спеціаліст повертає свою знахідку; координатор зводить у один звіт.
- **Кадр-висновок:** та сама ідея, що Agent Teams у 10.4, тільки як один Managed-Agents-сеанс за API.

---

## Мапа сценаріїв

| # | Скрипт | Механізм Managed Agents | Що доводить |
|---|---|---|---|
| 1 | `run.py` | session + SSE-стрім + `user.message` | hosted loop ревʼює реальний репо |
| 2 | `interrupt.py` | `user.interrupt` + redirect | сесія керована наживо |
| 3 | `outcome.py` | `user.define_outcome` + grader | вихід за рубрикою, self-eval loop |
| 4 | `multiagent.py` | `multiagent` coordinator + threads | API-аналог Agent Teams |

## Recording runbook

1. `cp .env.example .env`, встав `ANTHROPIC_API_KEY`.
2. `make install`, потім `make setup` (раз; запам'ятай, що це платний ресурс).
3. `make parse` - переконайся, що всі скрипти парсяться перед записом.
4. Пиши кожен сценарій із `python <script>.py`; поряд відкрий session-viewer на
   platform.claude.com і покажи ту саму сесію в UI.
5. Якщо прогін недетермінований або збоїть - у кадр іде `fallback/<script>.txt`.
6. Після запису: видали тестові сесії через API (`session-operations`), почисти
   `.env` від id, якщо репо йде в мірор.
