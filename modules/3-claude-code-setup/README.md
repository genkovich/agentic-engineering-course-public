# Module 3 - Claude Code Setup

Встановлення Claude Code, конфігурація під свій стек, ключові режими роботи і блок безпеки (permissions, sandbox, devcontainer). Цей модуль про те, як перетворити Claude Code на робочий інструмент для свого проекту, а не залишити дефолтний CLI.

## Лекції модуля

- 3.1 Встановлення Claude Code
- 3.2 Налаштування робочого середовища
- 3.3 Ввід і команди
- 3.4 Settings.json - повний гід
- 3.5 Сесії, контекст та compaction
- 3.6 Permissions
- 3.7 Sandboxing
- 3.8 Docker та devcontainers
- 3.9 Claude Code поза терміналом + capstone HW

## Артефакти модуля

Лекції 3.1-3.5 проходяться без коду, тільки CLI і конфіг. З лекції 3.6 починається безпековий блок, для якого у repo є 4 starters (Шлях B capstone, 3.9) і reference snippet-и з лекцій 3.3, 3.4, 3.6, 3.7, 3.8 (Шлях A capstone, написати конфіг з нуля).

### Reference snippet-и з лекцій

Окремі шматки конфігурації, які можна вставити у власний проект руками. Дзеркало vault Module 3 у companion repo: vault залишається ground truth, тут копія для CLI-friendly доступу.

| Артефакт | Лекція | Що показує |
|---|---|---|
| [3.3-commands](./3.3-commands/) | 3.3 Ввід і команди | Довідник slash-команд Claude Code (контекст, сесії, код, безпека, MCP, hooks, налаштування) |
| [3.4-settings](./3.4-settings/) | 3.4 Settings.json - повний гід | 3 tier-и (User, Project, Local) у форматі прикладів |
| [3.6-permissions](./3.6-permissions/) | 3.6 Permissions | 4 пресети: team-shared, protect-secrets, python-project, go-project |
| [3.7-sandbox](./3.7-sandbox/) | 3.7 Sandboxing | Блок `sandbox` у settings + OS-level `init-firewall.sh` |
| [3.8-devcontainer](./3.8-devcontainer/) | 3.8 Docker та devcontainers | `devcontainer.json`, `Dockerfile`, `docker-compose.yml` |

### Starters (Шлях B capstone)

4 повноцінні cloneable проекти, кожен покриває Permissions + Sandbox + Devcontainer для свого стеку.

| Starter | Стек | README |
|---|---|---|
| [3.9-starters/nodejs-typescript](./3.9-starters/nodejs-typescript/) | Node.js 20 + TypeScript + Express | [→](./3.9-starters/nodejs-typescript/README.md) |
| [3.9-starters/python-fastapi](./3.9-starters/python-fastapi/) | Python 3.12 + FastAPI + pytest | [→](./3.9-starters/python-fastapi/README.md) |
| [3.9-starters/go-chi](./3.9-starters/go-chi/) | Go 1.22 + chi/v5 | [→](./3.9-starters/go-chi/README.md) |
| [3.9-starters/rust-axum](./3.9-starters/rust-axum/) | Rust stable + axum | [→](./3.9-starters/rust-axum/README.md) |

Starter це capstone artifact для лекцій 3.6-3.9. До цього достатньо самого Claude Code і свого редактора.

### Як вибрати між reference і starter

Capstone HW (Lecture 3.9) має два шляхи:

- **Шлях A** це написати конфіг з нуля по reference прикладах. Студент сам збирає `.claude/settings.json`, `init-firewall.sh`, `Dockerfile`, `devcontainer.json` під свій проект, дивлячись на `3.3-commands` / `3.4-settings` / `3.6-permissions` / `3.7-sandbox` / `3.8-devcontainer`.
- **Шлях B** це склонувати готовий starter відповідного стека з `3.9-starters/` і адаптувати під свій проект.

Capstone Шлях A reference checklist:

- `.claude/settings.json` (Project tier) → база з [3.6-permissions/example-team-shared.json](./3.6-permissions/example-team-shared.json), плюс `sandbox` блок з [3.7-sandbox/example-sandbox-config.json](./3.7-sandbox/example-sandbox-config.json).
- `.devcontainer/devcontainer.json` → [3.8-devcontainer/example-devcontainer.json](./3.8-devcontainer/example-devcontainer.json).
- `.devcontainer/Dockerfile` → [3.8-devcontainer/example-Dockerfile](./3.8-devcontainer/example-Dockerfile).
- `.devcontainer/init-firewall.sh` → [3.7-sandbox/init-firewall.sh](./3.7-sandbox/init-firewall.sh).
- `docker-compose.yml` (опційно, без VS Code) → [3.8-devcontainer/example-docker-compose.yml](./3.8-devcontainer/example-docker-compose.yml).

Покриття у starters: всі 4 starters мають готові версії цих файлів, адаптовані під стек.

## 4 рівні захисту (Lectures 3.6-3.8)

Безпековий блок модуля будує захист пошарово. Зняти будь-який шар можна, але кожен наступний шар підстраховує попередній якщо ти про щось забув.

### Рівень 1: Settings tier (Lecture 3.4)

Три файли settings.json з різними scope:

- `~/.claude/settings.json` (User) - глобальні преференції, не у repo.
- `.claude/settings.json` (Project) - правила команди, у git.
- `.claude/settings.local.json` (Local) - твої overrides, у gitignore.

У starter є тільки Project tier (`.claude/settings.json`) і шаблон Local (`.claude/settings.local.json.example`). User tier налаштовуєш сам глобально.

### Рівень 2: Permissions (Lecture 3.6)

`permissions.allow` і `permissions.deny` у Project settings. Allow це основні команди workflow (тести, лінтер, git diff). Deny це секрети, незворотні операції, sudo, curl-pipe-bash.

Allow адаптується під стек. Deny спільний для всіх starters: блокує читання `.env`, `*.pem`, `*.key`, `~/.ssh`, `~/.aws`.

### Рівень 3: Sandbox (Lecture 3.7)

Блок `sandbox` у Project settings. Працює на рівні OS: bash subprocess не може прочитати файл навіть якщо bash сам дозволений. Захист від обходу permissions через `bash -c "cat .env"`.

`network.allowedDomains` whitelist для outbound з Claude. Все інше блокується.

### Рівень 4: Devcontainer (Lecture 3.8)

`.devcontainer/Dockerfile` + `init-firewall.sh` дають OS-level firewall з default-deny iptables і ipset whitelist. Реальна мережна ізоляція, не application-layer.

`.devcontainer/devcontainer.json` для VS Code. `docker-compose.yml` як альтернатива без VS Code.

## Як обрати starter

- **Працюєш з TypeScript/JavaScript** → `nodejs-typescript`.
- **Python проект, FastAPI або Flask** → `python-fastapi`.
- **Go бекенд** → `go-chi`.
- **Rust сервіс** → `rust-axum`.

Якщо твоя мова не у списку, бери `nodejs-typescript` як reference і адаптуй під свій стек: пакетний менеджер у Makefile, allow-команди у `.claude/settings.json`, домени у `init-firewall.sh`.

## Capstone HW (Lecture 3.9)

Capstone завдання модуля має два шляхи:

**Шлях A** це написати конфіг з нуля по 4 рівнях. Дивись лекції 3.4, 3.6, 3.7, 3.8.

**Шлях B** це клонувати starter відповідного стека, адаптувати під свій проект (свої домени, команди, секрети), запустити `make verify` і показати результат.

Деталі завдання у Lecture 3.9 курсу.
