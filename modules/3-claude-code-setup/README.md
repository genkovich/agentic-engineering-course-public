# Module 3 — Claude Code Setup

Встановлення Claude Code, конфігурація під свій стек, ключові режими роботи і блок безпеки (permissions, sandbox, devcontainer). Цей модуль про те, як перетворити Claude Code на робочий інструмент для свого проекту, а не залишити дефолтний CLI.

## Лекції модуля

- 3.1 Встановлення Claude Code
- 3.2 Налаштування робочого середовища
- 3.3 Ввід і команди
- 3.4 Settings.json — повний гід
- 3.5 Сесії, контекст та compaction
- 3.6 Permissions
- 3.7 Sandboxing
- 3.8 Docker та devcontainers
- 3.9 Claude Code поза терміналом + capstone HW

## Артефакти модуля

Лекції 3.1–3.5 проходяться без коду, тільки CLI і конфіг. З лекції 3.6 починається безпековий блок, для якого у repo є 4 starters — повноцінні cloneable проекти, кожен покриває Permissions + Sandbox + Devcontainer для свого стеку.

| Starter | Стек | README |
|---|---|---|
| [nodejs-typescript](./starters/nodejs-typescript/) | Node.js 20 + TypeScript + Express | [→](./starters/nodejs-typescript/README.md) |
| [python-fastapi](./starters/python-fastapi/) | Python 3.12 + FastAPI + pytest | [→](./starters/python-fastapi/README.md) |
| [go-chi](./starters/go-chi/) | Go 1.22 + chi/v5 | [→](./starters/go-chi/README.md) |
| [rust-axum](./starters/rust-axum/) | Rust stable + axum | [→](./starters/rust-axum/README.md) |

Starter це capstone artifact для лекцій 3.6–3.9. До цього достатньо самого Claude Code і свого редактора.

## 4 рівні захисту (Lectures 3.6–3.8)

Безпековий блок модуля будує захист пошарово. Зняти будь-який шар можна, але кожен наступний шар підстраховує попередній якщо ти про щось забув.

### Рівень 1: Settings tier (Lecture 3.4)

Три файли settings.json з різними scope:

- `~/.claude/settings.json` (User) — глобальні преференції, не у repo.
- `.claude/settings.json` (Project) — правила команди, у git.
- `.claude/settings.local.json` (Local) — твої overrides, у gitignore.

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

Capstone завдання модуля: склонувати starter відповідного стека, адаптувати під свій проект (свої домени, команди, секрети), запустити `make verify` і показати результат. Деталі завдання у Lecture 3.9 курсу (LMS).
