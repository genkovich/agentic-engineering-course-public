# Demos: lecture-5 (Plugins)

**Module:** 5 — Claude Code extended
**Lecture:** 5.5 — Plugins: встановлення та використання

Демо-сет для скринкастів лекції 5.5. Усі 6 скринкастів — **file-based walkthroughs**: жодного виконання команд у терміналі. CLI-команди цитуються лише у voiceover як reference.

| Папка | Призначення | Скринкаст(и) |
|---|---|---|
| `hello-plugin/` | Універсальний демо-плагін: маніфест, command, skill, hook, bin | 1, 2 |
| `examples/scope-project-after/` | After-state `.claude/settings.json` після `--scope project` install | 3 |
| `examples/edit-loop/` | Before/after `greet.md` — приклад правки одного файлу для `/reload-plugins` циклу | 4 |
| `audit-example/` | Навчальний «поганий» плагін з ред-флаг хуком (не встановлювати) | 5 |
| `standalone-before/` | Початкова точка для конвертації standalone → plugin | 6 |
| `hello-plugin-converted/` | After-state конвертації — повна структура plugin після 4 кроків міграції | 6 |

## Що демонструє кожен скринкаст

### 🎬 1 — Структура плагіна (~60s)
- **Open:** IDE на `hello-plugin/`, file explorer розгорнутий
- **Show:** `.claude-plugin/` містить тільки `plugin.json`; компоненти на корені; `plugin.json` поля `name/description/version/author`; `bin/hello-bin` і `hooks/hooks.json` як приклади
- **Key points:** маніфест ізольований у `.claude-plugin/`; компоненти на корені; `bin/` показує що плагін ширший за чотири основні типи

### 🎬 2 — `--plugin-dir` + namespace (~45s)
- **Open:** split `hello-plugin/commands/greet.md` ↔ `hello-plugin/.claude-plugin/plugin.json`. Слайд деки з `claude --plugin-dir ./hello-plugin` як reference
- **Show:** поле `name` у маніфесті стає namespace-префіксом для `/hello-plugin:greet`; без префікса `/greet` не існує
- **Key points:** жоден скринкаст не запускає Claude Code — структура файлів і слайд-cite пояснюють поведінку

### 🎬 3 — Installation scopes через after-state (~45s)
- **Open:** `examples/scope-project-after/.claude/settings.json` поруч з README
- **Show:** блок `enabledPlugins` з записом `hello-plugin@local-marketplace`; README пояснює що це commit-ready state після `claude plugin install hello-plugin --scope project`
- **Key points:** `--scope project` → `.claude/settings.json` (комітиться); без флагу — у `~/.claude/` (тільки для тебе)

### 🎬 4 — Edit-loop через before/after файли (~60s)
- **Open:** split `examples/edit-loop/before/greet.md` ↔ `examples/edit-loop/after/greet.md` + README
- **Show:** одне додане речення про `/reload-plugins` у `after/`; решта файлу ідентична. README описує 5-кроковий цикл `--plugin-dir → виклик → правка → /reload-plugins → повторний виклик`
- **Key points:** dev-loop без install і без рестарту; CLI-команди цитуються у voiceover, не виконуються

### 🎬 5 — Trust audit (~60s)
- **Open:** `audit-example/` у file explorer + side-by-side `hello-plugin/hooks/hooks.json` як reference
- **Show:** `plugin.json` з фейковим автором (`anon-dev-2024@nowhere.invalid`); `hooks.json` з `matcher: ".*"`, `curl POST` на чужий endpoint, `exit 0` для приховування
- **Key points:** trust = on you; ексфільтрація `tool_input` без логів — навмисна стелс-поведінка

### 🎬 6 — Конвертація standalone → plugin через side-by-side (~75s)
- **Open:** split file explorer `standalone-before/.claude/` ↔ `hello-plugin-converted/` + слайд деки з 4 кроками
- **Show:**
  1. `hello-plugin-converted/.claude-plugin/plugin.json` — новий маніфест з `name: "hello-plugin"`
  2. `commands/greet.md` і `skills/welcomer/SKILL.md` ідентичні з обох сторін — лише шлях змінився
  3. `standalone-before/.claude/settings.json` блок `hooks` ↔ `hello-plugin-converted/hooks/hooks.json` — той самий вміст, але як кореневий обʼєкт
  4. На слайді — `claude --plugin-dir ./hello-plugin-converted` як ефемерний run для перевірки
- **Key points:** файли всередині `commands/`/`skills/` не змінюються; `/greet` стає `/hello-plugin:greet`

## Pre-recording cleanup (опційно)

Скринкасти не виконують команд, тому offline plugin state не впливає на запис. Якщо ти колись запускав `claude plugin install hello-plugin` локально і хочеш чистого окружения для voiceover-демо:

```bash
# remove any installed hello-plugin artifacts (do not blanket-rm ~/.claude/plugins/)
claude plugin uninstall hello-plugin 2>/dev/null || true
```

## Lecture link

`Own Brand/AI Course/Claude Course/Module 5/Lecture 5/Lecture 5.5 - Plugins.md` — voiceover тексти і `Open/Show/Say/Cut` для кожного скринкасту.
