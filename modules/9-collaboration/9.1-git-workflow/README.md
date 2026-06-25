# Demo: 9.1 Git workflow

**Module:** 9 - Collaboration
**Lectures:** 9.1 Git workflow з Claude (trunk-based і охайні коміти)

## Що показує

Це fixture-демо: самодостатній крихітний Python-«api», у якого є власна git-історія. Історія будується в runtime у теці `sandbox/` (git-ignored монорепо), тому в монорепо комітяться лише шаблони й скрипти, а не сама історія. На цьому фікстурі знімаються всі п'ять `🎬`-скринкастів лекції 9.1.

Демо тримає два стани, бо різні скринкасти хочуть різного робочого дерева:

- `make sandbox` дає чисту seed-історію (~8 комітів у форматі Conventional Commits із трейлером `Co-Authored-By`, tag `good-baseline` на завідомо робочому коміті, один планований баг усередині). На цьому стані знімаються `git bisect`, два рівні відкату й секрет-guard.
- `make arm` накидає поверх sandbox змішані незакомічені правки. На цьому стані знімаються коміт, чанкування й звірка діфу.

ANTHROPIC_API_KEY не потрібен: демо керується інтерактивно через Claude Code, не через API-скрипт. Файл `.env.example` лежить тут лише задля скринкаста секрет-guard (демо D).

## Pre-requisites

- Python 3.10+ (тільки stdlib, без pip-залежностей).
- git.
- jq - потрібен PreToolUse-хуку `block-env.sh` (демо D).

## Як запустити

```bash
cd modules/9-collaboration/9.1-git-workflow

make sandbox     # чиста seed-історія + tag good-baseline
make arm         # накинути змішані незакомічені правки поверх sandbox
make test        # тест пагінації (червоний на HEAD, зелений на good-baseline)
make reset       # clean + sandbox: перебудувати чисто між дублями
make clean       # прибрати sandbox/
```

## Мапа скринкастів

| Скринкаст | Секція лекції | Режим | Що показує |
|---|---|---|---|
| `git bisect` | Секція 2 | `make sandbox` | bisect ділить історію навпіл і виходить на коміт `refactor(api): simplify pagination cursor handling`, що зробив тест червоним |
| A. Коміт + чанкування | Секція 2 | `make sandbox && make arm` | Claude сам пише Conventional-меседж із діфу, додає `Co-Authored-By`, розкладає змішане дерево на логічні коміти |
| B. Звірка діфу | Секція 3 | `make sandbox && make arm` | `git diff`, `/diff`, `git add -p src/api/auth.py` (два hunk-и: `y` на одному, `n` на іншому) |
| C. Два рівні відкату | Секція 4 | `make sandbox` | `/rewind` (сесійний), `git revert` (постійний), `git reset --hard` упирається в deny-правило |
| D. Секрет-guard | Секція 4 | `make sandbox` | PreToolUse-хук `block-env.sh` блокує `git add -f .env` (exit 2) |

## Recording runbook

1. `make reset` перед кожним дублем, щоб стартувати з ідентичного стану.
2. Для A і B одразу після `make sandbox` зроби `make arm`.
3. `cd sandbox` і запускай `claude` уже з кореня пісочниці, щоб агент брав `.claude/` і `CLAUDE.md` саме звідти.
4. C і D працюють на чистому `make sandbox`: deny-правило й хук уже лежать у `template/.claude/settings.json`, нічого доналаштовувати не треба.
5. Нюанс D: `.env` git-ignored, тому щоб блок хука було видно в кадрі, інсценуй аварію через `git add -f .env`.

## Source

- Лекція 9.1 Git workflow з Claude (`Module 9 / Lecture 1`).
- Anthropic best practices, permissions, commands, checkpointing, hooks.
- Conventional Commits; Driessen / GitHub Flow / trunk-based.
