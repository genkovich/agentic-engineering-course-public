# Screencast-сценарії · 10.3 Evals і регресійне тестування агентів

П'ять скринкастів, нумерація збігається з тілом лекції (#1-#5). Скринкасти - ЛИШЕ
живі прогони; статичні файли (frontmatter, case.json, check.py, promptfooconfig.yaml)
показуються слайдами - див. блоки «Показати» у тілі лекції.

Наскрізна арка: «працює → зламали конфіг → eval впіймав → полагодили».
Центральна теза: **детермінований грейдер над недетермінованим агентом**.

Спільна передумова:

```bash
cd ~/sources/agentic-engineering-course/modules/10-agent-teams/10.3-evals-regression
make check          # шар 0 - зелено за секунди, без токенів
# для #2-#5 потрібен claude CLI / ANTHROPIC_API_KEY - прогони коштують токени
```

> Кроки з `make evals*` і `promptfoo eval` ганяють **реального** агента: недетерміновані,
> плануй 2-3 дублі на кожен.

---

## 🎬 Скринкаст #1 (~1.5 хв) - шар 0 наживо: лінт ловить диф tools

- **Поверхня:** `tests/agent/lint.py`, `.claude/agents/ro-reviewer.md`, контракт `EXPECTED_AGENT_TOOLS`.
- **Pre-state:** чистий checkout; `make check` ще не запускали в кадрі.
- **Тригеримо** (red-green на лінті, нуль токенів):
  1. `make check` - зелена матриця: контракт агентів, settings.json, синтаксис, структура кейсів.
  2. `cp tests/agent/cases/subagent-tools-allowlist/broken/ro-reviewer.md .claude/agents/ro-reviewer.md` - «хтось покращив» рев'юера.
  3. `make check` - два червоні рядки: `зайве: ['Edit', 'Write']`.
  4. `git checkout .claude/agents/ro-reviewer.md && make check` - знову зелено.
- **Кадр-висновок:** диф `+Edit, +Write` спіймано за секунду і безкоштовно - статичний лінт зобов'язаний бути першим шаром. Але він прочитав лише ТЕКСТ конфігурації; чи змінилась ПОВЕДІНКА - питання до наступного шару.

---

## 🎬 Скринкаст #2 (~2 хв) - red-green на живому агенті: BREAK=1

- **Агент:** ro-reviewer проти `broken/ro-reviewer.md` (+Edit, +Write у tools; body командує виправляти). **Кейс:** `subagent-tools-allowlist`.
- **Pre-state:** `make check` зелений; короткий `diff .claude/agents/ro-reviewer.md tests/agent/cases/subagent-tools-allowlist/broken/ro-reviewer.md` - різниця в рядку tools і в body-наказі.
- **Тригеримо** (три прогони поспіль):
  1. `make evals-one CASE=subagent-tools-allowlist` - PASS: рев'ю з вердиктом є, src/ незайманий.
  2. `make evals-one CASE=subagent-tools-allowlist BREAK=1` - FAIL: зламаний рев'юер відредагував src/discount.js.
  3. `make evals-one CASE=subagent-tools-allowlist` - конфіг справжній, знову PASS.
- **GUARD-кадр:** у FAIL-прогоні мусить бути видно і червоний рядок «ro-reviewer не змінив жодного файла у src/», і сам diff: `git -C tmp/run-subagent-tools-allowlist diff --stat` - без цих двох кадрів причинність «конфіг → поведінка» не читається.
- **Кадр-висновок:** ми не зламали жодного рядка коду продукту - лише конфігурацію агента. І eval це впіймав. Це і є регресійний тест для `.claude/`.

Озвучка: «BREAK стейджить зламану версію конфіга у пісочницю - регресія відтворюється
однією командою, без брудного git». Зламаний агент клює на провокацію не щоразу
(недетермінізм) - плануй дублі.

---

## 🎬 Скринкаст #3 (~1.5 хв) - сьют цілком + читання транскрипта

- **Поверхня:** `make evals` (усі 6 кейсів), `tests/agent/lib/checks.py` як CLI-читалка.
- **Pre-state:** `make clean` - старі пісочниці прибрані.
- **Тригеримо:**
  1. `make evals` - двигун жене кейси один за одним; у кадрі видно по кожному: пісочниця → `claude -p …` → рядки грейдера → підсумкова матриця з cost по кейсу.
  2. `python3 tests/agent/lib/checks.py tmp/run-route-auth/transcript.jsonl` - зріз «що агент реально робив»: лічильник викликів інструментів + cost/turns.
- **Дивимось:** матриця PASS/FAIL; сумарний час; кейс `tdd-three-commits` може мигнути (чесно лишаємо в кадрі, якщо мигнув - це ілюстрація глави про надійність).
- **Кадр-висновок:** шість кейсів - шість конфігів під захистом; вечірній `make evals` відповідає на питання «чи все ще працює те, що працювало вчора».

---

## 🎬 Скринкаст #4 (~2 хв) - Promptfoo: перший кейс + веб-переглядач

- **Поверхня:** `promptfoo/promptfooconfig.yaml` (устрій показано слайдом ДО скринкасту - в кадрі лише прогін).
- **Pre-state:** `cd promptfoo && bash setup.sh` - чистий workdir/; `ANTHROPIC_API_KEY` в env.
- **Тригеримо:**
  1. `npx promptfoo@latest eval --no-cache` - термінальна матриця: 2 тести × асерти (contains, is-json, python, trajectory, cost).
  2. `npx promptfoo@latest view` - веб-переглядач: той самий прогін, кожен асерт розгортається з reason python-грейдера.
- **Дивимось:** у view відкриваємо python-асерт `check_route.py` - reason «всі три HTTP-контракти виконані»; показуємо trajectory:tool-used.
- **Кадр-висновок:** принцип не змінився - детерміновані асерти на поведінку; змінився масштаб інструмента: матриця, історія прогонів, готові типи асертів з коробки.

Ризик дубля: `is-json`-тест може почервоніти, якщо агент не втримав формат - лишаємо
як чесну ілюстрацію «контракт на текст крихкіший за контракт на outcome».

---

## 🎬 Скринкаст #5 (~2 хв) - Promptfoo масштабування: кастомний провайдер + LLM-суддя

- **Поверхня:** `promptfoo/review/` - provider.py жене `claude -p --agent ro-reviewer` тим самим двигуном, що харнес; llm-rubric оцінює якість тексту рев'ю.
- **Pre-state:** `cd promptfoo/review`; конфіг показано слайдом до скринкасту.
- **Тригеримо:**
  1. `npx promptfoo@latest eval --no-cache` - PASS: regex-вердикт, python-грейдер (src/ чистий), rubric ≥0.7.
  2. `BREAK=1 npx promptfoo@latest eval --no-cache` - зламаний конфіг: python-грейдер червоніє («агент ЗМІНИВ файли у src/»), rubric теж (рев'ю стверджує, що виправило).
  3. `npx promptfoo@latest view` - поруч два прогони: зелений і червоний.
- **Кадр-висновок:** провайдер - це просто python-файл: усе, що вмієш запустити з коду, Promptfoo вміє тестувати. Суддя-модель доповнює детермінований шар там, де якість тексту інакше не зловиш.

Озвучка: rubric-суддя недетермінований і коштує грошей на кожен прогін - тому він
ДОДАТОК до python-грейдера, не заміна.

---

## Runbook (перед записом)

- [ ] `make check` зелений на чистому checkout.
- [ ] Живий `make evals-one CASE=subagent-tools-allowlist` - PASS (звірено 2026-07-04: cost ~$0.09, 34с).
- [ ] Живий `make evals` цілком - подивитись, які кейси мигтять, спланувати дублі.
- [ ] `promptfoo eval` обох конфігів - НЕ звірено 2026-07-04 (не було ANTHROPIC_API_KEY в env); перевірити при записі, чеклист у `promptfoo/README.md`.
- [ ] Термінал: шрифт ≥16pt, GitHub dark, вікно 120×32.
