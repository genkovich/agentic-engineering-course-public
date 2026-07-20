# 11.5 - Claude Code в команді: від пілота до стандарту

Демо-кіт до лекції 11.5. Три сцени наживо: командний репозиторій, managed settings і телеметрія OTel.

```
11.5-team-adoption/
├── team-repo/          # демо-репо очима нового розробника (Скринкаст #1)
├── team-marketplace/   # мінімальний marketplace-репо з одним плагіном
├── managed/            # managed-settings.json + install/uninstall (Скринкаст #2)
├── otel/               # docker compose: Collector + Prometheus + Grafana (Скринкаст #3)
└── README.md
```

## Карта портів

| Порт | Сервіс | Примітка |
|---|---|---|
| 4317 | OTLP gRPC (Collector) | сюди шле Claude Code |
| 4318 | OTLP HTTP (Collector) | альтернативний прийом |
| 8889 | Prometheus exporter (Collector) | звідси скрейпить Prometheus |
| 9090 | Prometheus | UI і query API |
| 3400 | Grafana | UI (3000 всередині контейнера; 3400 вільний на хості) |

## Статус верифікації (2026-07-13, Claude Code 2.1.207)

- ✅ `team-repo`: `node --test` - 5/5 тестів проходять; `.claude/settings.json` валідний.
- ✅ `team-marketplace`: `claude plugin validate ./team-marketplace` - passed, без warnings.
- ✅ `managed`: JSON за документованою схемою; install/uninstall прогнано проти тимчасової теки (свіжий install, бекап наявної політики, відновлення, чисте видалення). **Запис у системну теку потребує sudo - єдиний крок, який робить рекордер вручну.**
- ✅ `otel`: стек піднімається, усі endpoints 200, дашборд і datasource провізіоновані; наскрізний потік телеметрії перевірено - дві реальні сесії з різними `team.id` дали `claude_code_session_count_total` по командах у Prometheus.

---

## 🎬 Скринкаст #1 - team-repo: клон, довіра, повний сетап

**Що показуємо:** новий розробник клонує командний репозиторій і за одне підтвердження довіри отримує весь сетап: permissions, marketplace, плагіни, CLAUDE.md.

> ⚠️ Перед записом: `extraKnownMarketplaces` у `team-repo/.claude/settings.json` і `strictKnownMarketplaces` у `managed/managed-settings.json` вказують на `your-org/team-marketplace` як заглушку. Заміни на реальний github-репо АБО, для локального запису, залий `team-marketplace/` на власний приватний github і онови обидва посилання. Локальний шлях у `extraKnownMarketplaces` авто-пропозицію не тригерить (лише git-джерела) - це поведінка з docs, перевір на своєму білді.

1. Свіжий клон: `git clone <repo> && cd team-repo`.
2. `cat .claude/settings.json` - показати allow/deny, `extraKnownMarketplaces`, `enabledPlugins`.
3. `ls .claude/skills/` - два командні skills (`run-checks`, `create-pr`).
4. Запустити `claude` у корені - зʼявляється trust dialog зі списком правил проєкту. Підтвердити.
5. Прийняти пропозицію встановити marketplace команди; `/plugin` показує `team-standards` активним.
6. Спитати агента: «які критичні правила цього сервісу?» - відповідь зі структури CLAUDE.md без додаткового налаштування.

**Кадр-висновок:** онбординг = `git clone` + одне підтвердження довіри.

---

## 🎬 Скринкаст #2 - managed-settings: політика, яку не обійти

**Що показуємо:** managed-шар задає політику поза репозиторієм; розробник бачить її в `/status`, але вимкнути не може.

```bash
cat managed/managed-settings.json          # deny, disableBypassPermissionsMode, strictKnownMarketplaces
sudo bash managed/install.sh                # кладе файл у /Library/Application Support/ClaudeCode/
```

1. До install: у `claude` виконати `/status` - рядок Setting sources без managed; `claude --dangerously-skip-permissions` стартує.
2. `sudo bash managed/install.sh` - файл лягає в системну теку (наявну політику бекапить у `.pre-11.5-demo.bak`).
3. Перезапустити `claude`, `/status` - тепер Enterprise managed settings із шляхом до файлу.
4. `claude --dangerously-skip-permissions` - відмовляється стартувати.
5. `claude plugin marketplace add <сторонній-репо>` - блокується `strictKnownMarketplaces`.
6. **Відкат обовʼязковий:** `sudo bash managed/uninstall.sh` - відновлює бекап або прибирає demo-файл; `/status` знову без managed.

**Кадр-висновок:** політика живе поза домовленостями; `/status` її показує, вимкнути не можна.

> Для тесту без sudo: `CLAUDE_MANAGED_DIR=/tmp/cc-managed bash managed/install.sh` (і той самий override для uninstall).

---

## 🎬 Скринкаст #3 - OTel: дашборд адопції за двадцять хвилин

**Що показуємо:** одна `docker compose` і один env-прапорець дають повну видимість адопції і витрат на власній інфраструктурі, з розбивкою по командах.

```bash
cd otel
docker compose up -d                        # Collector + Prometheus + Grafana
docker compose ps                           # три контейнери healthy
```

1. Відкрити Grafana: http://localhost:3400 (anonymous Viewer увімкнено; admin/admin для редагування). Дашборд «Claude Code - Adoption & Cost (11.5)».
2. У новому терміналі: `source otel/claude-otel.env && claude` - запустити коротку сесію (правки файлів).
3. Змінити команду і ще сесія: `export OTEL_RESOURCE_ATTRIBUTES=team.id=backend-b,department=engineering && claude` - сесія тільки з питаннями.
4. Через ~15 секунд дашборд оживає: `session.count` по командах, `lines_of_code.count`, `cost.usage` по моделях, рішення по правках. Панель з розбивкою `team_id` показує обидві команди окремо.
5. Прибрати: `docker compose down -v`.

**Кадр-висновок:** видимість адопції і витрат = один `docker compose` + один env-прапорець.

> **Чесна нотатка про приватність:** OTel-мітки містять реальні `user_email` / account_id тієї людини, чия сесія записується. Для публічного відео або зніми ці панелі, або запусти сесію під тестовим акаунтом. Вміст промптів редагується за замовчуванням (`OTEL_LOG_USER_PROMPTS` вимикає це - не вмикай для запису).

---

## Чесні нотатки

- Вивід агента недетермінований - скринкаст може вимагати кількох дублів.
- `team-repo/CLAUDE.md`, критичні правила і болі команд - знеособлені (компанія A з лекції); збіги з реальними сервісами випадкові.
- Скринкаст #2 пише в системну теку; `uninstall.sh` повертає стан. Не забудь відкат.
- Скринкаст #3 читає твій реальний акаунт у мітки - прибери приватні панелі перед публікацією.
