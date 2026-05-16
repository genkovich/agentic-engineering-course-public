# Module 4 — Майстерність Промптингу

Як писати промпти і керувати контекстом так, щоб Claude Code давав результат, який не треба переробляти. Цей модуль збирає прийоми (specificity, few-shot, verification) і артефакти контролю контексту (`.claude/`, `CLAUDE.md`, rules, Plan/Think режими) у єдину дисципліну роботи з агентом — від короткого промпта до багатоденного legacy-рефакторингу.

Артефакти модуля впорядковані за LMS-нумерацією: `demos/4-prompting-mastery/4.N-<topic>/`.

## Лекції модуля

- 4.1 Як писати промпти — specificity, формат, few-shot, verification
- 4.2 Як давати контекст — що приклеювати у промпт, чого ні
- 4.3 `.claude/` папка як база — структура per-project конфігурації
- 4.4 CLAUDE.md — конвенції проєкту, які Claude читає сам
- 4.5 Claude Code Rules — path-rules і умовні обмеження
- 4.6 Режими — Plan і Think — коли який mode рятує
- 4.7 Контекст у довгій сесії — як не втратити сигнал на 100k токенів
- 4.8 Bounded Contexts — як архітектурні межі допомагають агенту
- 4.9 Legacy Refactoring без меж — протокол на real-world спагеті
- 4.10 Scaffold як кульмінація — як зібрати все з модуля в один прохід

## Артефакти модуля

| Demo | Що показує | Лекції |
|---|---|---|
| [4.1-prompts](../../demos/4-prompting-mastery/4.1-prompts) | Текстові приклади промптів для скринкастів лекції: vague vs explicit, few-shot з 1/3 прикладами, race-condition, verification. Не runnable — це reference для повторення вживу | 4.1 |
| [4.8-bc](../../demos/4-prompting-mastery/4.8-bc) | E-commerce домен з 5 BC, реалізований у Go × TS × Python × 3 стадіях зрілості (flat → feature-first → hexagonal). 9 робочих проєктів, per-stage Makefile, arch-test у Stage 3 | 4.8 |
| [4.9-legacy-refactor](../../demos/4-prompting-mastery/4.9-legacy-refactor) | FastAPI «спагетті» users-модуль + протокол з 7 skills (`legacy-spike` → `legacy-extract` → `legacy-critic` → `legacy-plan` → `legacy-tests` → `legacy-cutover`) для рефакторингу у чистий `internal/account/` через 1-2 дні роботи з агентом | 4.9 |

## Pre-requisites

- Claude Code локально (див. Module 3)
- Python 3.12 (для 4.9 — FastAPI demo)
- Go 1.26 / Node 22 / Python 3.12 (для 4.8 — обираєш свою мову)

## Як використовувати

Кожен runnable demo має власний `README.md` із інструкціями. Скринкасти лекцій спираються на ці артефакти — копіюй промпти з `4.1-prompts/PROMPTS.md`, запускай 4.8 і 4.9 локально, щоб повторити дії з лекції на власній машині.

```bash
# 4.8 — Go stage-1 baseline
cd demos/4-prompting-mastery/4.8-bc/go/stage-1-flat
make run

# 4.9 — Legacy refactor demo
cd demos/4-prompting-mastery/4.9-legacy-refactor
python3 -m venv .venv && source .venv/bin/activate && pip install -e .
pytest -q
```

## Що робити після цього модуля

Module 4 закладає робочу дисципліну роботи з промптом і контекстом. У Module 5 ці навички розширюються через custom commands, skills, hooks і plugins — поверх вже сформованої звички тримати чистий контекст і явні rules.
