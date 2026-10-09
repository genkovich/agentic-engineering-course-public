# Lecture 11.2.1 — monitoring, observability та AI-черговий

Ця лекція починається після завершеної
[`11.2-vps-deploy`](../11.2-vps-deploy/README.md): `course-project` уже працює на
VPS, self-hosted runner уже зелений, deploy workflow уже проходить.

Тепер додаємо компоненти по одному:

```text
course-project /api/metrics → Prometheus → Grafana
course-project stdout → Alloy → Loki → Grafana
Prometheus rules → Alertmanager → watcher webhook → bounded report → AI verdict
deploy workflow ────────────────────────→ watcher webhook ────────────┘
```

Це **self-hosted Grafana OSS**. Немає Grafana Cloud, trial або окремої SaaS
оплати. Ми платимо лише за ресурси власної VPS. Обмеження чесне: якщо впаде вся
VPS, локальний monitoring теж впаде і не зможе повідомити назовні.

## 1. Спочатку створюємо метрики в застосунку

`course-project` спочатку не має `/metrics`. Тому kit додає:

- `prom-client@15.1.3`;
- [`lib/observability.ts`](course-project-files/lib/observability.ts) з Counter,
  Histogram і process metrics;
- [`/api/metrics`](course-project-files/app/api/metrics/route.ts) у Prometheus
  text format;
- wrappers для `/api/memes` і `/api/memes/random`;
- JSON logs одного request у stdout.

Покроковий видимий diff (що саме змінюється в коді застосунку і як інструментувати
свої власні роути, а не тільки ці мем-роути) - у
[`course-project-metrics.md`](course-project-metrics.md).

Після deploy відкрий:

```bash
curl http://SERVER_IP/api/metrics | head -40
```

Це лише **поточний snapshot**. Застосунок не зберігає історію і не малює
графіки. Саме тому наступним з'являється Prometheus.

Базові signals:

| Metric | Що означає |
|---|---|
| `up` | Prometheus зміг забрати `/api/metrics` |
| request rate | скільки HTTP requests за секунду |
| 5xx ratio | частка server errors |
| p95 latency | 95% requests завершилися не повільніше цього часу |
| process RSS | приблизно скільки RAM тримає Node process |

## 2. Prometheus зберігає історію

Prometheus кожні 15 секунд робить HTTP GET на `app:3000/api/metrics`, додає
timestamp і зберігає time series у named volume. Конфіг лежить у
[`prometheus.yml`](course-project-files/observability/prometheus/prometheus.yml).

Чому `app:3000`, а не public IP? Усередині Compose services бачать один одного
за service name. Traffic не виходить в internet.

Prometheus UI слухає лише `127.0.0.1:9090`. З ноутбука відкриваємо SSH tunnel:

```bash
ssh -L 9090:127.0.0.1:9090 deploy@SERVER_IP
```

`-L LOCAL_PORT:REMOTE_HOST:REMOTE_PORT` шифровано переносить локальний port
9090 до loopback port 9090 на VPS. Після цього відкрий `http://localhost:9090`
і виконай query `up{job="course-project"}`.

## 3. Grafana лише візуалізує

Grafana не замінює Prometheus і не збирає metrics із застосунку. Вона робить
queries до Prometheus і малює panels. Другий data source — Loki для logs.

Dashboard уже provisioning-иться з repository:
[`course-project.json`](course-project-files/observability/grafana/dashboards/course-project.json).

```bash
ssh -L 3001:127.0.0.1:3001 deploy@SERVER_IP
```

Відкрий `http://localhost:3001`, login `admin`, password — з локального
`observability/secrets/grafana-admin-password.txt` на VPS. У folder
`Course Project` відкрий `Course Project / Production`.

📸 Для запису: `06-grafana-login.png`, `07-dashboard-signals.png`.

## 4. Loki та Alloy додають логи

Застосунок пише один JSON object на рядок у stdout. Docker уже зберігає stdout,
але шукати його через `docker logs` незручно.

- **Alloy** читає Docker socket тільки для service `app` і пересилає log lines;
- **Loki** індексує labels і зберігає logs 7 днів;
- **Grafana Explore** виконує LogQL query `{service_name="app"}`.

Docker socket змонтований read-only, але це все одно sensitive interface. Alloy
працює як root лише щоб читати socket; AI watcher socket не отримує взагалі.

У Grafana Explore:

```logql
{service_name="app"}
{service_name="app"} |= "error"
```

📸 Для запису: `08-loki-explore.png` з однією розгорнутою JSON log line.

## 5. Alert rules і webhook

Rules у [`app.yml`](course-project-files/observability/prometheus/rules/app.yml):

- app недоступний 1 хвилину;
- 5xx ratio ≥ 5% протягом 2 хвилин;
- p95 ≥ 1 s протягом 2 хвилин.

Prometheus обчислює rules. Alertmanager групує й дедуплікує alerts, потім робить
signed-by-token POST на внутрішній endpoint
`http://watcher:3001/webhooks/alertmanager`. Endpoint не публічний.

Watcher також має loopback endpoint для post-deploy check:
`http://127.0.0.1:3002/webhooks/deploy`. Його викликає
[`release-watch.yml`](course-project-files/.github/workflows/release-watch.yml)
після успішного `deploy-vps`.

Обидва triggers використовують той самий pipeline, але мають різний context:
deploy передає commit SHA, Alertmanager — labels і annotations alert.

## 6. Де саме AI

Watcher спочатку **без AI** робить bounded `release-report.json`:

- fixed 5-minute window;
- `up`, request rate, 5xx ratio, p95;
- максимум 50 error log lines;
- thresholds і release SHA;
- sanitized trigger data.

Лише цей report читає `$review-release-health`. Skill повертає strict JSON:

```json
{
  "schema_version": 1,
  "status": "anomaly",
  "should_open_issue": true,
  "summary": "5xx ratio crossed the release threshold.",
  "evidence": ["error_ratio=0.12, threshold=0.05"],
  "recommended_action": "investigate",
  "dedupe_key": "release-abc123"
}
```

Code перевіряє schema. Model не має Bash, network, GitHub, Docker socket, SSH і
не робить rollback. Без Anthropic API key metrics, dashboard, logs, alerts і
reports продовжують працювати; пропускається лише AI verdict.

## 7. Копіюємо kit у `course-project`

Спочатку застосуй Lecture 11.2 kit. Потім із кореня course repository:

```bash
modules/11-production/11.2-agent-on-duty/apply-to-course-project.sh \
  /path/to/course-project
```

Скрипт копіює всі файли, pin-ить `prom-client@15.1.3` і оновлює lockfile.

На VPS у checkout repository:

```bash
observability/init-secrets.sh
```

`init-secrets.sh`:

- `set -euo pipefail` зупиняє script при error, unset variable або failed pipe;
- `umask 077` робить нові secret files доступними лише власнику;
- `openssl rand` генерує випадкові token і Grafana password;
- створює `~/.config/course-project/observability.env` і secret files **поза
  runner checkout**, тому `actions/checkout` не видаляє їх;
- створює порожній `anthropic-api-key.txt`, щоб AI був opt-in.

Якщо потрібен AI review, встав API key у
`~/.config/course-project/anthropic-api-key.txt`. Значення
`~/.config/course-project/watcher-token.txt` один раз скопіюй у GitHub Actions secret
`WATCHER_WEBHOOK_TOKEN`. Не показуй ці файли в записі.

Після застосування 11.2.1 workflow `deploy-vps.yml` навмисно замінюється: він
піднімає **обидва** Compose-файли. Інакше base workflow з `--remove-orphans`
зупинив би monitoring services під час наступного deploy.

## 8. Перевіряємо конфіги до запуску

```bash
docker compose \
  --env-file .env.observability.example \
  -f compose.vps.yml \
  -f compose.observability.yml \
  config

docker run --rm \
  --entrypoint /bin/promtool \
  -v "$PWD/observability/prometheus:/etc/prometheus:ro" \
  prom/prometheus:v3.13.1 \
  check config /etc/prometheus/prometheus.yml

docker run --rm \
  -v "$PWD/observability/alertmanager:/etc/alertmanager:ro" \
  prom/alertmanager:v0.33.1 \
  amtool check-config /etc/alertmanager/alertmanager.yml
```

`-f` поєднує base Compose і observability overlay. `--entrypoint` просить image
запустити validator `promtool` замість Prometheus server. `-v HOST:CONTAINER:ro`
монтує config read-only у temporary validation container. `--rm` видаляє
container після check.

## 9. Запускаємо й відкриваємо тільки через SSH tunnels

```bash
docker compose \
  --env-file "$HOME/.config/course-project/observability.env" \
  -f compose.vps.yml \
  -f compose.observability.yml \
  up -d --build
```

Жоден admin UI не відкритий у public internet: усі bindings починаються з
`127.0.0.1`. Один tunnel може відкрити все потрібне:

```bash
ssh \
  -L 3001:127.0.0.1:3001 \
  -L 9090:127.0.0.1:9090 \
  -L 9093:127.0.0.1:9093 \
  deploy@SERVER_IP
```

## 10. Повний цикл перевірки

1. Відкрий app і кілька разів згенеруй/збережи meme.
2. Перевір `/api/metrics`.
3. Дочекайся points у Prometheus.
4. Відкрий provisioned Grafana dashboard.
5. Знайди JSON logs у Loki.
6. Запусти `release-watch` через `Run workflow`.
7. На VPS виконай:

```bash
scripts/show-release-watch.sh
```

Скрипт показує watcher logs, зібраний report і, якщо заданий AI key, validated
verdict. Це і є повний loop: deploy → signals → report → bounded AI review.

## 11. Від аномалії до draft-PR фіксу

Досі AI-черговий лишався **read-only**: watcher складав bounded report,
`$review-release-health` повертав strict verdict із полем `should_open_issue`, і
на цьому ланцюг обривався. Поле ніхто не читав. `alert-worker.yml` замикає петлю:
бере anomaly-verdict і готує **draft PR** із найменшим фіксом. Мерджить людина.

Це те саме, що issue-worker з 11.1 (issue → sandboxed агент → draft PR), але
стартує від алерту, а не від issue. І головне — теза безпеки не слабшає, а
**посилюється**: read-шлях лишається без прав на запис, а окремий write-шлях
працює на ефемерній VM, ніколи не на VPS.

Один workflow, дві джоби на двох типах ранерів:

```text
schedule */15  ┐
workflow_dispatch ├→ detect (VPS, self-hosted)      author-fix (ubuntu-latest, ефемерна VM)
                 │   permissions: contents: read      permissions: contents: write, pull-requests: write
                 │   читає найновіший verdict         ┌─ tripwire (regex по report+verdict)
                 │   gate: anomaly && should_open_issue│  dedupe (gh pr list --label alert-worker)
                 │   upload report+verdict ────────────┼─ sandboxed claude -p → фікс коду
                 └─────────────── open_pr=true ────────┤  check: protected files + git diff --check + npm ci/lint/build
                                                        └─ workflow (не модель) → git push + gh pr create --draft
                                                                                  → draft PR → людина мерджить
```

Хто який токен тримає:

| Компонент | Ранер | Права GitHub | Секрети | Пише в GitHub |
|---|---|---|---|---|
| watcher | VPS (контейнер) | немає токена | `ANTHROPIC_API_KEY` (opt-in) | ні |
| `detect` | VPS (self-hosted) | `contents: read` | немає | ні |
| `author-fix` | ubuntu-latest (ефемерна) | `contents: write`, `pull-requests: write` | `CLAUDE_CODE_OAUTH_TOKEN` | тільки draft PR |
| людина | — | merge | — | так, мерджить |

Жоден write-токен не з'являється на VPS. Watcher і `detect` тільки читають.

### Запуск

```bash
# з чекаута course-project (workflow уже в репозиторії)
gh workflow run alert-worker.yml
gh run watch

# найновіший verdict + report прямо з watcher-а (read-only, той самий прийом,
# що show-release-watch.sh)
scripts/latest-anomaly.sh /tmp/incident

# зручні обгортки
make -C modules/11-production/11.2-agent-on-duty alert-run  REPO=owner/course-project
make -C modules/11-production/11.2-agent-on-duty alert-show REPO=owner/course-project
```

Щоб побачити живий цикл, спершу спровокуй аномалію (тимчасово, на VPS):

```bash
# знизити поріг 5xx і перечитати правила без рестарту
sed -i 's/>= 0.05/>= 0.0001/' observability/prometheus/rules/app.yml
curl -X POST http://127.0.0.1:9090/-/reload
# або нагенеруй реальних 5xx навантаженням на застосунок
```

Після firing → watcher пише anomaly-verdict → `gh workflow run alert-worker.yml`
→ `detect` зелений (`open_pr=true`) → `author-fix` з реальним дифом → draft PR із
лейблом `alert-worker` і статусом Draft. **Поверни поріг назад** після демо.

### Чому watcher не змінюється

`server.mjs`, `verdict-schema.json`, `alertmanager.yml`, `release-watch.yml` і
`deploy-vps.yml` лишаються як були. Alert-worker нічого в них не переписує: він
лише **читає** те, що watcher уже поклав у `artifacts/`. Read-half і write-half
розв'язані навмисно.

### На що зважати

- **Protected `main` обов'язковий.** Draft PR — не захист сам по собі; захист —
  це required review + заборона push у `main` напряму. Увімкни branch protection
  і required approvals, інакше сенс draft-у губиться.
- **Дозвіл на PR від Actions.** У Settings → Actions увімкни «Allow GitHub Actions
  to create and approve pull requests», інакше `gh pr create` впаде.
- **AI ніколи не мерджить.** Модель не має мережі, `gh`, push і commit; draft PR
  публікує детермінований крок workflow, а не модель. Merge — рішення людини.
- **Захищені файли.** Після моделі workflow падає, якщо змінено `.github/`,
  `.claude/`, `.env`, `package*.json`, `Dockerfile` або `observability/`. Тобто
  агент не може «полагодити» алерт, послабивши власний поріг чи пісочницю.
- **Draft PR не тригерить deploy.** `deploy-vps` спрацьовує лише на push у `main`;
  push у гілку `agent/alert-*` дає draft PR і не запускає новий реліз. Петля не
  замикається сама.
- **Невдалий прогін ретраїться.** Якщо `author-fix` упав до відкриття PR
  (модель не знайшла безпечного фіксу, впав lint), наступний cron за 15 хв
  спробує знову — доки новий здоровий verdict не витіснить аномалію. Це не баг,
  а плата за детермінований планувальник; май на увазі бюджет.
- **Латентність cron.** `*/15` означає до 15 хв затримки; для миттєвого показу є
  `workflow_dispatch` (`gh workflow run`).

## Версії, перевірені 2026-07-13

| Компонент | Pin |
|---|---|
| `prom-client` | 15.1.3 |
| Prometheus | `prom/prometheus:v3.13.1` |
| Grafana OSS | `grafana/grafana:13.1.0` |
| Loki | `grafana/loki:3.7.3` |
| Alloy | `grafana/alloy:v1.17.1` |
| Alertmanager | `prom/alertmanager:v0.33.1` |
| Claude Code in watcher | 2.1.207 |

Не використовуємо `grafana/grafana-oss`: repository image зупинився на 12.4.
Не використовуємо `latest`.

## Локальна перевірка матеріалів

```bash
make -C modules/11-production/11.2-agent-on-duty verify
```

Старі `victim-app/`, `agent/` і root `compose.yml` залишені як historical
standalone demo попередньої редакції. Новий маршрут лекції використовує тільки
`course-project-files/` і реальний `course-project`.
