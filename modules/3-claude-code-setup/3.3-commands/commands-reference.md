# Довідник команд Claude Code

Повний список команд Claude Code, згрупований по кластерах. Набери `/` в Claude Code щоб побачити доступні команди з фільтрацією по літерах. Ключові команди з поясненнями — в [[Lecture 3.3 - Ввід, команди та персоналізація]]

---

## Контекст, сесії і вартість

| Команда | Що робить |
|---------|-----------|
| `/context` | Візуалізує поточне використання контексту як кольорова сітка. Показує optimization suggestions: memory bloat, context-heavy tools, capacity warnings |
| `/cost` | Вартість поточної сесії і кількість токенів. Для API users — реальний billing. Для підписників — usage overview |
| `/stats` | Щоденне використання, історія сесій, streaks, переваги моделей — візуалізація у стилі GitHub contribution graph |
| `/usage` | Ліміти плану і статус rate limits. Коли і скільки залишилось |
| `/compact [instructions]` | Стиснути контекст з опціональним фокусом: `/compact focus on the auth module` зберігає деталі auth і стискає решту |
| `/clear` | Очистити контекст повністю. Аліаси: `/reset`, `/new` |
| `/rename [name]` | Назви поточну сесію. Без аргументу — авто-назва з AI. Потім `/resume` показує її за іменем |
| `/resume [session]` | Відновити сесію по ID або назві, або відкрити session picker. Аліас: `/continue` |
| `/rewind` | Відкотити розмову/код до попередньої точки. Аліас: `/checkpoint` |

## Код і файли

| Команда | Що робить |
|---------|-----------|
| `/diff` | Інтерактивний diff viewer: uncommitted changes + per-turn diffs. ←/→ між git diff і turns Claude. ↑/↓ між файлами |
| `/export [filename]` | Експортує розмову як plain text. Без аргументу — діалог copy/save |
| `/copy [N]` | Копіює останню відповідь в clipboard. `/copy 2` — передостанню. При code blocks — interactive picker. `w` пише в файл (корисно через SSH) |
| `/add-dir <path>` | Додати нову робочу директорію до поточної сесії. Claude бачить файли з обох директорій |

## Аналіз і безпека

| Команда | Що робить |
|---------|-----------|
| `/insights` | Генерує звіт по твоїх Claude Code сесіях: які частини проекту найчастіше чіпаєш, interaction patterns, friction points. Як аналітика для розробника |
| `/security-review` | Аналізує pending changes (git diff) на security вразливості: ін'єкції, auth проблеми, data exposure. Як security review перед PR |
| `/pr-comments [PR]` | Підтягує коментарі з GitHub PR. Автовизначає PR для поточної гілки або передай URL/номер. Потребує `gh` CLI |
| `/release-notes` | Повний changelog Claude Code. Найновіша версія найближче до промпту |
| `/doctor` | Діагностика інсталяції: перевіряє всі settings sources, authentication, MCP з'єднання |

## Workflow

| Команда | Що робить |
|---------|-----------|
| `/btw <question>` | Бокове питання без додавання в контекст. "До речі, що означає sparse checkout?" — відповідь не забруднює основну розмову |
| `/branch [name]` | Розгалужити розмову: створює нову сесію з тією ж історією. Аліас: `/fork` |
| `/plan [description]` | Увійти в plan mode прямо з промпту. `/plan fix the auth bug` — одразу починає планування |
| `/schedule` | Створити/оновити хмарні scheduled tasks. Claude проведе через setup |
| `/sandbox` | Toggle sandbox mode (деталі в уроці 3.7) |
| `/init` | Створити CLAUDE.md для проекту. З `CLAUDE_CODE_NEW_INIT=true` запускає інтерактивний setup |
| `/hooks` | Показати конфігурацію hooks для tool events |
| `/memory` | Редагувати CLAUDE.md memory файли, toggle auto-memory |
| `/agents` | Управління конфігураціями subagents |
| `/mcp` | Управління MCP з'єднаннями і OAuth автентифікацією |
| `/plugin` | Browse, install, enable/disable плагіни |
| `/skills` | Показати доступні skills |
| `/tasks` | Показати і управляти background tasks |

## Налаштування і персоналізація

| Команда | Що робить |
|---------|-----------|
| `/config` | GUI інтерфейс налаштувань — вкладки, toggle, вибір моделі. Аліас: `/settings` |
| `/status` | Версія, модель, аккаунт, connectivity. Працює під час відповіді Claude |
| `/model [model]` | Змінити модель. ←/→ для effort level. Зміна негайна, не чекає завершення відповіді |
| `/effort [level]` | Змінити effort: low/medium/high/max/auto. Негайно, без очікування |
| `/fast [on\|off]` | Toggle fast mode |
| `/theme` | Змінити кольорову тему. Light/dark, daltonized, ANSI |
| `/chrome` | Toggle Chrome інтеграції: browse, click, type на сторінках. Потребує Chrome extension |
| `/color [color]` | Колір prompt bar: red, blue, green, yellow, purple, orange, pink, cyan |
| `/vim` | Toggle Vim / Normal editing mode |
| `/voice` | Toggle push-to-talk voice dictation |
| `/keybindings` | Відкрити конфігурацію keybindings |
| `/statusline` | Налаштувати status line — опиши природною мовою що хочеш бачити |
| `/terminal-setup` | Налаштувати Shift+Enter і шорткати для терміналу. Видима тільки якщо термінал це потребує |
| `/permissions` | Показати всі permission rules і їх джерела. Аліас: `/allowed-tools` |

## Login, plans, meta

| Команда | Що робить |
|---------|-----------|
| `/login` / `/logout` | Авторизація в Anthropic аккаунт |
| `/upgrade` | Сторінка апгрейду плану (тільки Pro/Max) |
| `/extra-usage` | Налаштувати extra usage коли rate limits вичерпані |
| `/privacy-settings` | Privacy налаштування (тільки Pro/Max) |
| `/feedback` | Надіслати feedback. Аліас: `/bug` |
| `/desktop` | Продовжити сесію в Desktop app (macOS/Windows). Аліас: `/app` |
| `/remote-control` | Зробити сесію доступною для remote control з claude.ai. Аліас: `/rc` |
| `/mobile` | QR код для Claude mobile app. Аліаси: `/ios`, `/android` |
| `/install-github-app` | Встановити Claude GitHub Actions для репозиторію |
| `/install-slack-app` | Встановити Claude Slack app через OAuth flow |
| `/stickers` | Замовити Claude Code стікери |
| `/passes` | Поділитись безкоштовним тижнем Claude Code (якщо eligible) |

---

## Примітки

> [!note] Видимість команд
> Не всі команди видимі всім. `/desktop` тільки на macOS і Windows. `/upgrade` і `/privacy-settings` тільки на Pro і Max. `/terminal-setup` прихована якщо термінал нативно підтримує keybindings. `/passes` видима тільки якщо аккаунт eligible. Тому `/help` показує різний список залежно від контексту

Також є MCP prompts — команди від MCP серверів у форматі `/mcp____<server>__<prompt>`. Автоматично з'являються від підключених серверів

### Keyboard shortcuts

Багато команд мають шорткати: `Alt+P` = `/model`, `Alt+T` = thinking toggle, `Alt+O` = `/fast`, `Shift+Tab` = cycle permission mode, `Ctrl+O` = verbose/transcript mode, `Ctrl+R` = model/thinking quick change, `Ctrl+L` = clear screen, `Ctrl+B` = background task. Повний список — в уроці 3.2
