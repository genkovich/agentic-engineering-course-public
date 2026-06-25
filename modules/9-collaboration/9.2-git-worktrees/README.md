# Demo: 9.2 Git Worktrees

**Module:** 9 - Collaboration
**Lectures:** 9.2 Git Worktrees: паралельна робота агентів

## Що показує

Це fixture-демо: самодостатній крихітний Python-сервіс, у якого є власна git-історія. Історія будується в runtime у теці `sandbox/` (git-ignored монорепо), тому в монорепо комітяться лише шаблони й скрипти, а не сама історія. На цьому фікстурі знімаються всі сім `🎬`-скринкастів лекції 9.2.

Worktree-специфіка: фікстур дає **детермінований стартовий стан** (git + щонайменше один commit - це передумова worktree; плюс локальний `origin` із гілками `main`/`develop`, щоб `claude --worktree` за `origin/HEAD` і `git worktree add ... origin/main` працювали наживо). Сам показ паралельних агентів веде ведучий наживо: фікстур гарантує лише, що репозиторій готовий, а не що агенти зроблять однакові кроки.

Ключове в стартовому стані:

- `.worktreeinclude` (перелічує `.env`) і рядок `.claude/worktrees/` у `.gitignore` - гігієна worktree зі Slide 5.
- локальний `origin` (bare-репо `sandbox-origin.git`) із гілками `main`/`develop` і `origin/HEAD → main` - база для `claude --worktree` і демо `git remote set-head` (Slide 8).
- `app.py` читає `PORT` і `DB_NAME` з `.env` - щоб демо **ізоляції оточення** (Slides 10-11) було наочним: два worktree → два порти → без зіткнення.
- `scripts/w.sh` - закомічений helper `w` (incident.io-стиль). Скринкаст #4 робить `source scripts/w.sh`, а не припускає `.zshrc`.
- `.claude/agents/frontend-dev.md` - субагент із `isolation: worktree` у frontmatter (Slide 13/Скринкаст #5).
- `component.py` - задача з кількома валідними рішеннями для agent-vs-agent (Скринкаст #7).

ANTHROPIC_API_KEY для бази не потрібен: стартовий стан будується звичайним git. Живі агент-сесії (`claude --worktree`, субагенти) потребують самого Claude Code.

## Pre-requisites

- Python 3.10+ (тільки stdlib, без pip-залежностей).
- git.
- Claude Code - для живих агент-сесій (скринкасти, що піднімають агентів/субагентів).
- tmux - лише для Скринкаста #6 (`tmux -V` має показати версію).

## Як запустити

```bash
cd modules/9-collaboration/9.2-git-worktrees

make sandbox     # чистий git-репо з seed-історією + .worktreeinclude/.env/helper/субагент
make serve       # підняти сервіс на PORT із sandbox/.env (довести ізоляцію порту)
make reset       # clean + sandbox: перебудувати чисто між дублями
make clean       # прибрати sandbox/ та worktree-сіблінги

# усередині пісочниці:
cd sandbox
claude --worktree feature-a          # нативний worktree (передумова git+commit виконана)
source scripts/w.sh && w feature-a   # один виклик: worktree + .env + вільний порт
```

## Мапа скринкастів

Кожен скринкаст стоїть inline під слайдом своєї фішки (не в кінці секції) і має точну послідовність команд.

| Скринкаст | Слайд | Що показує (команди) |
|---|---|---|
| #1. Дві паралельні сесії | 5 | `claude --worktree feature-a` + `claude --worktree bugfix-b`; `cat .claude/worktrees/feature-a/.env`; `git worktree list`; `diff .claude/worktrees/feature-a/app.py .claude/worktrees/bugfix-b/app.py` |
| #2. Ручне проти нативного | 7 | `git worktree add ../sandbox-manual -b manual-x origin/main` + `cp .env …` проти `claude --worktree feature-x`; `git worktree remove ../sandbox-manual` |
| #3. Enter/Exit у сесії | 9 | у сесії `EnterWorktree` → правка → `ExitWorktree` (без рестарту CLI) |
| #4. Helper `w` | 12 | `source scripts/w.sh`; `w feature-a` (вільний порт у `.env`); `python3 app.py`; `w dashboard`/`w hubspot`; `git worktree list`; `ls -d ../sandbox-*` |
| #5. Спавн субагентів + Agent View | 15 | промпт «3 субагенти frontend-dev, кожен render_card своїм підходом»; Agent View; `git worktree list` → 3 worktree |
| #6. tmux detach/attach | 16 | `claude --worktree feature-a --tmux`; `Ctrl-b d`; `tmux ls`; `claude --worktree bugfix-b --tmux`; `tmux attach -t <ім'я>` |
| #7. agent-vs-agent comparison | 18 | `claude --worktree variant-a`/`variant-b` (той самий промпт); `diff …/variant-a/component.py …/variant-b/component.py`; `git worktree remove …/variant-b --force` |

## Recording runbook

1. `make reset` перед кожним дублем, щоб стартувати з ідентичного стану.
2. `cd sandbox` і запускай `claude` уже з кореня пісочниці, щоб агент брав `.claude/` і `CLAUDE.md` саме звідти.
3. Для #1 відкрий два термінали поряд; третій - для `git worktree list`/`cat`/`diff`.
4. Для #4 спершу `source scripts/w.sh`, тоді `w <feature>` - helper сам призначить вільний порт у `.env` нового worktree.
5. Для #6 потрібен tmux; від'єднання - `Ctrl-b` (відпустити) тоді `d`; під'єднання назад - `tmux attach -t <ім'я зі списку tmux ls>`.
6. Worktree-демо інтерактивні (живі агент-сесії). Фікстур гарантує лише стартовий стан; кроки агентів і вигляд інтерфейсу (зокрема Agent View) можуть відрізнятися.

## Що НЕ демонструвати тут (жорстка межа)

Усе про **merge паралельних гілок назад і cleanup** - це лекція **9.3**, не 9.2. Тут не показуємо:

- злиття worktree-гілок назад у `main` (`git merge`/squash паралельних гілок);
- прибирання worktree після роботи (`git worktree remove`/`prune`, видалення гілок);
- хуки `WorktreeCreate`/`WorktreeRemove`;
- push-у-base-branch paper-cut і розв'язання конфліктів між паралельними гілками.

У 9.2 ми лише піднімаємо паралельну роботу й ізолюємо її. Безпечний фініш - у 9.3.

## Source

- Лекція 9.2 Git Worktrees (`Module 9 / Lecture 2`).
- Anthropic docs: нативний `claude --worktree`, база `origin/HEAD`, `.worktreeinclude`, `isolation: worktree`, `EnterWorktree`/`ExitWorktree`, `--tmux`.
- Чотири YouTube-огляди (bri, Better Stack, Developers Digest, Matt Pocock) + incident.io (helper `w`, 4-5 агентів).
