---
name: legacy-screencast
description: Use when preparing screencast recording for one of the four protocol steps. Generates an asciinema or vhs script with explicit narration markers. Triggers on '/legacy-screencast <step>' or when user asks to 'записати скрінкаст для Step 2', 'screencast script', 'демо запис'.
argument-hint: <step> (1|2|3|4)
allowed-tools: Read, Write, Bash
disable-model-invocation: false
---

# legacy-screencast — генерація скрінкаст-сценаріїв

Опційний skill — допомагає лектору/курсанту записати скрінкаст для одного з 4 кроків. Не запускається автоматично; зазвичай — окремий цикл після того, як основний протокол вже пройдено.

## Аргументи

- `<step>` — номер Step (1, 2, 3, або 4). Step 3 додатково розбивається на `3.1`, `3.2`, `3.3`.

## Output: SCREENCAST-step<N>.sh

bash-сценарій з коментарями для запису через asciinema або vhs:

```bash
#!/usr/bin/env bash
# Screencast for Step 2 — extract + critic
# Tools: asciinema rec / vhs / OBS+terminal
# Duration: ~5-7 minutes

# === Setup ===
cd ~/sources/claude-course-demos/4.9-legacy-refactor
git status                                    # clean working tree

# === Recording ===

# 🎬 [00:00] — open Claude in plan mode
claude
# (UI: Shift+Tab двічі — у footer plan mode on)

# 🎬 [00:30] — extract
# Type у Claude:
# /legacy-extract account

# 🎬 [03:00] — wait for parallel subagents (3-5 min)
# Show /context — < 10k

# 🎬 [04:00] — verify output
cat LEGACY/account.md      # 6 секцій присутні
wc -w LEGACY/account.md    # ≤ 1500 words (~2k tokens)

# 🎬 [05:00] — critic
# /legacy-critic account
cat CRITIC.md
grep "Спростовані (0)" CRITIC.md  # ✅ verdict
```

## Acceptance criteria

- Сценарій містить timecode-маркери `# 🎬 [MM:SS]`
- Тривалість ≤ 10 хвилин для одного Step
- Включає expected output для перевірки на запис
- НЕ включає sleep'ів довших за 30 секунд (для очікування subagents — `# wait`).

## Examples

```
/legacy-screencast 2     # генерує SCREENCAST-step2.sh
/legacy-screencast 3.2   # генерує SCREENCAST-step3-tests.sh
```

## Anti-patterns

- **Не записуй скрінкаст до того, як протокол пройдено руками** — без real run скрінкаст-сценарій ламається на 60% часу.
- **Не вмикай sleep > 30s у сценарій** — глядач не дочекається. Кат на «3-5 хв пізніше».
- **Не пропускай маркери `🎬 [MM:SS]`** — вони використовуються post-production для timestamp у YouTube description.
