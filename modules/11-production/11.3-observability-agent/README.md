# Lecture 11.3 — метрики, логи й AI-черговий після deploy

Це повний студентський набір до лекції 11.3. Матеріал самої лекції не потрібен:
усі файли, команди, перевірки та дві демонстрації є тут.

Ми додаємо лише найменшу систему, яка показує повний production loop:

```text
push main
   ↓
deploy-vps → app на VPS → /api/metrics → Prometheus → Grafana
                    └──→ JSON stdout → Docker logs
   ↓
release-watch: Python раз на хвилину читає 3 metrics і свіжі error logs
   ├── healthy → workflow green
   └── anomaly → report.json → Telegram/stub → Claude → draft PR → human review
```

Тут навмисно немає Loki, Alloy та Alertmanager. Для однієї навчальної VPS
Prometheus зберігає metrics, Grafana їх малює, а Docker уже зберігає logs.

## Що лежить у цій теці

| Файл | Для чого він |
|---|---|
| [`lib/observability.ts`](course-project-files/lib/observability.ts) | Counter, Histogram і один JSON log на request |
| [`app/api/metrics/route.ts`](course-project-files/app/api/metrics/route.ts) | endpoint `/api/metrics` для Prometheus |
| [`app/api/memes/route.ts`](course-project-files/app/api/memes/route.ts) | instrumented GET і POST `/api/memes` |
| [`app/api/memes/random/route.ts`](course-project-files/app/api/memes/random/route.ts) | instrumented GET `/api/memes/random` |
| [`observability/prometheus.yml`](course-project-files/observability/prometheus.yml) | Prometheus забирає metrics раз на 15 секунд |
| [`compose.observability.yml`](course-project-files/compose.observability.yml) | рівно два нові services: Prometheus і Grafana |
| [`deploy-vps.yml`](course-project-files/.github/workflows/deploy-vps.yml) | deploy app і observability двома Compose-файлами |
| [`watch_release.py`](course-project-files/scripts/watch_release.py) | простий 1–20-хвилинний deterministic watcher |
| [`release-watch.yml`](course-project-files/.github/workflows/release-watch.yml) | watch → Telegram/stub → artifact → fix-agent → draft PR |
| [`.env.observability.example`](course-project-files/.env.observability.example) | довідкове тестове значення; у `course-project` його копіювати не потрібно |

## Результат кожної фази

Не переходь далі, поки не побачив артефакт поточної фази.

| Фаза | Видимий checkpoint |
|---|---|
| 1. Код застосунку | `/api/metrics` повертає Counter/buckets, terminal показує JSON logs |
| 2. Збір сигналів | Prometheus показує `up = 1`, Grafana має 3 panels, Docker віддає log |
| 3. Post-deploy loop | healthy rehearsal зелений; anomaly дає stub, report і draft PR |

## Передумови

Спочатку заверши
[`11.2-vps-deploy`](../11.2-vps-deploy/README.md). Має бути:

- `course-project` уже працює на VPS;
- у repository є `compose.vps.yml`;
- GitHub workflow `deploy-vps` зелений;
- self-hosted runner має label `course-vps`;
- локально встановлені `git`, `node`, `npm`, `docker`, `gh`;
- GitHub CLI авторизований: `gh auth status` завершується успішно.

У прикладах заміни `SERVER_IP` на IP своєї VPS. Не вставляй символи `<` і `>`.

## Крок 0. Задаємо шляхи й перевіряємо старт

На ноутбуці:

```bash
export COURSE_REPO="$HOME/sources/agentic-engineering-course"
export APP_REPO="$HOME/sources/course-project"
export KIT="$COURSE_REPO/modules/11-production/11.3-observability-agent/course-project-files"

test -f "$KIT/lib/observability.ts"
test -f "$KIT/scripts/watch_release.py"
test -f "$APP_REPO/compose.vps.yml"
test -f "$APP_REPO/package.json"
echo $?
```

Очікуй `0`. Якщо бачиш `1`, один зі шляхів неправильний — виправ його зараз.

Перевір робоче дерево й створи branch:

```bash
cd "$APP_REPO"
git status --short
git switch main
git pull --ff-only
git switch -c lecture/11.3-observability
```

Перед створенням branch `git status --short` має бути порожнім.

## Яким шляхом ідемо

Для першого проходження використовуй ручні Кроки 1–9 нижче: так видно, навіщо
потрібен кожен файл. Не запускай apply-script паралельно з ручним шляхом — інакше
ти скопіюєш ті самі файли двічі.

Після першого проходження весь kit можна повторно застосувати однією командою.
Вона копіює одразу обидві фази, встановлює `prom-client` і працює лише поверх
чистого, незміненого результату 11.2:

```bash
cd "$COURSE_REPO/modules/11-production/11.3-observability-agent"
make verify
make apply TARGET="$APP_REPO"
cd "$APP_REPO"
git status --short
python3 -c 'from pathlib import Path; compile(Path("scripts/watch_release.py").read_text(), "scripts/watch_release.py", "exec")'
npm run lint
npm run build
```

Якщо apply-script каже, що `deploy-vps.yml` змінений, нічого не перетирай.
Пройди ручні кроки нижче й перенеси нову Compose-команду у свій workflow. Навіть
після успішного apply все одно потрібно створити secret на VPS і налаштувати
GitHub permissions до merge — script навмисно не змінює зовнішні системи.

## Крок 1. Додаємо metrics і JSON logs руками

Мета: застосунок сам рахує requests і duration. Prometheus ще не запускаємо.

Встановлюємо одну dependency:

```bash
cd "$APP_REPO"
npm install --save-exact prom-client@15.1.3
```

Створюємо теки й копіюємо чотири готові файли:

```bash
mkdir -p lib app/api/metrics app/api/memes/random

cp "$KIT/lib/observability.ts" lib/observability.ts
cp "$KIT/app/api/metrics/route.ts" app/api/metrics/route.ts
cp "$KIT/app/api/memes/route.ts" app/api/memes/route.ts
cp "$KIT/app/api/memes/random/route.ts" app/api/memes/random/route.ts
```

Що змінилося:

- `Counter` рахує requests за `method`, `route`, `status`;
- `Histogram` зберігає duration buckets для p95;
- `/api/metrics` віддає Prometheus text format;
- `observeRequest(...)` пише один JSON object у stdout.

Подивися реальний diff:

```bash
git status --short
git diff -- app/api/memes/route.ts
git diff -- app/api/memes/random/route.ts
sed -n '1,240p' lib/observability.ts
```

Не додавай у labels user ID, email, query parameters або повний URL. Інакше
кількість time series ростиме без межі. У logs не пиши body, cookies, tokens і
authorization headers.

## Крок 2. Копіюємо Prometheus, Grafana і deploy workflow

Мета: Prometheus зберігає історію metrics, Grafana показує графіки. Logs і далі
зберігає Docker — нового log-сервісу немає.

```bash
cd "$APP_REPO"
mkdir -p observability .github/workflows

cp "$KIT/observability/prometheus.yml" observability/prometheus.yml
cp "$KIT/compose.observability.yml" compose.observability.yml
```

Перед заміною workflow подивися різницю:

```bash
diff -u \
  .github/workflows/deploy-vps.yml \
  "$KIT/.github/workflows/deploy-vps.yml" || true
```

Якщо твій `deploy-vps.yml` — результат 11.2 без власних кроків, копіюй готовий:

```bash
cp "$KIT/.github/workflows/deploy-vps.yml" \
  .github/workflows/deploy-vps.yml
```

Якщо у workflow є власні кроки, збережи їх і заміни тільки deploy-команду на:

```yaml
- name: Build and deploy app plus observability
  env:
    RELEASE_SHA: ${{ github.sha }}
  run: |
    docker compose \
      --env-file "$HOME/.config/course-project/observability.env" \
      -f compose.vps.yml \
      -f compose.observability.yml \
      up -d --build --remove-orphans
```

Чому тут два `-f`: перший файл описує app із 11.2, другий додає Prometheus і
Grafana. `--remove-orphans` тепер бачить усі три services й не зупиняє monitoring.

## Крок 3. Перевіряємо метрики й логи локально

Спочатку syntax/build:

```bash
cd "$APP_REPO"
npm run lint
npm run build
```

Запусти app:

```bash
npm run dev
```

Не закривай цей terminal. У другому terminal:

```bash
curl --silent http://localhost:3000/api/memes/random > /dev/null
curl --silent http://localhost:3000/api/memes/random > /dev/null

curl --silent http://localhost:3000/api/metrics \
  | grep -E 'course_project_http_requests_total|course_project_http_request_duration_seconds_bucket' \
  | head -10
```

Очікуй Counter і Histogram buckets. У terminal із `npm run dev` очікуй два
рядки приблизно такого вигляду:

```json
{"level":"info","event":"request_completed","method":"GET","route":"/api/memes/random","status":200,"duration_ms":7,"release":"local"}
```

Тепер перевіряємо, що два Compose-файли склеюються:

```bash
export GRAFANA_ADMIN_PASSWORD=temporary-validation-password

docker compose \
  -f compose.vps.yml \
  -f compose.observability.yml \
  config --quiet

echo $?
```

Очікуй порожній output і `0`. Це checkpoint фази 1.

## Крок 4. Один раз готуємо VPS

Package installation робимо з root-session. На ноутбуці:

```bash
ssh root@SERVER_IP
apt update
apt install -y jq openssl python3
exit
```

Тепер login під `deploy` і створюємо Grafana password поза repository:

```bash
ssh deploy@SERVER_IP

install -d -m 700 "$HOME/.config/course-project"
umask 077
printf 'GRAFANA_ADMIN_PASSWORD=%s\n' "$(openssl rand -hex 16)" \
  > "$HOME/.config/course-project/observability.env"

chmod 600 "$HOME/.config/course-project/observability.env"
cut -d= -f1 "$HOME/.config/course-project/observability.env"
exit
```

Очікуй лише назву `GRAFANA_ADMIN_PASSWORD`. Не друкуй password у відео, issue,
commit або Actions log.

## Крок 5. Публікуємо перший PR і запускаємо stack

На ноутбуці:

```bash
cd "$APP_REPO"
git status --short
git diff --stat

git add \
  app/api/metrics \
  app/api/memes \
  lib/observability.ts \
  observability/prometheus.yml \
  compose.observability.yml \
  .github/workflows/deploy-vps.yml \
  package.json package-lock.json

git commit -m "feat: add minimal production observability"
git push -u origin lecture/11.3-observability
gh pr create --fill
```

Перевір PR і merge його. Потім знайди deploy run:

```bash
gh run list --workflow=deploy-vps.yml --limit=3
```

Скопіюй ID найновішого run:

```bash
DEPLOY_RUN_ID=PASTE_ID_HERE
gh run watch "$DEPLOY_RUN_ID"
gh run view "$DEPLOY_RUN_ID" --json conclusion,url --jq '{conclusion,url}'
```

Очікуй `conclusion: success`.

## Крок 6. Відкриваємо Prometheus і Grafana

Admin ports слухають лише `127.0.0.1` VPS. Відкриваємо SSH tunnel:

```bash
ssh \
  -L 9090:127.0.0.1:9090 \
  -L 3001:127.0.0.1:3001 \
  deploy@SERVER_IP
```

Не закривай session.

Prometheus:

1. Відкрий `http://localhost:9090`.
2. Виконай `up{job="course-project"}`.
3. Очікуй value `1`.

Grafana:

1. У session на VPS прочитай password командою нижче. Не показуй його в записі.

   ```bash
   cut -d= -f2- "$HOME/.config/course-project/observability.env"
   ```

2. Відкрий `http://localhost:3001`.
3. Login `admin`, password — значення з попередньої команди.
4. `Connections → Data sources → Add data source → Prometheus`.
5. URL: `http://prometheus:9090`.
6. Натисни `Save & test` — очікуй success.
7. `Dashboards → New → New dashboard → Add visualization`.
8. Створи три panels.

Panel `UP`:

```promql
up{job="course-project"}
```

Panel `5xx / 5m`:

```promql
sum(increase(course_project_http_requests_total{status=~"5.."}[5m])) or vector(0)
```

Panel `p95 latency`:

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(course_project_http_request_duration_seconds_bucket[5m])
  )
)
```

Збережи dashboard як `Course Project / Production`.

## Крок 7. Доводимо, що Docker уже тримає logs

З ноутбука зроби звичайний request:

```bash
curl --silent http://SERVER_IP/api/memes/random > /dev/null
```

На VPS:

```bash
cd "$HOME/actions-runner/_work/course-project/course-project"

docker compose \
  --env-file "$HOME/.config/course-project/observability.env" \
  -f compose.vps.yml \
  -f compose.observability.yml \
  logs --since 2m --tail 20 --no-color --no-log-prefix app
```

Очікуй JSON із route `/api/memes/random` і status `200`. Ми нічого нового не
запустили: `docker compose logs` лише прочитав stdout, який Docker уже зберіг.

Тепер той самий error-filter, який використовує watcher:

```bash
docker compose \
  --env-file "$HOME/.config/course-project/observability.env" \
  -f compose.vps.yml \
  -f compose.observability.yml \
  logs --since 2m --tail 100 --no-color --no-log-prefix app \
  | grep -E '"level":"error"|"status":5[0-9][0-9]' || true
```

На healthy release output порожній. `|| true` означає, що відсутність error
lines — нормальний результат, а не падіння shell-команди.

## Крок 8. Додаємо Python watcher і workflow

Повернися до оновленого `main` і створи другий branch:

```bash
cd "$APP_REPO"
git switch main
git pull --ff-only
git switch -c lecture/11.3-release-watch

mkdir -p scripts .github/workflows
cp "$KIT/scripts/watch_release.py" scripts/watch_release.py
cp "$KIT/.github/workflows/release-watch.yml" \
  .github/workflows/release-watch.yml
chmod +x scripts/watch_release.py
```

Перевір syntax:

```bash
python3 -c 'from pathlib import Path; compile(Path("scripts/watch_release.py").read_text(), "scripts/watch_release.py", "exec")'
git diff --check
git status --short
```

Watcher не викликає AI щохвилини. Він детерміновано перевіряє:

| Умова | `reason` у report |
|---|---|
| `up != 1` | `app_not_up` |
| 5xx за хвилину `> 0` | `new_5xx` |
| p95 `> 1` second | `p95_over_one_second` |
| є error log | `error_log_detected` |
| Prometheus або Docker недоступні | `signals_unavailable` |

Результат завжди один файл `report.json`. Exit `0` означає healthy, exit `42`
означає anomaly. Claude стартує лише після exit `42`.

## Крок 9. Один раз налаштовуємо GitHub

У GitHub repository відкрий:

`Settings → Actions → General → Workflow permissions`

Увімкни:

- `Read and write permissions`;
- `Allow GitHub Actions to create and approve pull requests`.

Додай token для Claude Code:

```bash
cd "$APP_REPO"
gh secret set CLAUDE_CODE_OAUTH_TOKEN
```

Terminal попросить значення приховано.

Telegram можна не налаштовувати. Без двох secrets workflow покаже безпечну
заглушку `[telegram stub] ...`. Для реального bot:

```bash
gh secret set TELEGRAM_BOT_TOKEN
gh secret set TELEGRAM_CHAT_ID
```

Публікуємо другий PR:

```bash
git add scripts/watch_release.py .github/workflows/release-watch.yml
git commit -m "feat: watch releases for twenty minutes"
git push -u origin lecture/11.3-release-watch
gh pr create --fill
```

Перевір і merge PR. Відтепер успішний `deploy-vps` автоматично запускає
`release-watch` на 20 хвилин.

## Демонстрація 1. Healthy release за дві хвилини

Ручний режим нічого не deploy-ить. Він перевіряє commit, який уже працює:

```bash
cd "$APP_REPO"
git switch main
git pull --ff-only

gh workflow run release-watch.yml \
  --ref main \
  -f release_sha="$(git rev-parse HEAD)" \
  -f watch_minutes=2
```

Знаходимо run і спостерігаємо:

```bash
RUN_ID="$(gh run list \
  --workflow=release-watch.yml \
  --limit=1 \
  --json databaseId \
  --jq '.[0].databaseId')"

gh run watch "$RUN_ID"
gh run view "$RUN_ID" --json conclusion,url --jq '{conclusion,url}'
```

Очікуй приблизно:

```text
minute 1/2: {'up': 1.0, 'errors_1m': 0.0, 'p95_seconds': 0.0}, error_logs=0
minute 2/2: {'up': 1.0, 'errors_1m': 0.0, 'p95_seconds': 0.08}, error_logs=0
report=.../release-watch/report.json
```

`conclusion` має бути `success`, а job `author-fix` — `skipped`. `p95=0.0` може
означати, що у короткому вікні не було traffic; це fallback, а не реальна нульова
latency.

## Демонстрація 2. Anomaly → stub → report → draft PR

Роби це лише на власній навчальній VPS.

Створюємо branch із одним видимим bug:

```bash
cd "$APP_REPO"
git switch main
git pull --ff-only
git switch -c demo/11.3-broken-release
```

Відкрий `app/api/memes/random/route.ts` і всередині callback
`observeRequest(...)`, перед `const template`, додай:

```ts
throw new Error("DEMO_RELEASE_BUG");
```

Перевір і опублікуй:

```bash
git diff -- app/api/memes/random/route.ts
git add app/api/memes/random/route.ts
git commit -m "demo: introduce visible release bug"
git push -u origin demo/11.3-broken-release
gh pr create --fill
```

Перевір і merge demo PR. Health endpoint не зламаний, тому `deploy-vps` буде
green, а `release-watch` стартує автоматично.

Створи десять реальних 500 responses:

```bash
for attempt in {1..10}; do
  status="$(curl --silent --output /dev/null \
    --write-out '%{http_code}' \
    http://SERVER_IP/api/memes/random)"
  printf 'attempt=%s status=%s\n' "$attempt" "$status"
  sleep 2
done
```

Очікуй `status=500`. Дивимося найновіший watcher run:

```bash
RUN_ID="$(gh run list \
  --workflow=release-watch.yml \
  --limit=1 \
  --json databaseId \
  --jq '.[0].databaseId')"

gh run watch "$RUN_ID"
```

Очікуй:

```text
minute 1/20: {'up': 1.0, 'errors_1m': 10.0, 'p95_seconds': 0.02}, error_logs=10
[telegram stub] course-project: release anomaly: new_5xx; run ...
```

Watcher завершується одразу після anomaly, не чекає всі 20 хвилин. Далі workflow:

1. upload-ить лише bounded `report.json`;
2. запускає Claude на окремій GitHub VM;
3. забороняє агенту змінювати workflows, monitoring, scripts і dependencies;
4. перевіряє реальний `git status`, diff, lint і build;
5. сам створює draft PR. Модель не push-ить і не merge-ить.

Знайди PR:

```bash
gh pr list \
  --state open \
  --search 'agent: fix post-deploy anomaly in:title' \
  --json number,title,isDraft,url \
  --jq '.[0]'
```

Очікуй `isDraft: true`. Diff має прибрати тільки
`throw new Error("DEMO_RELEASE_BUG")`. Переглянь і merge PR руками. Новий deploy
знову запустить watcher; тепер він має пройти healthy path.

## Що відбувається під капотом

```text
GitHub deploy success
        │
        ▼
self-hosted VPS job, contents:read
        │
        ├─ Prometheus query: up
        ├─ Prometheus query: 5xx / 1m
        ├─ Prometheus query: p95 / 5m
        └─ Docker logs: last 70s, max 40 error lines
                 │
          deterministic thresholds
             │             │
          healthy        anomaly
             │             │
          success       report.json
                           │
                    Telegram або stub
                           │ artifact
                           ▼
                GitHub-hosted write job
                           │
                    Claude edits checkout
                           │
              workflow verifies real diff
                           │
                        draft PR
                           │
                     human review
```

Головна межа: production data є недовіреним evidence, а не командою. Read-job на
VPS не має write-token. Write-job отримує короткий report і чистий checkout, а
публікує код лише workflow після власних перевірок.

## Типові проблеми

### `test` повернув `1`

Перевір шляхи:

```bash
printf 'COURSE_REPO=%s\nAPP_REPO=%s\nKIT=%s\n' \
  "$COURSE_REPO" "$APP_REPO" "$KIT"
```

### Prometheus показує `up = 0`

На VPS:

```bash
cd "$HOME/actions-runner/_work/course-project/course-project"
docker compose \
  --env-file "$HOME/.config/course-project/observability.env" \
  -f compose.vps.yml \
  -f compose.observability.yml \
  ps

docker compose \
  --env-file "$HOME/.config/course-project/observability.env" \
  -f compose.vps.yml \
  -f compose.observability.yml \
  logs --tail 100 prometheus app
```

### Grafana не відкривається

Переконайся, що SSH tunnel ще працює, а потім:

```bash
curl --silent --show-error http://localhost:3001/api/health | jq
```

### `release-watch` одразу дає `signals_unavailable`

У Actions log прочитай `recent_error_logs` у report. Найчастіше відсутній
`observability.env`, не встановлений `python3`/`jq`, або Compose запущений не з
двома файлами.

### Agent не створив PR

Перевір у такому порядку:

1. `author-fix` був `skipped` — watcher не побачив anomaly.
2. `Agent did not change any files` — evidence недостатньо; це безпечна зупинка.
3. Actions не може створювати PR — увімкни permissions із Кроку 9.
4. Немає `CLAUDE_CODE_OAUTH_TOKEN` — додай secret.

## Перевірка матеріалів курсу

Із цієї теки:

```bash
make verify
```

Очікуй:

```text
OK: Lecture 11.3 materials are complete and syntactically valid.
```

Ця команда перевіряє наявність усіх distributed files, Bash, Python і YAML
syntax, а також підтверджує, що в мінімальний kit випадково не повернулися Loki,
Alloy або Alertmanager.
