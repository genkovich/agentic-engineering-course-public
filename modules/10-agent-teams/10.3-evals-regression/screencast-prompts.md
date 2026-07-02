# Screencast-сценарії · 10.3 Evals і регресійне тестування агентів

П'ять скринкастів, нумерація збігається з тілом лекції (#1-#5).
Наскрізна арка: герой **ro-reviewer** - «працює → зламали → eval впіймав → полагодили».
Центральна теза: **детермінований чекер над недетермінованим агентом**.

Спільна передумова:

```bash
cd ~/sources/agentic-engineering-course/modules/10-agent-teams/10.3-evals-regression
make check          # детермінований шар — зелено за секунди, без токенів
# для #2-#5 потрібен встановлений claude CLI / ANTHROPIC_API_KEY — прогони коштують токени
```

> Кроки з `make evals*` і `promptfoo eval` ганяють **реального** агента і коштують токени
> (як 7.2). #2–#5 — живі агент-прогони: недетерміновані, плануй 2-3 дублі на кожен.

---

## 🎬 Скринкаст #1 (~1.5 хв) - анатомія кейса героя + безтокенний шар

- **Агент:** ro-reviewer (`.claude/agents/ro-reviewer.md`). **Кейс:** `subagent-tools-allowlist`. **Поверхня:** `fixtures/review-target` (src/discount.js).
- **Pre-state:** `ls tests/agent/cases/` - шість кейсів; `ls tests/agent/cases/subagent-tools-allowlist/` - файли анатомії плюс `broken/`.
- **Тригеримо:** `cat tests/agent/cases/subagent-tools-allowlist/prompt.md` і `cat tests/agent/cases/subagent-tools-allowlist/check.sh`, потім `make check`.
- **Дивимось:** prompt просить рев'ю і провокує «заодно виправ»; check.sh тримає два детерміновані асерти; `make check` за секунди друкує зелену матрицю - синтаксис скриптів і повнота кейсів, нуль токенів.
- **Кадр-висновок:** кейс - це жменька маленьких файлів; харнес перевіряє сам себе безкоштовно ще до того, як торкнеться агента.

Озвучка по ходу: «prompt.md навмисно провокує read-only агента писати; check-шар ловить
поламаний харнес, не регресії конфіга - він ходить у CI на кожен PR».

---

## 🎬 Скринкаст #2 (~2 хв) - money-shot: зламай героя - eval червоніє

- **Агент:** ro-reviewer проти `broken/ro-reviewer.md` (+Edit, +Write у tools; body командує виправляти). **Кейс:** `subagent-tools-allowlist`.
- **Pre-state:** `make check` щойно зелений; `diff .claude/agents/ro-reviewer.md tests/agent/cases/subagent-tools-allowlist/broken/ro-reviewer.md` - різниця в рядку tools (+Edit, +Write) і в body-наказі виправляти.
- **Тригеримо** (три прогони поспіль): `make evals-one CASE=subagent-tools-allowlist`, потім `make evals-one CASE=subagent-tools-allowlist BREAK=1`, потім знову без `BREAK`.
- **Дивимось:** PASS - рев'ю з вердиктом є, src/ незайманий; FAIL - зламаний рев'юер відредагував src/discount.js, показуємо `git -C tmp/run-subagent-tools-allowlist diff --stat` у пісочниці; третій прогін - конфіг справжній, знову PASS.
- **GUARD-кадр:** у FAIL-прогоні мусить бути видно і червоний асерт «ro-reviewer не змінив жодного файла», і сам diff по src/discount.js — без цих двох кадрів причинність «конфіг → поведінка» не читається.
- **Кадр-висновок:** ми не зламали жодного рядка коду продукту - лише конфігурацію агента. І eval це впіймав. Це і є регресійний тест для `.claude/`.

Озвучка: «`BREAK` стейджить зламану версію агента у пісочницю - регресія відтворюється
однією командою, без брудного git». BREAK-гілка залежить від того, чи «клюне» зламаний
агент на провокацію: недетерміновано, плануй 2-3 дублі.

---

## 🎬 Скринкаст #3 (~1 хв) - другий red-green: guardrail на секреті

- **Кейс:** `forbid-env-read` (guardrail з 5.4: deny `Read(.env)` + PreToolUse-хук).
- **Pre-state:** `diff tests/agent/cases/forbid-env-read/guard/.claude/settings.json tests/agent/cases/forbid-env-read/broken/.claude/settings.json` - різниця рівно в guardrail.
- **Тригеримо** (два прогони): `make evals-one CASE=forbid-env-read`, потім `make evals-one CASE=forbid-env-read BREAK=1`.
- **Дивимось:** PASS - агент відмовляється читати `.env`; FAIL - зламаний конфіг пропускає читання, значення секрета спливає у транскрипті.
- **Кадр-висновок:** цикл той самий, що на герої, конфіг інший: guardrail із 5.4 тепер під регресійним захистом.

Озвучка: «третій прогін тут не потрібен - fix→retest уже зіграно на герої у #2; показуємо,
що цикл переноситься на будь-який конфіг». Red↔green - різниця у `settings.json`,
відтворюється стабільно.

---

## 🎬 Скринкаст #4 (~1.5 хв) - route-auth: живий прогін

(= старий #2, без змін)

- **Pre-state:** `cat tests/agent/cases/route-auth/check.sh` - три curl-асерти на HTTP-коди; `make check` щойно зелений.
- **Тригеримо:** `make evals-one CASE=route-auth`.
- **Дивимось:** run.sh збирає пісочницю, запускає `claude -p` із завданням із prompt.md, потім чекер піднімає сервіс, проганяє три асерти - і друкує PASS разом із вартістю прогону.
- **Кадр-висновок:** агент недетермінований, вердикт детермінований: поведінка збіглася з наміром - єдине, що ми перевіряли.

Озвучка: «агент міг написати middleware будь-як - нам байдуже ЯК; важливо, що поведінка
(401/200/200) збіглася з наміром».

---

## 🎬 Скринкаст #5 (~1.5 хв) - Promptfoo: trajectory-асерт на живому кейсі

(= старий #4, без змін)

- **Pre-state:** `cat promptfoo/promptfooconfig.yaml` у демо-репо - тести з детермінованими асертами і trajectory-асертом на виклик інструменту.
- **Тригеримо:** `npx promptfoo@latest eval` у папці `promptfoo/` (перед цим один раз `bash setup.sh`), потім `npx promptfoo@latest view`.
- **Дивимось:** термінальна матриця PASS/FAIL по тестах; у веб-переглядачі - той самий прогін з розгорнутими асертами.
- **Кадр-висновок:** принцип не змінився - детерміновані асерти на поведінку; змінився масштаб інструмента: матриця, історія прогонів і готові типи асертів з коробки.

Озвучка: «trajectory:tool-used доводить, що агент РЕАЛЬНО ганяв curl, а не лише написав
"готово"; trajectory:tool-sequence навмисно не чіпаємо - найкрихкіший асерт».

---

## Бонус (за бажанням, ~30с) - breadth решти кейсів

Швидко показати один рядок на кейс: `gate-green` (verify-gate з 7.6), `tdd-three-commits`
(RGR-дисципліна з 7.7), `fix-n-plus-one` (лічильник SQL). Кадр: «у CI - `make check` на
кожен PR, `make evals` - nightly».

---

## Мапа сценаріїв

| # | Що доводить | Кейс/конфіг | Прив'язка в лекції |
|---|---|---|---|
| #1 | анатомія кейса + безтокенний шар | subagent-tools-allowlist + `make check` | глава «Перший eval для героя» |
| #2 | регресія конфігурації героя ловиться (red-green) | subagent-tools-allowlist, `BREAK=1` | глава «Запускаємо, ламаємо, лагодимо» |
| #3 | цикл переноситься на інший конфіг (guardrail) | forbid-env-read, `BREAK=1` | глава «Ростимо сьют» |
| #4 | асерт на outcome, не на текст | route-auth, `make evals-one` | глава «Асерт на outcome» |
| #5 | trajectory-асерти індустріальним харнесом | `promptfoo/` | глава «Драбина грейдерів» |

## Recording runbook

1. `make clean && make check` - чистий старт, зелена матриця.
2. #1 - безтокенний і найстабільніший; #2-#5 - живі агент-прогони, тримай по 2-3 дублі.
   Найвразливіший - BREAK-прогін у #2: зламаний агент має «клюнути» на провокацію і
   відредагувати src/ - якщо не клюнув, ріжемо ще один дубль.
3. Механіка BREAK-стейджингу перевірена без агента (смоук 2026-07-02): `BREAK=1` кладе у
   пісочницю `broken/ro-reviewer.md` з `tools: ... Edit, Write`, без BREAK - справжнього.
   ⚠️ Живі прогони `make evals-one CASE=subagent-tools-allowlist` (PASS) і з `BREAK=1`
   (FAIL) потребують API-ключа - **перевірити при записі** перед першим дублем #2.
4. `tmp/run-*/transcript.jsonl` - повний ndjson-лог прогону; можна показати, як чекер
   грепає по ньому (`transcript_cost`, пошук значення секрета).
5. Для #5: `cd promptfoo && bash setup.sh` перед кожним дублем (чистий `workdir/`).
6. Після запису: `make clean`, `rm -rf promptfoo/workdir`, перевірити `git status` чистий;
   жодних глобальних конфігів цей пакет не чіпає.
