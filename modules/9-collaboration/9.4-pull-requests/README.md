# Demo: 9.4 Pull Requests

**Module:** 9 - Collaboration
**Lecture:** 9.4 Pull Requests: створення та автоматизація

## Що показує

Це fixture-демо: самодостатній крихітний Python-«api» (тема — видача й рефреш
access-токена) із власною git-історією. На цьому фікстурі знімаються всі три
`🎬`-скринкасти лекції 9.4.

На відміну від 9.1-9.3, тут не можна обійтися повністю локальною фікстурою:
`gh pr create` фундаментально звертається до GitHub API. Тому фікстура 9.4 =
**локально детермінований seed** (історія, гілки, код, конфіги) **+ реальний
`origin` на GitHub** + cleanup-скрипт для повторюваності між дублями.

Демо тримає три стартові стани — по одному на скринкаст, кожен `make` чисто
перебудовує `sandbox/`:

- `make sandbox` — базовий repo + запушена гілка `feat/token-refresh` + demo
  issue. `CLAUDE.md` **без** секції PR, **без** PR-template, дефолтні
  permissions. Стан для **SC#1** (diff → summarize → create → enhance →
  session-link).
- `make rules` — `sandbox` + `.github/pull_request_template.md` + секція
  `## Pull requests` у `CLAUDE.md` + skill `fix-issue` + **друга** гілка
  `feat/rate-limit` для контрастного PR. Стан для **SC#2**.
- `make perms` — `sandbox` + `.claude/settings.json` (`allow` на
  `Bash(gh pr create *)`, `ask` на `Bash(gh pr merge *)`). Стан для **SC#3**.

Прогресивні (а не «усе-в-одному») стани зберігають педагогіку чистою: у SC#1
агент вільно формує опис із діфу (правил ще нема), у SC#2 контраст «агент сам
узяв правила» лишається відчутним.

ANTHROPIC_API_KEY не потрібен: демо керується інтерактивно через Claude Code.

## Pre-requisites

- Python 3.10+ (тільки stdlib, без pip-залежностей).
- git.
- [`gh`](https://cli.github.com/) — GitHub CLI, залогінений (`gh auth login`).
  Потрібен для пушу гілок, demo-issue і самих PR. Без нього працює лише
  локальний seed (`GH_DEMO_REPO= make sandbox`).

## Одноразовий GitHub-bootstrap (робить лектор один раз)

1. `gh auth login` — scope `repo` (HTTPS або SSH, як зручно).
2. Мати приватне/публічне репо `genkovich/course-project`. Своє? Передай через
   змінну: `GH_DEMO_REPO=ваш-org/ваш-repo make sandbox`.
3. (Опційно, для SC#3 step 3) Увімкнути branch protection на `main`
   (Settings → Branches → require a pull request before merging). У SC#3 це
   згадується лише голосом — але мати ввімкненим бажано для чесності демо.
   ⚠️ Вмикай protection **після** першого `make sandbox`: захищена `main` блокує
   force-push seed-історії. Між дублями `setup.sh` оновлює лише `feat/*`-гілки,
   тож protection на `main` далі не заважає.

## Як запустити

```bash
cd modules/9-collaboration/9.4-pull-requests

make sandbox       # SC#1: base + feat/token-refresh + issue (no PR rules)
make rules         # SC#2: + PR template + CLAUDE.md PR section + feat/rate-limit
make perms         # SC#3: + .claude/settings.json (allow create / ask merge)

make reset         # clean + sandbox: перебудувати чисто між дублями
make clean         # прибрати локальний sandbox/
make cleanup-prs   # закрити demo-PR + видалити віддалені demo-гілки на GitHub
make test          # тести токена в sandbox (зелені на кожній гілці)

GH_DEMO_REPO= make sandbox   # network-free: лише локальний seed, без пушу
```

## Мапа скринкастів

| Скринкаст | Секція лекції | Режим | Що показує |
|---|---|---|---|
| #1 Claude відкриває PR з авто-описом | Секція 2 | `make sandbox` | summarize (`git diff main..feat/token-refresh`) → create (`gh pr create --draft` з `Closes #N`) → enhance (агент доповнює тіло) → session-link (`claude --from-pr <N>`) |
| #2 template + `CLAUDE.md` → консистентний PR | Секція 3 | `make rules` | агент сам бере правила: заголовок у форматі коміта, розділи шаблону, `Closes #`, `--draft`; другий PR із `feat/rate-limit` для контрасту |
| #3 дозволи: create проходить, merge впирається в ask | Секція 5 | `make perms` | `gh pr create` дозволений (`allow`), `gh pr merge` зупиняється на `ask`; branch protection згадується голосом як другий шар |

## Recording runbook

1. `make <режим>` під відповідний скринкаст (див. мапу). Кожен режим чисто
   перебудовує `sandbox/` і оновлює віддалені demo-гілки.
2. `cd sandbox` і запускай `claude` уже з кореня пісочниці, щоб агент брав
   `CLAUDE.md` (і `.claude/` у режимах rules/perms) саме звідти.
3. **Номер issue.** GitHub нумерує issue послідовно — гарантувати саме `#214`
   не можна. `setup.sh` друкує реальний номер створеного/наявного demo-issue:
   підставляй його в кадрі. У слайдах і голосі `#214` лишається як приклад.
   (Альтернатива: тримати один довгоживучий demo-issue й переюзати його номер.)
4. **Між дублями** — `make reset` (локально) і за потреби `make cleanup-prs`
   (закрити demo-PR + почистити віддалені demo-гілки). `setup.sh` і сам кличе
   cleanup перед пушем, тож повторний `make sandbox`/`make rules` ідемпотентний.
5. SC#3: `.claude/settings.json` уже лежить у `sandbox/` після `make perms` —
   доналаштовувати нічого не треба. Merge у кадрі впреться в `ask`; реально
   зливати PR не обов'язково (а краще не зливати — лишай чернеткою).

## fix-issue skill (референс, не записується)

Режим `rules` кладе у `sandbox/.claude/skills/fix-issue/SKILL.md` skill
`fix-issue` — матеріалізований «PR-author як skill» зі Slide 13 (потік
issue → fix → PR одним викликом). Жоден скринкаст його не записує; він тут як
артефакт, на який лекція може послатися (узгоджено з правилом «лекційні
протоколи посилаються на skills, а не на inline-промпти»).

## Source

- Лекція 9.4 Pull Requests (`Module 9 / Lecture 4`).
- Anthropic best practices / common-workflows (`gh` рекомендований; summarize →
  create → enhance; `Closes #N`; headless `claude -p`; `--from-pr`).
- GitHub CLI manual (`gh pr create`), GitLab `glab` manual (паритет).
