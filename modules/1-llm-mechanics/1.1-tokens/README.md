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

- Python 3.10+
- Інтернет на перший запуск: tiktoken і Hugging Face качають словники, далі вони беруться з кешу
- Для скриптів 2 і 3: `ANTHROPIC_API_KEY` з [platform.claude.com](https://platform.claude.com) у `.env`

`count_tokens` безкоштовний, але працює лише з API-акаунтом. Якщо API відповідає `credit balance is too low`, поповни баланс на platform.claude.com. Підписка Pro чи Max на claude.ai сюди не рахується, це окремий рахунок.

## Як запустити

```bash
make setup                 # .venv і залежності
make run-tokenizers        # скрипт 1, ключ не потрібен
make run-tokenizers TEXT='"твій текст"'

cp .env.example .env       # встав ANTHROPIC_API_KEY
make run-generations       # скрипт 2
make run-pairs             # скрипт 3
```

Свої параметри:

```bash
.venv/bin/python claude_generations.py --model claude-haiku-4-5 --model claude-opus-5-5
.venv/bin/python claude_generations.py --file my_prompt.md
.venv/bin/python claude_pairs.py --model claude-sonnet-5-5
```

## Очікуваний output

`make run-tokenizers` на слові «Токенізація»:

```
  cl100k (GPT-4)    9 ток.   Т|ок|ен|і|з|а|ц|і|я
  o200k (GPT-4o)    5 ток.   Т|ок|ен|іза|ція
  Gemma 3           5 ток.   То|кен|і|за|ція
```

У терміналі межі показані кольором, у пайпі чи з `NO_COLOR=1` через `|`.

`make run-generations` дає таблицю: модель, дата заміру, покоління токенізатора, `input_tokens` для EN і UA, множник UA/EN. Під таблицею приріст нової моделі проти першої у відсотках.

`make run-pairs` дає три блоки, у кожному `input_tokens` обох варіантів і різницю в разах.

У `input_tokens` входить кілька службових токенів обгортки повідомлення, тому на дуже коротких рядках різниця менша, ніж на довгих.

## Чому не Workbench

Раніше токени рахували у Workbench на console.anthropic.com. Його замінив Playground на platform.claude.com, і окремої кнопки для `count_tokens` там нема. Скрипт дає те саме число і його можна повторити на будь-якій моделі.

## Source

- Лекція «Токени» курсу Agentic Engineering
- Token counting: https://platform.claude.com/docs/en/build-with-claude/token-counting
- API reference: https://platform.claude.com/docs/en/api/messages/count_tokens
