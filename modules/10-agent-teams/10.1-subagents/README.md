# Demo: 10.1 Subagents

**Module:** 10 - Agent Teams
**Lecture:** 10.1 Subagents: делегування та ізоляція контексту

## Що показує

Самодостатній крихітний **монореп** із чотирма незалежними пошуковими поверхнями. Історія
будується в runtime у теці `sandbox/` (git-ignored монорепо), тому в монорепо комітяться лише
шаблони (`template/`) і `setup.sh`, а не сама історія. На цьому фікстурі знімаються всі чотири
`🎬`-скринкасти лекції 10.1.

Сенс фікстура: дати делегуванню **реальні, роздільні цілі**. Fan-out трьох Explore має три файли
автентифікації; orchestrator-worker має три різні поверхні; voting має код із дрібним недоліком;
контракт A/B має достатньо матеріалу, щоб «розкажи все» розпухло, а контракт - ні.

## Чотири поверхні

| Пакет | Файли | Що в ньому (і для якого скринкаста) |
|---|---|---|
| `packages/billing` | `invoice.js`, `discount.js`, `__tests__/invoice.test.js` | інвойс із ризиком округлення + знижка без валідації `percent` (Скринкасти #2, #3, #4) |
| `packages/queue` | `consumer.js`, `__tests__/consumer.test.js` | RabbitMQ-style retry + dead-letter з тонким багом дубль-requeue на межі спроб (Скринкаст #3) |
| `packages/auth` | `middleware.js`, `session.js`, `__tests__/auth.test.js` | Bearer-middleware + стор сесій із TTL - три файли для fan-out (Скринкаст #1) |
| `packages/reports` | `summary.js`, `__tests__/summary.flaky.test.js` | дайджест + навмисно flaky-тест (недетермінований вхід) - поверхня «знайди flaky» (Скринкаст #3) |

`.claude/agents/ro-reviewer.md` - read-only рев'юер (`tools: Read, Grep, Glob, Bash`) для voting-скринкаста #4.

## Pre-requisites

- Node 18+ (тільки вбудовані `node:test` і stdlib, **без `npm install`**).
- git.
- Claude Code - для живих агент-сесій (усі чотири скринкасти).

## Як запустити

```bash
cd modules/10-agent-teams/10.1-subagents

make sandbox     # чистий монореп-репо з seed-історією і чотирма поверхнями
make test        # node --test у пісочниці: billing/queue/auth зелені, reports flaky
make reset       # clean + sandbox: перебудувати чисто між дублями
make clean       # прибрати sandbox/

cd sandbox
node --test      # green-пакети проходять; reports flaky падає через раз
claude           # стартуй сесію і копіюй промпт зі screencast-prompts.md
```

## Скринкасти

Storyboard усіх чотирьох (копі-пейст промпти, Pre-state, що дивитись, кадр-висновок) - у
[`screencast-prompts.md`](./screencast-prompts.md). Коротка мапа:

| Скринкаст | Патерн | Поверхня |
|---|---|---|
| #1 fan-out 3 Explore | parallelization / sectioning | `packages/auth` |
| #2 контракт результату A/B | (контракт) | `packages/billing` |
| #3 orchestrator-worker | orchestrator-workers | billing / queue / reports |
| #4 voting 3 рев'юери | parallelization / voting | `packages/billing` |

## Чесні нотатки

- Живі агент-сесії недетерміновані: фікстур гарантує лише стартовий стан, не однакові кроки агентів.
- `node --test` навмисно «мигає» на `packages/reports` - це і є демо-поверхня flaky-тестів. Решта
  пакетів стабільно зелені.
- ANTHROPIC_API_KEY для бази не потрібен: стартовий стан будується звичайним git. Самі скринкасти
  ведуться інтерактивно в Claude Code.

## Source

- Лекція 10.1 Subagents (`Module 10 / Lecture 1`).
- Fixtures адаптовано зі стилю `9.2-git-worktrees` (seed-історія, `Co-Authored-By`) і
  `10.2-custom-subagents` (`ro-reviewer`, патерн чистого `node` без npm).
