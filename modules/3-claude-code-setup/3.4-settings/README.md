# 3.4 Settings: приклад для Node.js-команди

Коментований приклад до уроку 3.4 «Settings.json - повний гід». Сценарій: проєкт на Node.js + TypeScript, команда з п'яти людей, а один із розробників ще й підтримує Go-частину.

У JSON не можна писати коментарі, тому всі пояснення тут. Приклад звірено з документацією code.claude.com/docs, а спірні правила перевірено наживо в Claude Code.

## Куди копіювати

| Файл | Куди | Рівень | У git |
|---|---|---|---|
| `example-user-settings.json` | `~/.claude/settings.json` | User: ваші налаштування для всіх проєктів | ні |
| `example-project-settings.json` | `.claude/settings.json` у корені проєкту | Project: правила команди | так, кожен отримає його разом із репозиторієм |
| `example-local-settings.json` | `.claude/settings.local.json` у корені проєкту | Local: ваші правки саме для цього проєкту | ні |

Пріоритет рівнів такий: Local > Project > User. Адаптуйте файли під свій стек і не копіюйте їх буквально.

## User: ваш особистий стиль

- `model: sonnet`, `effortLevel: medium` (наскільки глибоко модель міркує перед відповіддю), `outputStyle: Explanatory` (Claude додатково пояснює свої рішення) і `language: ukrainian` задають, як Claude працює з вами в усіх проєктах.
- `"voice": { "enabled": true }` вмикає голосове введення. Ключ `voiceEnabled` застарів.
- `attribution` з порожніми `commit` і `pr` прибирає AI-підпис, тобто рядок `Co-Authored-By` у комітах і позначку в описі PR. Це ваше особисте рішення.
- `cleanupPeriodDays: 14` видаляє старі сесії (історію розмов) частіше, ніж типово (30 днів).
- Косметичні налаштування на ваш смак: `spinnerTipsEnabled: false` прибирає підказки у спінері, а в блоці `env` змінна `CLAUDE_CODE_NO_FLICKER=1` вмикає fullscreen-режим, у якому інтерфейс не мерехтить під час перемальовування.
- `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` (теж у блоці `env`) прибирає облікові дані з середовища Bash, хуків і зовнішніх інструментів (stdio MCP-серверів), щоб команди, які запускає Claude, не бачили ваших токенів і паролів. Змінна лежить у User, бо в нашій перевірці наживо Claude Code ігнорував її в `.claude/settings.json` і писав попередження «project-scoped settings can't set this key». Задати її можна в `~/.claude/settings.json` або в managed settings, тобто налаштуваннях, які розгортає адміністратор компанії.

## Project: домовленості команди

- Завдяки `$schema` у першому рядку (у Local теж) редактор підказує назви ключів. Назви ключів схема суворо перевіряє тільки всередині `permissions`, тож опечатку, наприклад, у `cleanupPeriodDays` редактор не підсвітить: перевіряйте назви вручну.
- `defaultMode: acceptEdits` означає, що команда домовилась приймати правки файлів без підтвердження. `auto` і `bypassPermissions`, режими, де Claude діє без запитів, не діють ні з проєктного, ні з локального файлу. Задавати їх треба в `~/.claude/settings.json` або в managed settings.
- `allow` дозволяє те, що команда запускає щодня: `npm run`, `npm test`, `npx`, `git add/commit/diff/log/status`, `gh pr create`. Там же дозволені MCP-інструменти у форматі `mcp__<сервер>__<інструмент>`, а зірочка в `mcp__playwright__*` означає всі інструменти сервера playwright.
- `ask` щоразу питає підтвердження перед `gh pr merge`.
- `deny` забороняє `git push`, `rm -rf`, `curl ... | bash`, `curl ... | sh` і читання `.env`, `credentials`, `.pem`, `.key`. Заборону з Project не скасує жоден інший рівень. Правило `Read(**/.env)` блокує і `cat`, `head`, `tail` у Bash, але лише файлові команди, які Claude Code розпізнає: скрипт на Python чи Node, який сам відкриває файл, воно не зупинить.
- У нашій перевірці наживо правило `Bash(curl * | bash*)` не блокувало `| sh`, тому поруч стоїть окреме `Bash(curl * | sh*)`.
- Правил `Bash(* --version)` чи `Bash(* --help)` у прикладі немає. Зірочка на початку збігається з чим завгодно, тож у нашій перевірці наживо `bash -c 'touch marker' --version` з таким дозволом виконалась без запиту. Так само пройшла б будь-яка команда всередині `bash -c`. Якщо вам потрібен такий дозвіл, вказуйте конкретну програму: `Bash(node --version)`.
- `BASH_DEFAULT_TIMEOUT_MS=300000` (5 хв) потрібен, бо тести проєкту тривають довше за дефолтні 2 хв.
- Хук `PreToolUse`, команда, яку Claude Code запускає перед кожним викликом інструмента, тут спрацьовує на Bash і пише в `/tmp/claude-audit.log` час кожного виклику (саму команду не пише). Так у команди є найпростіший аудит: кожен бачить, коли Claude запускав Bash.
- `worktree.symlinkDirectories`: коли Claude Code створює окрему робочу копію репозиторію через git worktree, `node_modules` і `.cache` стають у ній симлінками, тож залежності не ставляться заново.
- `companyAnnouncements` показує нагадування команді на старті, наприклад «Run npm run lint before committing».

> `allow` з цього файлу запрацює лише після того, як під час першого запуску ви підтвердите довіру до теки у вікні довіри (trust dialog). `deny` і `ask` діють одразу. В інтерактивному режимі Claude Code показує вікно довіри, а `claude -p` у теці, якій ви ще не довіряли, пише попередження, що ігнорує allow.

## Local: тільки ваше і тільки тут

- `allow` на `go test ./...`, `go build ./...`, `make *`, бо Go-частину підтримуєте лише ви.
- `CLAUDE_CODE_DISABLE_MOUSE=1` у блоці `env`, бо ви працюєте в tmux і не хочете, щоб Claude Code перехоплював мишу.
- `enabledMcpjsonServers: ["playwright"]` вмикає з серверів, описаних у `.mcp.json` у корені проєкту, тільки playwright, бо Playwright MCP потрібен тільки вам.
- `model: opus`, бо в цьому проєкті вам потрібна сильніша модель. Local має пріоритет над User.

## Що вийде, коли Claude Code об'єднає три файли

- **Скаляри**, тобто рядки й числа на кшталт `model`, перевизначаються: береться значення з вищого рівня, тож `model` буде `opus` з Local.
- **Списки** зливаються: `allow` містить правила з Project і Local разом, а `deny` з Project діє незалежно від Local. Навіть якщо в Local ви дозволите `git push`, заборона з Project усе одно спрацює.
- **`env`** - це об'єкт: кожна змінна береться з найвищого рівня, де її задано.

## Перевірки

1. Запускайте Claude Code з кореня проєкту, бо Claude Code читає `.claude/settings.json` з теки, звідки його запустили.
2. Виконайте `/status` і знайдіть рядок `Setting sources`. Там перелічено прочитані файли. Звідки взявся конкретний ключ, `/status` не показує.
3. Додайте `.claude/settings.local.json` у `.gitignore` і перевірте `git status`. Local-файлу там бути не повинно, а `.claude/settings.json` має бути (якщо ще не закомічений).

## Посилання

- Урок 3.4 «Settings.json - повний гід» у курсі
- https://code.claude.com/docs/en/settings
- https://code.claude.com/docs/en/permissions
- https://code.claude.com/docs/en/env-vars
