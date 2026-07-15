# Lecture 11.2 — від порожньої VPS до першого deploy

Це основний практичний маршрут лекції. Ми купуємо VPS на прикладі Contabo,
готуємо Ubuntu, ставимо GitHub self-hosted runner і після `push` у `main`
розгортаємо реальний `course-project` через Docker Compose.

Моніторингу тут ще немає. Він навмисно винесений у наступну лекцію
[`11.2.1-agent-on-duty`](../11.2-agent-on-duty/README.md), щоб Prometheus,
Grafana і Loki не з'являлися раніше, ніж у застосунку з'являться метрики й логи.

## Що студент отримає

```text
ноутбук → GitHub → self-hosted runner на VPS → Docker Compose → course-project
```

- одна VPS з Ubuntu LTS;
- окремий Linux-користувач `deploy`;
- Docker Engine і Compose з офіційного Docker repository;
- GitHub runner як systemd service;
- production Dockerfile, persistent SQLite volume і `/api/health`;
- workflow, який робить build, deploy і deterministic healthcheck.

> `Runner` — не AI-агент. Це звичайний executor: він отримує job від GitHub і
> виконує команди workflow. AI у цій лекції працює до deploy: допомагає створити
> та перевірити інфраструктурні файли через skill `$prepare-vps-deploy`.

## 1. Купуємо Contabo VPS: три рішення

1. Відкрий [Contabo Cloud VPS](https://contabo.com/en/vps/), натисни
   `Get Started` біля найдешевшої VPS, якої достатньо для Docker build.
2. У configurator обери найближчий location, NVMe і **найновішу Ubuntu LTS,
   яку показує форма**. На момент перевірки матеріалів це Ubuntu 26.04 LTS;
   якщо її ще немає в конкретному location — Ubuntu 24.04.4 LTS.
3. Задай новий `root` password, одразу збережи його в password manager,
   заверши оплату. Після provisioning випиши IPv4 сервера з Customer Panel.

📸 Для запису: `01-contabo-plan.png`, `02-contabo-os.png`,
`03-contabo-server-ip.png`. Не показуй пароль, email, customer ID або payment data.

## 2. Перший SSH-вхід

На своєму комп'ютері:

```bash
ssh root@SERVER_IP
```

- `ssh` відкриває зашифровану shell-сесію на іншій машині;
- `root` — початковий administrator Linux;
- `@SERVER_IP` вказує, до якого сервера під'єднатися;
- на перший fingerprint відповідаємо `yes`, якщо IP збігається з Contabo Panel;
- пароль під час введення не відображається — це нормальна поведінка terminal.

Перевіряємо, куди потрапили:

```bash
whoami
hostname
cat /etc/os-release
```

`whoami` має повернути `root`; `hostname` показує ім'я сервера;
`/etc/os-release` — встановлений Linux і його версію.

## 3. Оновлюємо Ubuntu

```bash
apt update
apt full-upgrade -y
apt install -y ca-certificates curl git ufw
```

- `apt` — пакетний менеджер Ubuntu;
- `apt update` лише оновлює список доступних пакетів;
- `apt full-upgrade` встановлює оновлення і за потреби коректно змінює залежності;
- `-y` автоматично відповідає `yes` на підтвердження;
- `ca-certificates` потрібен для перевірки HTTPS-сертифікатів;
- `curl` завантажує дані по HTTP(S), `git` працює з repository;
- `ufw` означає **Uncomplicated Firewall** — простий інтерфейс до firewall Linux.

Якщо Ubuntu просить reboot після оновлення:

```bash
reboot
```

SSH розірветься. Почекай приблизно хвилину і під'єднайся ще раз.

## 4. Ставимо актуальний Docker з офіційного repository

Ubuntu repository часто містить старішу збірку Docker. Тому додаємо офіційний
Docker apt repository за [інструкцією Docker](https://docs.docker.com/engine/install/ubuntu/):

```bash
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo \"${UBUNTU_CODENAME:-$VERSION_CODENAME}\") stable" \
  > /etc/apt/sources.list.d/docker.list

apt update
apt install -y docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin
```

Що тут відбулося:

- `install -d` створив каталог для ключів; `-m 0755` задав права;
- `curl -f` завершується помилкою при HTTP error, `-sS` прибирає progress, але
  лишає errors, `-L` дозволяє redirect;
- GPG key дає `apt` змогу перевірити, що пакети підписав Docker;
- `dpkg --print-architecture` підставляє `amd64` або `arm64`;
- рядок з `/etc/os-release` підставляє codename нашої Ubuntu;
- `docker-ce` — engine, `containerd.io` — runtime,
  `docker-buildx-plugin` — сучасний builder, `docker-compose-plugin` — команда
  `docker compose`.

Не копіюємо конкретні apt build numbers: repository сам дає актуальний stable
build для обраної Ubuntu. Перевіряємо:

```bash
docker version
docker compose version
```

## 5. Чому `systemctl enable --now docker`

```bash
systemctl enable --now docker
systemctl status docker --no-pager
```

`systemctl` керує сервісами `systemd`, тобто програмами, які Linux запускає у
background. `enable` додає Docker в autostart після reboot, а `--now` запускає
його одразу. `status` показує поточний стан; `--no-pager` друкує результат у
terminal і не відкриває окремий viewer. Очікуємо `active (running)`.

## 6. Створюємо користувача `deploy`

```bash
adduser --disabled-password --gecos "" deploy
usermod -aG docker deploy
su - deploy
docker run --rm hello-world
```

- `adduser` створює home directory `/home/deploy`;
- `--disabled-password` забороняє password-login для цього account;
- `--gecos ""` пропускає питання про повне ім'я й телефон;
- `usermod -aG docker deploy` додає користувача в supplementary group `docker`:
  `-a` означає append, `-G` — список додаткових groups;
- `su - deploy` відкриває login shell користувача `deploy`;
- `docker run --rm hello-world` запускає test container і видаляє його після
  завершення завдяки `--rm`.

> [!warning] Docker group майже дорівнює root
> Людина або workflow з доступом до Docker socket може отримати повний контроль
> над VPS. Для уроку використовуй окрему VPS, trusted private repository,
> protected `main` і review змін у `.github/workflows/`.

### Додаємо SSH key для `deploy`

`--disabled-password` вимкнув password-login, тому даємо `deploy` доступ через
public key. На ноутбуці створи key, якщо його ще немає:

```bash
ssh-keygen -t ed25519 -C "course-vps"
cat ~/.ssh/id_ed25519.pub
```

`ssh-keygen` створює private key у `~/.ssh/id_ed25519` і public key з суфіксом
`.pub`. Private key нікуди не копіюємо. Скопіюй один рядок public key.

На VPS у root shell:

```bash
install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
printf '%s\n' 'PASTE_PUBLIC_KEY_HERE' \
  > /home/deploy/.ssh/authorized_keys
chown deploy:deploy /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys
```

`authorized_keys` перелічує public keys, яким дозволений вхід. Каталог має
права `700`, файл — `600`; інакше SSH навмисно може відмовитися їх читати.
Перевір з нового terminal на ноутбуці: `ssh deploy@SERVER_IP`.

## 7. Вмикаємо firewall без втрати SSH

Повертаємося в root shell командою `exit`, потім:

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw --force enable
ufw status verbose
```

Спочатку дозволяємо `OpenSSH`, і лише потім вмикаємо firewall — інакше можемо
закрити власну SSH-сесію. `80/tcp` — HTTP для застосунку. `--force` прибирає
interactive confirmation, а `status verbose` показує активні правила.

## 8. Ставимо GitHub self-hosted runner

У GitHub repository відкрий:

`Settings → Actions → Runners → New self-hosted runner → Linux → x64`

Повернися до користувача `deploy` (`su - deploy`) і **скопіюй команди з цього
екрана GitHub**: download, checksum, extract і `./config.sh`. GitHub підставляє
актуальну версію runner і одноразовий registration token.

На питання configurator відповідай:

| Поле | Значення |
|---|---|
| Runner group | `Default` |
| Runner name | `contabo-prod-1` |
| Additional labels | `course-vps` |
| Work folder | Enter, тобто `_work` |

Після `./config.sh` ставимо runner як service:

```bash
sudo ./svc.sh install deploy
sudo ./svc.sh start
sudo ./svc.sh status
```

Якщо для `deploy` ще не налаштовано `sudo`, виконай ці три команди з root shell
без `sudo` у каталозі `/home/deploy/actions-runner`.

- `svc.sh install deploy` створює unit для `systemd` від імені `deploy`;
- `start` запускає runner зараз;
- `status` має показати running;
- runner сам опитує GitHub через outbound HTTPS `443`, тому inbound port для
  GitHub не відкриваємо.

📸 Для запису: `04-runner-commands.png`, `05-runner-idle.png`. Registration
token обов'язково замалюй.

### Навіщо runner стоїть на тій самій VPS

Job виконує `docker compose` локально: не потрібні SSH private key, IP secret і
другий network hop. Це найкоротший навчальний шлях. Ціна простоти — workflow
отримує високі права на production machine. Тому deploy job запускається лише
з trusted `main`, не з `pull_request`.

## 9. Додаємо production-файли в `course-project`

Увесь copy-paste комплект лежить у [`course-project-files`](course-project-files/).
З кореня `agentic-engineering-course`:

```bash
modules/11-production/11.2-vps-deploy/apply-to-course-project.sh \
  /path/to/course-project
```

Скрипт:

1. копіює `Dockerfile.production`, Compose, health route, workflow і skill;
2. змінює `DB_PATH`, щоб SQLite жила в Docker volume;
3. дозволяє commit файлу `.env.vps.example`, але не `.env.vps`;
4. не запускає deploy і не торкається VPS.

Переглянь зміни перед commit:

```bash
cd /path/to/course-project
git status --short
git diff --check
docker compose --env-file .env.vps.example -f compose.vps.yml config
npm run build
```

`git status --short` показує змінені файли; `git diff --check` шукає whitespace
errors; `compose ... config` розгортає і перевіряє YAML без запуску containers;
`npm run build` доводить, що Next.js production build компілюється.

## 10. Перший deploy через GitHub Actions

Workflow [deploy-vps.yml](course-project-files/.github/workflows/deploy-vps.yml)
запускається після push у `main` або вручну через `Run workflow`:

1. `checkout` кладе код у runner work directory;
2. `docker compose up -d --build --remove-orphans` збирає image і замінює app;
3. `-d` залишає container у background;
4. `--build` збирає image з нового commit;
5. `--remove-orphans` видаляє старі services, яких уже немає в Compose;
6. `curl --fail` перевіряє `/api/health`; HTTP 4xx/5xx робить step червоним;
7. `docker compose ps` показує фінальний стан.

Відкрий `http://SERVER_IP`. Додай meme, повтори deploy і переконайся, що meme
не зник: SQLite зберігається в named volume `course-project-data`.

> [!danger] Не запускай `docker compose down -v`
> `-v` видалить named volume разом із production SQLite data.

## Де тут AI-агент

| Учасник | Роль | Чого не робить |
|---|---|---|
| GitHub Actions | вирішує, коли запускати job | не виконує job сам |
| self-hosted runner | виконує shell-команди на VPS | не аналізує результат як AI |
| `$prepare-vps-deploy` | перевіряє infra-файли до merge | не має SSH і не деплоїть сам |
| deterministic healthcheck | приймає рішення pass/fail | не пояснює складні аномалії |

У наступній лекції AI з'явиться **після** deterministic monitoring: він отримає
обмежений release report, пояснить аномалію, але не матиме Docker socket і не
робитиме automatic rollback.

## Версії, перевірені 2026-07-13

| Компонент | Версія/правило |
|---|---|
| Ubuntu | 26.04 LTS; fallback 24.04.4 LTS |
| GitHub Actions runner | UI GitHub; current release 2.335.1 |
| Docker Engine | 29.6.1 через stable apt repository |
| Docker Compose | 5.3.1 через `docker-compose-plugin` |
| Node image | `node:24.17.0-bookworm-slim` |
| `actions/checkout` | `v7.0.0`, pinned by full commit SHA |

Не використовуємо `latest`. Docker apt build numbers не pin-имо: вони залежать
від Ubuntu codename та architecture.

## Перевірка матеріалів лекції

```bash
make -C modules/11-production/11.2-vps-deploy verify
```

Команда не купує VPS і не запускає deploy. Вона перевіряє shell, Compose,
workflow guardrails і структуру skill.
