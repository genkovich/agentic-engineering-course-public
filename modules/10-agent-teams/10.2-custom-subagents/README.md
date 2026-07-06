# Demo: 10.2 Custom Subagents

**Module:** 10 - Agent Teams
**Lecture:** 10.2 Custom Subagents: авторинг власних агентів

## Що показує

Як **писати власні subagents** — файли `.claude/agents/<name>.md` — і як їхні поля frontmatter
(`tools` / `disallowedTools`, `model`, `permissionMode`, `memory`, `description`) реально керують
поведінкою: чим агент фізично може оперувати, якою моделлю думає, кого може спавнити, що памʼятає
між сесіями і коли Claude делегує йому сам.

Це **авторинг**-пара до **10.3 Evals і регресійне тестування агентів**: 10.2 вчить *написати*
конфіг агента, 10.3 — *захистити* той самий конфіг від тихих регресій golden-task сьютом. Той
самий `.claude/`, два кути: тут його створюють, там — регресять.

Історія будується в runtime у теці `sandbox/` (git-ignored монорепо), тому в монорепо комітяться
лише шаблони (`template/`), фікстури (`fixtures/`) і `setup.sh`, а не сама пісочниця.

## Дві поверхні sandbox

| Пакет | Файли | Для чого |
|---|---|---|
| `packages/queue` | `consumer.js`, `__tests__/consumer.test.js` | retry + dead-letter із тонким багом дубль-requeue на межі вичерпаних спроб. **Reasoning-таргет** для порівняння моделей (сценарій c): happy-path тести баг не ловлять, тому знайти його — нетривіально. |
| `packages/auth` | `middleware.js`, `session.js` | Bearer-middleware + стор сесій. Місце, куди `file-writer` може *записати* виправлення (сценарій a), щоб least-privilege було видно за `git diff`. |

Пакети self-contained (чистий `node`, без `npm install`) — sandbox цього демо повністю власний,
не залежить від 10.1.

## Сім сценаріїв авторингу

Кожен сценарій — окремий кут на те, як поле frontmatter змінює поведінку агента. Повні
копі-пейст промпти, Pre-state і кадр-висновок — у [`screencast-prompts.md`](./screencast-prompts.md).

- **(a) least-privilege** — `safe-researcher` (`disallowedTools: Write, Edit`) проти `file-writer`
  (той самий system prompt, але без denylist). Проси обох виправити баг: перший фізично не може
  (`git diff` порожній), другий пише. Allowlist/denylist інструментів = blast radius.
- **(b) spawn restriction (ДВА окремі механізми)** — хто кого може спавнити. Механізм 1:
  `tools: Agent(worker, researcher)` у frontmatter агента (діє, коли він сам — головний потік через
  `--agent`). Механізм 2: `permissions.deny: ["Agent(Explore)"]` у `settings.json` — глобально на
  всю сесію, незалежно від активного агента. Це **різні шари** — не одне правило.
- **(c) model comparison** — той самий `bug-hunter` з `model: haiku` проти `model: opus` на багу
  дубль-requeue в `consumer.js`. Проста summarization-задача виходить однаково; reasoning-задача
  (знайти баг, який тести пропускають) розводить моделі по точності й вартості.
- **(d) auto-delegation** — `code-explainer-vague` (загальний `description`) проти
  `code-explainer-proactive` (той самий prompt, але `description` із конвенцією «use proactively» і
  конкретним тригером). На природний запит користувача Claude делегує їм по-різному. Якість
  `description` = чи спрацює авто-делегування.
- **(e) scope priority** — однойменний агент (`name: helper`) на project-рівні
  (`.claude/agents/`) проти user-рівня (`$HOME/.claude/agents/`). Показує, який scope виграє.
  Це **ручний runbook** (торкає реальний глобальний конфіг), не Makefile-таргет. Managed
  (organization-wide) рівень — лише текстова примітка нижче, без імітації файлом.
- **(f) persistent memory** — `memory-keeper` (`memory: project`) пише спостереження в
  `.claude/agent-memory/memory-keeper/MEMORY.md` у сесії 1 і читає їх у сесії 2 (новий процес).
  Памʼять переживає завершення сесії.
- **(g) ask-Claude flow** — рекомендований спосіб створення після v2.1.198 (майстер `/agents`
  видалено): просиш Claude створити `changelog-writer`, він сам пише файл у `.claude/agents/`,
  ти ревʼюїш його як код. Ручний сценарій без Makefile-таргета; після запису прибрати файл.

## Про scope priority і managed-рівень

Точний порядок пріоритету scope (project vs user, і чи існує managed/organization-wide рівень над
ними) залежить від версії Claude Code — тому сценарій (e) робиться **живим runbook** на реальному
конфізі, а не описується як зафіксоване правило. Managed-рівень (organization-wide політики) на
практиці недоступний без enterprise-акаунту, тож у демо він лишається **текстовою приміткою** — ми
його не імітуємо фейковим файлом.

## Pre-requisites

- Node 18+ (тільки вбудований `node:test`, **без `npm install`**).
- git.
- Claude Code — для живих агент-сесій (усі сценарії).

## Як запустити

```bash
cd modules/10-agent-teams/10.2-custom-subagents

make sandbox     # чистий монореп із seed-історією, двома поверхнями і шістьма subagents
make test        # node --test у пісочниці: queue зелений (баг на непокритій межі)
make reset       # clean + sandbox: перебудувати чисто між дублями
make clean       # прибрати sandbox/

make demo-a      # ... demo-f : друкують runbook сценарію (НЕ запускають claude)

cd sandbox
ls .claude/agents            # шість авторських subagents
claude                       # стартуй сесію і копіюй промпт зі screencast-prompts.md
```

## Чесні нотатки

- Живі агент-сесії недетерміновані: фікстур гарантує лише стартовий стан, не однакові кроки агентів.
- Сценарій (e) торкає `$HOME/.claude/agents/` — після запису **прибери** доданий файл (runbook нагадує явно).
- `make demo-*` нічого не запускають — це друкований runbook для живого запису, не CI-тести.
- ANTHROPIC_API_KEY для бази не потрібен: стартовий стан будується звичайним git.

## Source

- Лекція 10.2 Custom Subagents (`Module 10 / Lecture 2`).
- Пара до `10.3-evals-regression` (той самий `.claude/`, кут регресії).
- Fixtures у стилі `10.1-subagents` (seed-історія, `Co-Authored-By`, чистий `node` без npm).
