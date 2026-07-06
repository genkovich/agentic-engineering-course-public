# Screencast-сценарії · 10.2 Custom Subagents

Сім сценаріїв лекції 10.2 (авторинг власних subagents). Усі знімаються в одній пісочниці,
зібраній `make sandbox`. Кожен — копі-пейст промпт у Claude Code, запущений із кореня `sandbox/`.

Спільна передумова:

```bash
cd ~/sources/agentic-engineering-course/modules/10-agent-teams/10.2-custom-subagents
make sandbox          # чистий монореп із seed-історією, двома поверхнями і шістьма subagents
cd sandbox
ls .claude/agents     # (опц.) показати шість авторських агентів
claude                # стартуємо сесію; нижче — промпти по одному
```

> Живі агент-сесії недетерміновані: фікстур гарантує лише стартовий стан (репо + агенти), а не
> однакові кроки агентів. Між дублями — `make reset`.

---

## 🎬 Сценарій (a) — least-privilege: `disallowedTools` = blast radius

**Агенти:** `safe-researcher` (`disallowedTools: Write, Edit`) проти `file-writer` (той самий
system prompt, без denylist). **Поверхня:** `packages/auth`.

- **Pre-state:** `cat .claude/agents/safe-researcher.md .claude/agents/file-writer.md` — показати, що
  system prompt однаковий, різниця лише в denylist інструментів. `git status` — чисто.
- **Тригеримо** (два прогони на тому самому завданні):
  - Прогін A (safe-researcher):
    > Через субагента safe-researcher: у packages/auth requireAuth повертає 401 без причини у полі reason для протухлого токена — виправ це, додай зрозумілу причину.
  - Reset: `git checkout -- .` (прибрати будь-які зміни), потім прогін B (file-writer):
    > Через субагента file-writer: те саме завдання — у packages/auth requireAuth додай зрозумілу reason для протухлого токена.
- **Дивимось:** safe-researcher фізично не має Write/Edit — він пояснює, ЯК виправити, але не пише;
  `git diff` після нього **порожній**. file-writer має Write — після нього `git diff` **непорожній**.
- **Кадр-висновок:** той самий агент-прототип, одна різниця в denylist — і протилежний blast radius.
  Allowlist/denylist інструментів вирішує, що агент фізично здатен зробити, а не що йому «дозволено».

---

## 🎬 Сценарій (b) — spawn restriction: ДВА незалежні механізми

Тут два окремі шари контролю над тим, кого агент може спавнити. Вони НЕ одне правило — знімаємо
двома підблоками.

### (b1) Механізм 1 — allowlist типів у frontmatter (`tools: Agent(...)`)

**Фікстура:** `fixtures/spawn-allowlist/`. Агент `lead-restricted` має `tools: ..., Agent(worker,
researcher)` — тобто може спавнити лише ці два типи.

- **Pre-state:** `cat fixtures/spawn-allowlist/.claude/agents/lead-restricted.md` — показати рядок
  `tools:` з `Agent(worker, researcher)`.
- **Тригеримо:** запусти цей агент як головний потік і спробуй змусити його спавнити чужий тип:
  ```bash
  cd fixtures/spawn-allowlist
  claude --agent lead-restricted
  ```
  > Спавни worker, щоб перелічив файли. Потім спавни Explore-субагента, щоб просканував репо.
- **Дивимось:** worker спавниться (він у allowlist); спроба спавнити Explore відхиляється —
  allowlist типів у frontmatter діє, поки цей агент — головний потік сесії (через `--agent`).
- **Кадр-висновок:** `Agent(worker, researcher)` у `tools:` = біла лист типів, які САМ цей агент
  може спавнити. Прив'язано до активного агента.

### (b2) Механізм 2 — глобальний deny у `settings.json` (`permissions.deny`)

**Фікстура:** `fixtures/spawn-deny/`. `settings.json` містить
`permissions.deny: ["Agent(Explore)"]` — заборона на рівні сесії, незалежно від активного агента.

- **Pre-state:** `cat fixtures/spawn-deny/.claude/settings.json` — показати рядок deny.
- **Тригеримо:** звичайна сесія (без `--agent`), проси спавнити Explore:
  ```bash
  cd fixtures/spawn-deny
  claude
  ```
  > Спавни Explore-субагента, щоб просканував структуру репо.
- **Дивимось:** спавн Explore блокується — навіть головний потік (не спеціальний агент) не може
  його підняти. Правило живе в `settings.json`, а не в frontmatter агента.
- **Кадр-висновок:** `permissions.deny: ["Agent(Explore)"]` = глобальна заборона типу на всю сесію.
  Механізм 1 прив'язаний до агента; механізм 2 — до сесії. Це два різні шари.

---

## 🎬 Сценарій (c) — model comparison: haiku проти opus на reasoning-багу

**Агент:** `bug-hunter` (той самий прототип, лише поле `model` різне). **Поверхня:**
`packages/queue/consumer.js` (баг дубль-requeue на межі `MAX_RETRIES`).

- **Pre-state:** `node --test` — queue-тести зелені (баг на непокритій межі); `cat
  packages/queue/consumer.js` — показати, що баг тонкий (requeue безумовний).
- **Тригеримо** (той самий промпт двічі, змінюємо лише `model` в агенті):
  - Спершу проста задача — обидві моделі впораються однаково:
    > Через субагента bug-hunter: підсумуй у трьох реченнях, що робить packages/queue/consumer.js.
  - Потім reasoning-задача — тут моделі розходяться:
    > Через субагента bug-hunter: у packages/queue/consumer.js є баг, який happy-path тести не ловлять. Знайди його, поясни, за яких умов повідомлення дублюється, і як виправити. Файли не змінюй.
  - Між прогонами відредагуй `model:` у `.claude/agents/bug-hunter.md`: `haiku` → `opus`.
- **Дивимось:** на summarization результат майже однаковий. На reasoning haiku частіше промахується
  повз межову умову `attempts >= MAX_RETRIES` (і в deadLetter, і назад у main), opus — стабільніше
  влучає; вартість прогону opus помітно вища (видно у `/cost`).
- **Кадр-висновок:** модель — це важіль ціна/якість на рівні агента. Просту роботу віддавай haiku,
  тонкий reasoning — сильнішій моделі; `model:` дає це вибирати поагентно.

---

## 🎬 Сценарій (d) — auto-delegation: якість `description` вирішує

**Агенти:** `code-explainer-vague` (загальний `description`) проти `code-explainer-proactive`
(ІДЕНТИЧНИЙ system prompt, але `description` із конвенцією «use proactively» + конкретний тригер).

- **Pre-state:** `cat .claude/agents/code-explainer-vague.md .claude/agents/code-explainer-proactive.md`
  — показати, що різниця ЛИШЕ в полі `description`.
- **Тригеримо** (природний запит користувача, без явного «через субагента»):
  > Поясни, як влаштована логіка повторних спроб у packages/queue.
- **Дивимось:** із загальним `description` Claude частіше робить це сам, не делегуючи; з
  proactive-описом (тригер збігається із запитом) він природно делегує саме code-explainer.
  Щоб побачити ефект чисто, тримай у сесії лише один із двох агентів за раз.
- **Кадр-висновок:** `description` — це не документація, а критерій маршрутизації. Проактивний,
  конкретний опис = агент підхоплюється сам; розмитий = лежить без діла.

---

## 🎬 Сценарій (e) — scope priority: project проти user (ручний runbook, торкає `$HOME`)

**Фікстура:** `fixtures/scope-priority/`. Project-scope агент `name: helper` уже на місці; в
runbook ти вручну кладеш ІДЕНТИЧНОГО за іменем `helper` у user-scope (`$HOME/.claude/agents/`), щоб
побачити, хто виграє. Це **не** Makefile-таргет — торкаємо реальний глобальний конфіг, тож роботи
руками й прибирання по завершенні.

- **Pre-state:**
  ```bash
  cd fixtures/scope-priority
  cat .claude/agents/helper.md          # project-scope helper (каже "PROJECT scope")
  ```
- **Крок 1 — лише project:** запусти `claude`, попроси:
  > Через субагента helper: скажи одним рядком, з якого scope ти завантажений.
  Помічаємо відповідь (project).
- **Крок 2 — додаємо user-scope дубль (руками):**
  ```bash
  mkdir -p "$HOME/.claude/agents"
  cp user-helper.md "$HOME/.claude/agents/helper.md"   # той самий name: helper, каже "USER scope"
  ```
  Знову `claude`, той самий запит — дивимось, чи змінилась відповідь (який scope переміг).
- **Дивимось:** обидва агенти мають однаковий `name: helper`; активним стає той, чий scope має
  вищий пріоритет. (Точний порядок пріоритету залежить від версії Claude Code — тому й дивимось
  наживо, а не декларуємо як зафіксоване правило.)
- **Кадр-висновок:** при однойменних агентах виграє один scope; знати цей порядок важливо, щоб
  локальний агент не перекрив глобальний (або навпаки) непомітно.
- **Managed-рівень:** над project і user буває organization-wide (managed) рівень політик. Він
  недоступний без enterprise-акаунту, тож ми його **не імітуємо** — лише згадуємо як третій,
  найвищий шар. (Текстова примітка, без файлу.)

> ⚠️ ОБОВʼЯЗКОВО прибрати після запису (див. Recording runbook нижче):
> `rm "$HOME/.claude/agents/helper.md"`

---

## 🎬 Сценарій (f) — persistent memory: пам'ять переживає сесію

**Агент:** `memory-keeper` (`memory: project`). Пише у
`.claude/agent-memory/memory-keeper/MEMORY.md`; на старті читає його першим.

- **Pre-state:** `ls .claude/agent-memory 2>/dev/null || echo "(пам'яті ще нема)"` — показати, що
  файлу памʼяті поки немає.
- **Сесія 1** (окремий процес `claude`):
  > Через субагента memory-keeper: пройдись по packages/queue і запиши у свою памʼять два факти про те, як влаштована логіка повторних спроб (щоб наступного разу не перечитувати код з нуля).
  Після завершення: `cat .claude/agent-memory/memory-keeper/MEMORY.md` — показати записані спостереження.
- **Сесія 2** (ВИЙДИ з попередньої, запусти `claude` наново — новий процес):
  > Через субагента memory-keeper: що ти вже знаєш про логіку повторних спроб у packages/queue зі своєї памʼяті?
- **Дивимось:** у сесії 2 агент посилається на факти, записані в сесії 1, не перечитуючи код —
  памʼять автозавантажилась зі старту (перші рядки MEMORY.md).
- **Кадр-висновок:** `memory: project` дає агенту стан, що переживає завершення сесії. Один агент —
  накопичувана памʼять проекту, а не чиста дошка щоразу.

---

## 🎬 Сценарій (g) — рекомендований флоу створення: попроси Claude (лекційний скринкаст #8)

Після v2.1.198 майстра `/agents` немає (команда лише друкує підказку «ask Claude to create or
update subagents, or edit the files directly») — рекомендований спосіб створення = розмова.

- **Pre-state:** `make reset`, `cd sandbox`, `ls .claude/agents/` — агента `changelog-writer` ще немає.
- **Тригеримо:** у сесії `claude` попросити:
  > Створи субагента changelog-writer: read-only, збирає останні коміти через git log і пише чернетку changelog. Інструменти: Read, Grep, Glob, Bash. Модель haiku.
- **Дивимось:** Claude сам пише файл — `cat .claude/agents/changelog-writer.md` показує згенерований
  frontmatter (name/description/tools/model) і system prompt. Далі нова сесія `claude` —
  `changelog-writer` з'являється у typeahead після `@`.
- **⚠️ Recording-time caveat:** живцем перевірити, чи видно щойно створеного агента вже в поточній
  сесії, чи лише після рестарту (субагенти завантажуються на старті сесії) — і зафіксувати в кадрі
  те, що реально відбулося.
- **Кадр-висновок:** рекомендований флоу після v2.1.198 — агент створюється розмовою, а живе
  файлом; цей файл ревʼюїш як код.
- **Cleanup:** `git checkout -- . && rm -f .claude/agents/changelog-writer.md` (або `make reset`).

---

## Мапа сценаріїв

| Сценарій | Поле frontmatter у центрі | Що доводить |
|---|---|---|
| (a) least-privilege | `disallowedTools` (vs `tools`) | denylist інструментів = blast radius |
| (b) spawn restriction | `tools: Agent(...)` + `settings.json permissions.deny` | два різні шари контролю спавну |
| (c) model comparison | `model` | важіль ціна/якість поагентно |
| (d) auto-delegation | `description` | критерій маршрутизації, не документація |
| (e) scope priority | розташування файлу (project/user/managed) | хто виграє при однойменних агентах |
| (f) persistent memory | `memory: project` | стан переживає завершення сесії |
| (g) ask-Claude flow | увесь файл цілком (генерується розмовою) | рекомендований спосіб створення після v2.1.198 |

## Бонус для лекції — JSON-каталог у дії (`--agents`)

Sandbox цього репо (пакети `template/packages/`) слугує також фоном для лекційного скринкасту #7
«JSON-каталог у дії: `--agents` CLI» — живий приклад, де subagent створюється на льоту через
`claude --agents '{...}'` без файлу на диску. Окремої теки-сценарію під це НЕ треба: беруть той
самий `sandbox/` і той самий queue-баг, лише агент задається інлайн-JSON у командному рядку замість
`.claude/agents/*.md`. (Використовується у лекції 10.2, секція про CLI-каталог агентів.)

## Recording runbook

1. `make reset` перед кожним дублем — ідентичний стартовий стан.
2. `cd sandbox` (або у відповідну `fixtures/<...>`), тоді `claude` — щоб агент брав `.claude/` і
   `CLAUDE.md` із кореня.
3. Сценарій (c) знімай двома прогонами з відредагованим `model:` між ними; фіксуй `/cost` для обох.
4. Сценарій (d) тримай активним лише один із двох `code-explainer-*` за раз, щоб ефект `description`
   було видно чисто.
5. **Сценарій (e) торкає реальний `$HOME/.claude/agents/`.** ПІСЛЯ запису ОБОВʼЯЗКОВО прибери
   доданий файл:
   ```bash
   rm "$HOME/.claude/agents/helper.md"
   ```
   Перевір, що прибрав: `ls "$HOME/.claude/agents/" | grep helper || echo "(clean)"`.
6. Agent View і точний вигляд інтерфейсу залежать від версії Claude Code; фікстур гарантує лише
   стартовий стан, не однакові кроки агентів.
7. Сценарій (g): агент, створений у поточній сесії файлом на диску, може вимагати нової сесії, щоб
   з'явитись у typeahead (`@`) — субагенти завантажуються на старті сесії. Перевір живцем і зніми
   фактичну поведінку; після запису прибери `changelog-writer.md`.
