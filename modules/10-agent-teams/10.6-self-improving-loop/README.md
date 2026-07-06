# Demo 10.6 — Self-Improvement Loop (skill self-editor)

Наскрізний демо-кіт до лекції 10.6. Реалізує петлю самопокращення за
патерном C (inner/outer, skill сам себе редагує) на конкретній задачі:
автоматичний тріаж вхідних issue.

## Що всередині

- **Inner loop** — скіл `.claude/skills/triage/SKILL.md` лейблить issue
  (`bug` / `feature` / `question` / `docs`). Наївна версія лейблить за
  ключовими словами і плутає питання з багами: held-out бал **14/20**.
- **Held-out суддя** — `eval/held-out.jsonl` (20 розмічених issue) + `eval/judge.py`
  (бінарний `predicted == gold`) + `eval/run.py` (прогін і бал). Плюс людські
  релейбли в git-історії (`git log --oneline`) як другий сигнал.
- **Outer loop** — субагент `.claude/agents/skill-improver.md` читає held-out
  провали + релейбли, дописує урок у `lessons.md`, додає одне правило в
  `SKILL.md` і відкриває **draft PR**. Після його правки бал **19/20**.
- **Дві пастки** — тихий баг обрізки `skill_md[:1500]` (`eval/run.py --buggy`) і
  забруднений seed (`make seed-bad`), що «ідеально» оптимізує в хибну ціль.

## Петля

```
issue -> triage (SKILL.md) -> лейбл          [inner loop, у проді]
              |
   held-out eval + людські релейбли          [сигнал]
              |
   skill-improver: lessons.md -> diff у SKILL.md -> re-eval -> draft PR   [outer loop, за розкладом]
              |
        людина рев'ює draft PR                [ворота]
```

## Швидкий старт

```bash
make setup        # будує sandbox/ (наївний скіл, held-out, історія релейблів)
make judge        # held-out бал наївного скіла: 14/20
make apply-fix    # детермінований стенд-ін outer loop: дописує правило -> 19/20
make seed-bad     # хибна ціль: забруднює gold -> наївний скіл 20/20 (оптимізує в хибне)
make fix-seed     # повертає чесний gold -> 14/20
make help         # усі таргети
```

Живий прогін outer loop (потрібен `ANTHROPIC_API_KEY` + `gh auth`):

```bash
cd sandbox
claude -p --agent skill-improver 'run one improvement cycle'
```

Повний сторіборд чотирьох скринкастів - `screencast-prompts.md`.

## Чесні нотатки

- **Детермінований стенд-ін замість живого агента.** Щоб числа (14/20, 19/20,
  20/20) відтворювались без `ANTHROPIC_API_KEY`, тріаж рахує `eval/triage.py` -
  детермінована реалізація тих самих правил, що описані в `SKILL.md`. У
  скринкасті #2 ту саму правку робить живий `skill-improver`; тут вона
  скриптована (`make apply-fix`), щоб бал був відтворюваний у CI.
- **`outer` / `pr` таргети лише друкують runbook** - вони НЕ запускають `claude`.
- **Баг `skill_md[:1500]` навмисний.** Він показує тиху обрізку контексту:
  дописане правило стоїть за символом 1500 і зникає з того, що бачить суддя.
- **Забруднений seed навмисний.** `make seed-bad` псує held-out gold, щоб
  показати: петля оптимізує рівно те, що міряєш, і забруднена ціль дає
  «ідеальний» бал у хибне.
- **Вивід живого агента недетермінований** - живий прогін може дати трохи інше
  формулювання правила; на held-out результат той самий.
- **draft PR, не merge.** Ворота петлі - людина. Ніщо не мержиться саме.

## Публічний мірор

Джерела кіту (без `sandbox/`) дзеркаляться в
`agentic-engineering-course-public`. Sandbox генерується локально з `setup.sh`.
