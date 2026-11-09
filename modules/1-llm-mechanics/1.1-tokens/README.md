# Demo: Tokens

**Module:** 1 - LLM Mechanics
**Lectures:** «Токени»

## Що показує

Три скрипти до трьох скринкастів лекції. Кожен можна запустити сам і підставити свій текст.

1. `tokenizers_side_by_side.py` ріже один рядок трьома відкритими токенізаторами: cl100k (GPT-4), o200k (GPT-4o, GPT-5) і Gemma 3. Кожен шматок має свій колір, поруч кількість токенів. Ключ не потрібен, усе рахується локально.
2. `claude_generations.py` проганяє той самий абзац англійською і українською через `count_tokens` на двох поколіннях токенізатора Claude: `claude-sonnet-4-6` (старий) і `claude-sonnet-5-5` (новий). Видно приріст між поколіннями і множник UA/EN окремо на кожній моделі.
3. `claude_pairs.py` показує на Claude три пари з лекції: лог-рядок з trace id і UUID проти того самого одним реченням, `json.dumps` з українськими іменами з `ensure_ascii` і без, звичайне речення проти ALL CAPS.

Якщо твій множник UA/EN не збігається з тим, що ти бачив деінде, глянь, на якій моделі рахували. Токени не переносяться між токенізаторами, навіть між двома поколіннями Claude.

## Pre-requisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/): він сам завантажить потрібний Python 3.13 і поставить пакети, системний Python не потрібен. Можна і без uv, тоді Python 3.10+ і pip (див. нижче)
- Інтернет на перший запуск: tiktoken і Hugging Face качають словники, далі вони беруться з кешу
- Для скриптів 2 і 3: `ANTHROPIC_API_KEY` з [platform.claude.com](https://platform.claude.com) у `.env`

`count_tokens` безкоштовний, але працює лише з API-акаунтом. Якщо API відповідає `credit balance is too low`, поповни баланс на platform.claude.com. Підписка Pro чи Max на claude.ai сюди не рахується, це окремий рахунок.

## Як запустити

Встанови uv один раз:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh                      # macOS, Linux
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"   # Windows
```

Після цього перезапусти термінал. Далі команди однакові на всіх системах:

```bash
cp .env.example .env                 # Windows: Copy-Item .env.example .env; встав ANTHROPIC_API_KEY
uv run check_setup.py                # перевірка: Python, пакети, ключ, API
uv run claude_generations.py         # скрипт 2
uv run claude_generations.py --file my_prompt.md
uv run claude_pairs.py               # скрипт 3
uv run tokenizers_side_by_side.py    # скрипт 1, ключ не потрібен
uv run tokenizers_side_by_side.py "твій текст"
```

Перший `uv run` створює `.venv` на Python 3.13 (версія записана в `.python-version`) і ставить пакети з `pyproject.toml`. Скрипт 1 має свої залежності прямо в шапці файлу, uv поставить їх окремо при першому запуску.

Свої параметри:

```bash
uv run claude_generations.py --model claude-haiku-4-5 --model claude-opus-5-5
uv run claude_pairs.py --model claude-sonnet-5-5
```

Якщо щось не працює, запусти `uv run check_setup.py` і скинь його вивід у чат курсу.

### Без uv

Для домашки (скрипти 2 і 3) потрібні тільки два пакети з `requirements.txt`. Пакети для скрипта 1 лежать окремо в `requirements-tokenizers.txt`: на нових чи free-threaded збірках Python (наприклад, 3.15t) для них може не бути готових збірок, і pip почне компілювати їх з Rust.

```bash
make setup                 # .venv і обидва requirements
make check
make run-generations
make run-pairs
make run-tokenizers TEXT='"твій текст"'
```

Windows (PowerShell), де `make` немає:

```powershell
py -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python check_setup.py
.venv\Scripts\python claude_generations.py
```

Якщо `py` не знаходиться, пиши `python`. Більше про курс на Windows: [WINDOWS.md](../../../WINDOWS.md).

## Очікуваний output

`uv run tokenizers_side_by_side.py` на слові «Токенізація»:

```
  cl100k (GPT-4)    9 ток.   Т|ок|ен|і|з|а|ц|і|я
  o200k (GPT-4o)    5 ток.   Т|ок|ен|іза|ція
  Gemma 3           5 ток.   То|кен|і|за|ція
```

У терміналі межі показані кольором, у пайпі чи з `NO_COLOR=1` через `|`.

`claude_generations.py` дає таблицю: модель, дата заміру, покоління токенізатора, `input_tokens` для EN і UA, множник UA/EN. Під таблицею приріст нової моделі проти першої у відсотках.

`claude_pairs.py` дає три блоки, у кожному `input_tokens` обох варіантів і різницю в разах.

У `input_tokens` входить кілька службових токенів обгортки повідомлення, тому на дуже коротких рядках різниця менша, ніж на довгих.

## Чому не Workbench

Раніше токени рахували у Workbench на console.anthropic.com. Його замінив Playground на platform.claude.com, і окремої кнопки для `count_tokens` там нема. Скрипт дає те саме число і його можна повторити на будь-якій моделі.

## Source

- Лекція «Токени» курсу Agentic Engineering
- Token counting: https://platform.claude.com/docs/en/build-with-claude/token-counting
- API reference: https://platform.claude.com/docs/en/api/messages/count_tokens
