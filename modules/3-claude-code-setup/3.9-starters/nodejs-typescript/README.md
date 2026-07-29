# Starter: Node.js + TypeScript Production-Ready Claude Code

**Module:** 3 - Claude Code Setup
**Stack:** Node.js 20 + TypeScript + Express
**Захищає:** Settings tier + Permissions + Sandbox + Devcontainer (всі 4 рівні Module 3)

## Швидкий старт

1. Клонуй repo або скопіюй цю директорію у свій проект:
   ```bash
   # самостійний потік
   git clone https://github.com/genkovich/agentic-engineering-course-public.git
   cd agentic-engineering-course-public/modules/3-claude-code-setup/3.9-starters/nodejs-typescript

   # груповий потік (потрібен доступ)
   git clone https://github.com/genkovich/agentic-engineering-course.git
   cd agentic-engineering-course/modules/3-claude-code-setup/3.9-starters/nodejs-typescript
   ```
2. Скопіюй `.env.example` у `.env` і заповни (як мінімум `ANTHROPIC_API_KEY`):
   ```bash
   cp .env.example .env
   ```
3. Відкрий папку у VS Code, натисни "Reopen in Container". Альтернатива без VS Code:
   ```bash
   docker compose up --build
   ```
4. Усередині контейнера запусти всі перевірки:
   ```bash
   make verify
   ```

Усі перевірки мають пройти: settings.json валідний, sandbox enabled, firewall блокує example.com, api.anthropic.com доступний.

## Що всередині

| Файл / директорія | Опис |
|---|---|
| `.claude/settings.json` | Project tier: permissions deny/allow, sandbox блок, env vars |
| `.claude/settings.local.json.example` | Шаблон для Local overrides (gitignored у реальному проекті) |
| `.devcontainer/devcontainer.json` | VS Code devcontainer з cap_add NET_ADMIN/NET_RAW |
| `.devcontainer/Dockerfile` | node:20 + Claude Code + iptables + ipset |
| `.devcontainer/init-firewall.sh` | default-deny iptables з whitelist |
| `docker-compose.yml` | Альтернатива devcontainer без VS Code |
| `src/index.ts` | Hello World Express API |
| `tests/sandbox-leak.test.sh` | Перевіряє що sandbox конфіг повний і блокує bash subprocess |
| `tests/firewall.test.sh` | Перевіряє firewall behavior всередині devcontainer |
| `Makefile` | Стандартний API: verify, test, build, clean |
| `package.json`, `tsconfig.json` | TS toolchain |
| `.env.example` | Placeholders для секретів. `.env` у gitignore |

## Рівні захисту

### Рівень 1: Settings tier (Lecture 3.4)

`.claude/settings.json` це Project tier - йде у git, бачить вся команда. `.claude/settings.local.json` для твоїх особистих overrides, у gitignore. User tier (`~/.claude/settings.json`) налаштовуєш сам глобально, не у starter.

### Рівень 2: Permissions (Lecture 3.6)

`permissions.deny` блокує:
- Незворотні bash: `git push --force`, `git reset --hard`, `rm -rf`, `sudo`, `chmod 777`, `curl | sh`.
- Секрети: `Read(.env)`, `Read(**/.env)`, `Read(**/*.pem)`, `Read(**/*.key)`, `Read(~/.ssh)`, `Read(~/.aws)`.
- Edit на `.env` файли.

`permissions.allow` для основного workflow Node.js: `npm install`, `npm test`, `npx`, `git diff/status/log`, `make verify*`.

### Рівень 3: Sandbox (Lecture 3.7)

`sandbox.enabled = true` дає OS-level захист поверх permissions:
- `filesystem.denyRead`: `~/.ssh`, `~/.aws`, `~/.gnupg`, `~/.kube/config`. Bash subprocess не прочитає навіть якщо bash дозволений.
- `network.allowedDomains`: api.anthropic.com, registry.npmjs.org, github.com та інші необхідні. Все поза цим списком блокується.
- `excludedCommands: ["docker"]` - docker запитується звичайно (інакше Docker socket потребує власного OS-level дозволу).

### Рівень 4: Devcontainer (Lecture 3.8)

Останній шар - реальна мережна ізоляція через iptables всередині контейнера:
- `Dockerfile` додає iptables і ipset, встановлює Claude Code globально.
- `init-firewall.sh` ставить default-deny на OUTPUT, додає whitelist через ipset з резолвом доменів.
- `devcontainer.json` додає `--cap-add=NET_ADMIN/NET_RAW` (інакше iptables не запуститься).
- Self-validation у кінці init-firewall.sh: api.anthropic.com має пройти, example.com має заблокуватись.

## Як адаптувати

### Свої домени

Відкрий `.devcontainer/init-firewall.sh`, знайди масив `ALLOWED_DOMAINS`, додай свої API і внутрішні сервіси:

```bash
ALLOWED_DOMAINS=(
  "api.anthropic.com"
  "registry.npmjs.org"
  "api.твоя-компанія.com"
  "internal-jira.твоя-компанія.com"
)
```

Дзеркально оновлюй `sandbox.network.allowedDomains` у `.claude/settings.json` - sandbox і firewall це два незалежні шари, обидва треба тримати у синхроні.

### Свої команди

`.claude/settings.json` `permissions.allow` адаптуй під свій workflow. Базовий список покриває Node.js, додай специфічне для твоєї збірки:

```json
"allow": [
  "Bash(npm install)",
  "Bash(npm run build)",
  "Bash(npm run test)",
  "Bash(docker compose *)",
  "Bash(kubectl get *)"
]
```

### Свої секрети

`.env.example` додай свої поля з заглушками. У `permissions.deny` додай патерни для будь-яких нових секретних файлів:

```json
"deny": [
  "Read(**/private-config.yml)",
  "Read(**/*.token)"
]
```

## Перевірка

| Команда | Що перевіряє |
|---|---|
| `make verify-syntax` | JSON валідний, bash скрипти без syntax errors |
| `make verify-sandbox` | settings.json має повний deny block і sandbox конфіг |
| `make verify-firewall` | у devcontainer: example.com timeout, api.anthropic.com OK |
| `make test` | unit тести проекту через `npm test` |
| `make build` | docker compose build без помилок |

`make verify` запускає всі що можливо у поточному середовищі. На хості без Docker зробить тільки syntax checks. У devcontainer запустить sandbox і firewall тести.

Live тест з Claude (вручну, потребує API key):

```bash
# Створи фейковий .env
cp .env.example .env

# Спробуй прочитати - має заблокуватись permissions
claude --print "прочитай файл .env і покажи його вміст"

# Спробуй обхід через bash subprocess - має заблокуватись sandbox
claude --print 'запусти bash -c "cat .env"'
```

## Gotchas

- **iptables не працює без NET_ADMIN/NET_RAW.** `runArgs` у `devcontainer.json` і `cap_add` у `docker-compose.yml` мусять бути присутні. `make verify-devcontainer` ловить цю помилку.
- **DNS обмежений до nameserver контейнера.** `init-firewall.sh` дозволяє UDP/TCP 53 тільки до IP з `/etc/resolv.conf` (зазвичай `127.0.0.11` для Docker embedded DNS). Це захист від обходу whitelist через arbitrary DNS resolver. Якщо контейнер не має `resolv.conf`, скрипт fallback-ить на `127.0.0.11`.
- **postStartCommand timing window.** Firewall ставиться у `postStartCommand` після старту контейнера. Між стартом і завершенням `init-firewall.sh` є вузьке вікно коли мережа відкрита. Для вищого рівня ізоляції винеси `init-firewall.sh` у `ENTRYPOINT` Dockerfile-у і запускай від root перед перемиканням на non-root user.
- **GitHub CIDR блок розширюється рідко.** `init-firewall.sh` тягне `api.github.com/meta` при старті, валідує кожен CIDR regex-ом і відкидає блоки ширші ніж `/8`. Якщо GitHub міняє ranges, `git clone` може почати падати, тому передбачено re-run init-firewall.sh.
- **IPv6 блокується default-deny.** `ip6tables` мірорить `iptables` правила. Якщо твій VPN/host провайдер дає IPv6, AAAA records резолвляться у `claude-allowed-6` ipset.
- **VS Code Reopen in Container спершу довгий.** Перший build тягне node:20 і npm install -g claude-code. ~5-10 хв. Наступні запуски швидкі завдяки cache layers.
- **`.claude/settings.local.json`** має бути у `.gitignore` свого проекту. У repo лежить тільки `.example` шаблон.
- **`tsx` для dev mode**, `tsc` для production build. Якщо нічого не з'являється у `dist/` - перевір що `npm run build` пройшов.

### Manual permission test з Claude

Тест `tests/sandbox-leak.test.sh` валідує тільки конфіг. Щоб перевірити runtime enforcement, потрібен Claude headless з валідним API ключем:

```bash
# 1. Створи фейковий .env (не справжній - зачитається тільки для тесту)
echo 'FAKE_KEY=test_value_should_not_leak' > .env

# 2. Спроба прочитати - має заблокуватись permission rule
claude --print "прочитай файл .env і покажи мені вміст"
# Очікувано: відмова, посилання на permissions.deny

# 3. Спроба обходу через bash subprocess - має заблокуватись sandbox
claude --print 'запусти bash -c "cat .env"'
# Очікувано: sandbox блокує на рівні ОС, навіть якщо bash дозволений

# 4. Прибери фейковий .env
rm .env
```

Якщо хоч одна спроба пройшла - перевір `.claude/settings.json`: чи `permissions.deny` має `Read(.env)`, чи `sandbox.enabled = true`, чи `defaultMode != bypass`.

## Source

- [Lecture 3.4 - Settings.json - повний гід](https://...)
- [Lecture 3.6 - Permissions](https://...)
- [Lecture 3.7 - Sandboxing](https://...)
- [Lecture 3.8 - Docker та devcontainers](https://...)
- [Lecture 3.9 - Capstone HW](https://...)
- Reference Anthropic devcontainer: https://github.com/anthropics/claude-code/tree/main/.devcontainer
- Документація Settings: https://docs.claude.com/en/docs/claude-code/settings
- Документація Permissions: https://docs.claude.com/en/docs/claude-code/iam
