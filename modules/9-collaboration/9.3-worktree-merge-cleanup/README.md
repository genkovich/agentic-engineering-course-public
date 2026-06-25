# Demo: 9.3 Worktree merge + cleanup

**Module:** 9 - Collaboration
**Lectures:** 9.3 Worktree merging та cleanup

## Що показує

Це fixture-демо: той самий крихітний env-driven Python-сервіс, що й у 9.2, але стартовий стан зібраний під безпечний фініш паралельної роботи. Історія будується в runtime у теці `sandbox/` (git-ignored монорепо) разом із worktree-сіблінгами, тому в монорепо комітяться лише шаблони й скрипт, а не сама історія. На цьому фікстурі знімаються обидва `🎬`-скринкасти лекції 9.3.

Фікстур дає **детермінований стартовий стан** під merge і cleanup, а самі кроки веде ведучий наживо. Ключове в стартовому стані:

- дві worktree-гілки `worktree-feature-a` і `worktree-bugfix-b`, кожна з власним комітом; **обидві правлять той самий рядок** `GREETING` в `app.py`. Тому коли ви вливаєте другу гілку назад, виходить справжній конфлікт саме на цьому рядку (Скринкаст #1).
- забутий worktree `worktree-old-experiment` (каталог `../sandbox-old-experiment`) - матеріал для cleanup-демо `list`/`remove`/`prune` (Скринкаст #2).
- локальний `origin` (bare-репо `.sandbox-origin.git`) з гілкою `main` і `origin/HEAD → main` - щоб merge і push працювали без мережі. Серверного захисту тут навмисно немає: прямий offline-merge лишається когерентним, а branch protection описуємо як серверний шар (Slide 5).
- `.claude/hooks/block-main-push.sh` - safety-hook на push зі Slide 5: ловить помилковий `git push ... main` і повертає `exit 2`. `.claude/settings.json` чіпляє його як `PreToolUse` matcher `Bash` і додатково забороняє force-push.
- `.worktreeinclude` (перелічує `.env`) і рядок `.claude/worktrees/` у `.gitignore` - гігієна worktree, перенесена з 9.2.
- `CLAUDE.md` - етикет завершення: вливай по одній з review кожного diff, `git pull` перед push, пуш у названу гілку (ніколи в `main`), `remove`+`prune` як звичка, гілка після ручного `remove` лишається (зітри `git branch -d`).

ANTHROPIC_API_KEY для бази не потрібен: стартовий стан будується звичайним git. Живі агент-сесії (вихід із `--worktree`, авто-removal) потребують самого Claude Code.

## Pre-requisites

- Python 3.10+ (тільки stdlib, без pip-залежностей).
- git.
- `jq` - safety-hook читає payload Claude Code через `jq`.
- Claude Code - для живих агент-сесій (авто-removal на виході у Скринкасті #2).

## Як запустити

```bash
cd modules/9-collaboration/9.3-worktree-merge-cleanup

make sandbox     # стартовий стан: seed-історія + дві конфліктні гілки + забутий worktree
make serve       # підняти сервіс на PORT із sandbox/.env
make reset       # clean + sandbox: перебудувати чисто між дублями
make clean       # прибрати sandbox/, worktree-сіблінги та bare origin

# усередині пісочниці:
cd sandbox
git worktree list                       # main + feature-a + bugfix-b + old-experiment
git diff main..worktree-feature-a       # review гілки перед merge
```

## Мапа скринкастів

Кожен скринкаст стоїть inline під слайдом своєї фішки і має точну послідовність команд.

| Скринкаст | Слайд | Що показує (команди) |
|---|---|---|
| #1. Влити дві паралельні гілки | 5 | `git diff main..worktree-feature-a` (review); `git merge worktree-feature-a` (чисто); на `worktree-bugfix-b` `git merge main` → CONFLICT на `app.py` → розв'язати наживо; `git push origin worktree-bugfix-b` (названа гілка); safety-hook ловить помилковий `git push origin main` і дає правильну команду |
| #2. Cleanup | 7 | вихід із `--worktree` сесії без змін → авто-removal; вихід зі змінами → запит keep/remove; `git worktree list` → забутий worktree; `git worktree remove ../sandbox-old-experiment`; після `rm -rf` іншого → `git worktree prune` |

## Recording runbook

1. `make reset` перед кожним дублем, щоб стартувати з ідентичного стану.
2. `cd sandbox` і запускай команди з кореня пісочниці, щоб git і `.claude/` бралися саме звідти.
3. Для Скринкаста #1, Step 1: покажи `git diff main..worktree-feature-a`, тоді влий першу гілку у `main`: `git merge worktree-feature-a` (тут fast-forward, бо `main` ще не чіпали).
4. Для Скринкаста #1, Step 2: перейди у сусідній worktree (`cd ../sandbox-bugfix-b`) і зведи з `main`: `git merge main`. Це дасть CONFLICT на рядку `GREETING` в `app.py`. Розв'яжи його наживо (залиш потрібний варіант, прибери маркери `<<<<<<<`/`=======`/`>>>>>>>`), тоді `git add app.py && git commit`. Наголоси голосом: конфлікт - нормальний наслідок паралельності.
   - Чесна нота про offline: у демо ми не пушимо напряму в `main` і немає другого автора, тому роль `git pull` на гілці виконує локальний `git merge main` (підтягнути щойно влите перше). Механіка зведення й конфлікту та сама.
5. Для Скринкаста #1, Step 3: пуш у названу гілку: `git push origin worktree-bugfix-b`. Тоді покажи помилку: `git push origin main` - safety-hook поверне `exit 2` і підкаже named-гілку. Перевірити хук уручну можна так:
   ```bash
   echo '{"tool_input":{"command":"git push origin main"}}' | bash template/.claude/hooks/block-main-push.sh; echo $?   # 2 + блок
   echo '{"tool_input":{"command":"git push origin worktree-bugfix-b"}}' | bash template/.claude/hooks/block-main-push.sh; echo $?   # 0
   ```
6. Для Скринкаста #2: авто-removal на виході з `--worktree` сесії - це жива поведінка Claude Code (без змін → авто; зі змінами → keep/remove). Поза сесією: `git worktree list` покаже `worktree-old-experiment`; прибери його через `git worktree remove ../sandbox-old-experiment`. Щоб показати `prune`, зітри інший worktree грубо (`rm -rf ../sandbox-feature-a`), тоді `git worktree prune` витре мертвий запис.
7. Merge/cleanup-демо частково інтерактивні (авто-removal веде жива сесія). Фікстур гарантує лише стартовий стан; вигляд інтерфейсу й кроки агента можуть відрізнятися.

## Що НЕ демонструвати тут (жорстка межа)

- Хуки `WorktreeCreate`/`WorktreeRemove` тут навмисно не написані. Лекція (Slide 8) прямо радить не писати їх наперед: вони потрібні лише для не-git VCS (SVN/Perforce/Mercurial) і складного провіженінгу під кожен worktree. У типовому git-проєкті досить нативного керування. Це talking-point, а не код фікстура.
- Концепт worktree, підняття багатьох сесій, ізоляція оточення, субагенти - це 9.2 (демо `9.2-git-worktrees`). Тут лише безпечний фініш: merge назад і cleanup.
- Базовий git workflow (trunk-based, охайні коміти, звірка diff, відкат) - це 9.1 (демо `9.1-git-workflow`).
- Загальна механіка pull request і делегування review самому Claude - це 9.4/9.5. Тут review кожної гілки лишається ручним кроком завершення.

## Source

- Лекція 9.3 Worktree merging та cleanup (`Module 9 / Lecture 3`).
- Anthropic docs: cleanup-поведінка no-change/keep/remove, manual worktree management (`remove`/`prune`/`list`), push restricted to current branch, хуки `WorktreeCreate`/`WorktreeRemove`.
- Matt Pocock (paper-cut push зі worktree, safety-hook, remove без push = втрата), bri (merge-конфлікти, порядок commit→PR→merge), Better Stack (keep/resume, хуки).
