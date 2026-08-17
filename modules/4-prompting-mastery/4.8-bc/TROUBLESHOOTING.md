# TROUBLESHOOTING — демо 4.8-bc

Симптом → причина → фікс. Тексти помилок наведені дослівно: якщо ти прийшов сюди
пошуком по своєму терміналу, шукай саме свій рядок.

Перше, що варто зробити у будь-якій незрозумілій ситуації — з теки стейджа:

```bash
make doctor
```

Він перевіряє Docker і його демон, вільні порти, версію мови й активний venv,
і на кожну проблему друкує конкретну команду.

---

## Go / arch-lint

### `internal error: package "net/http" without types was imported from ...`

**Причина.** Стара версія `go-arch-lint` (наприклад v1.11.5) зібрана з
`golang.org/x/tools v0.17.0`, який не вміє читати export-дані сучасного Go.
Найгірше в цій поломці те, що лінтер повертав при цьому **нульовий** код:
`make arch-test` друкував помилку і вдавав успіх.

**Фікс.** У цьому демо два незалежні запобіжники, і обидва вже на місці:

1. Версія лінтера запінена в `Makefile` (`ARCH_LINT_VERSION ?= v1.17.0`)
   і запускається через `go run …@версія` — тобто вона завжди та, що написана.
2. `scripts/arch-test.sh` розпізнає цей клас падінь і виходить з **1**,
   а не з нуля.

Якщо ти все одно бачиш цей текст:

```bash
go version                       # потрібен Go 1.25+
go env GOTOOLCHAIN               # має бути auto (не local)
ARCH_LINT_VERSION=v1.17.0 make arch-test
```

### `go-arch-lint not installed; run: make arch-lint-install` — хоча установка пройшла успішно

**Причина.** Стара схема шукала бінар через `command -v go-arch-lint`, а
`go install` кладе його в `$(go env GOPATH)/bin`, якої в більшості систем немає
в `$PATH`. Виходило замкнене коло: установка «успішна», а тест каже «не встановлено».

**Фікс.** Уже виправлено: лінтер запускається через `go run`, у `$PATH` йому бути не треба.
Якщо ти бачиш це повідомлення — ти працюєш зі старою копією демо. Онови репозиторій.

### `go: github.com/fe3dback/go-arch-lint@v1.17.0 requires go >= 1.25.0; switching to go1.25.13`

Це не помилка. Твій Go старший за 1.25, і `GOTOOLCHAIN=auto` тихо тягне потрібний
тулчейн. Першому запуску потрібна мережа.

Якщо в тебе `GOTOOLCHAIN=local`, замість цього рядка буде відмова. Тоді:

```bash
go env -w GOTOOLCHAIN=auto     # або постав Go 1.25+
```

### Корпоративний проксі: `dial tcp: i/o timeout` на proxy.golang.org

```bash
go env -w GOPROXY=https://твій.внутрішній.проксі,direct
go env -w GOSUMDB=off          # якщо внутрішній проксі не віддає контрольні суми
```

Зовсім немає доступу до модулів і немає локального Go — є запасний шлях через образ:

```bash
make arch-test-docker
```

Образ `fe3dback/go-arch-lint` зібраний тільки під amd64: на Apple Silicon
він піде через емуляцію і буде помітно повільніший. Основний шлях — нативний.

### `make arch-test` зелений — а чи він узагалі щось перевіряє?

Правильне питання. Саме так виглядав зламаний лінтер. Перевір негативним контролем:

```bash
make arch-test-selftest        # ✓ Лінтер коректно ловить порушення.
```

Це окремий крихітний модуль у `scripts/archlint-selftest/`, де порушення
закладене навмисно. Якщо цей крок зелений — `arch-test` справді працює.

---

## Docker / Postgres

### `password authentication failed for user "demo"`

**Причина.** Майже завжди — на порту 5432 слухає **твій локальний Postgres**, а не
контейнер. З'єднання йде в нього, а користувача `demo` там немає. Креди в демо правильні.

**Фікс.** Візьми інший порт:

```bash
make db-up PGPORT=5433
make db-migrate PGPORT=5433
make run PGPORT=5433
```

Щоб не писати щоразу: `cp .env.example .env` і постав там `PGPORT=5433`
(цей файл читають і make, і docker compose).

`make doctor` ловить цю ситуацію заздалегідь і відрізняє «порт зайнятий чужим процесом»
від «порт зайнятий контейнером цього ж стейджа».

### `Error response from daemon: ... address already in use` / `bind: address already in use`

Те саме, що вище, але для HTTP-порту: `make run HTTP_PORT=8081`,
а смоук тоді `make smoke BASE_URL=http://localhost:8081`.

### `make db-down` (`docker compose down -v`) наче нічого не робить: дані лишаються

**Причина.** Образ `postgres:18` переїхав: кластер тепер у `/var/lib/postgresql/18/docker`,
а сам образ оголошує `VOLUME /var/lib/postgresql`. Том, змонтований у
`/var/lib/postgresql/data` (правильний шлях для образів ≤17), у 18-му вже нічого не тримає:
дані падають у шар контейнера. `down -v` витирає порожній том, а не базу.

**Фікс.** Уже виправлено: у `docker-compose.yml` том змонтований на батьківську теку
`/var/lib/postgresql`. Перевірити, що кластер дійсно всередині тому:

```bash
docker compose exec postgres ls /var/lib/postgresql/18/docker/PG_VERSION
```

Якщо ти копіюєш цей compose до себе і працюєш з образом ≤17 — там правильним
шляхом лишається `/var/lib/postgresql/data`.

### `relation "auth_users" already exists`

**Причина.** Ти накочуєш міграції на базу, де вони вже накочені. Класика — коли два
стейджі ділили один контейнер: до фіксу `go/stage-1-flat`, `ts/stage-1-flat` і
`py/stage-1-flat` мали однакове ім'я compose-проєкту (за назвою теки), тобто буквально
одну базу на трьох.

**Фікс.** Уже виправлено ключем `name: bc48-<мова>-s<номер>` у кожному compose.
Перевірити, що стейджі справді різні:

```bash
docker ps --format '{{.Names}}'
# bc48-go-s1-postgres-1
# bc48-py-s1-postgres-1
```

Якщо база все ж брудна — почати з чистої:

```bash
make db-down && make db-up && make db-migrate
```

### Контейнер піднявся, але міграції падають на «connection refused»

Postgres під час `initdb` слухає лише unix-сокет, і сокетна перевірка `pg_isready`
дає хибне «готовий». Тому healthcheck і цикл очікування ходять через TCP
(`pg_isready -h 127.0.0.1`), а `db-migrate` залежить від `db-up`. Якщо база не
підіймається за 60 секунд, `make db-up` сам покаже `docker compose logs --tail=40`.

### `Cannot connect to the Docker daemon`

Docker встановлений, але не запущений. Запусти Docker Desktop і дочекайся зеленого
статусу. `make doctor` перевіряє це окремо від наявності бінара.

---

## Python

### `ModuleNotFoundError: No module named 'psycopg2'`

**Причина.** DSN виду `postgresql://…` без явного драйвера змушує SQLAlchemy
**вгадувати**, і вона обирає psycopg2, якого в залежностях немає.

**Фікс.** Уже виправлено: `SYNC_DSN` і `alembic.ini` називають драйвер явно —
`postgresql+psycopg://`, а `migrations/env.py` нормалізує будь-який вхідний DSN
до psycopg 3. Якщо ти передаєш свій DSN — пиши драйвер явно:

```bash
make db-migrate SYNC_DSN=postgresql+psycopg://demo:demo@localhost:5433/demo
```

### `error: externally-managed-environment`

**Причина.** PEP 668: системний Python не дає ставити пакети глобально.

**Фікс.** Заведи venv у теці стейджа:

```bash
python3 -m venv .venv
source .venv/bin/activate      # Windows (Git Bash): source .venv/Scripts/activate
make install
```

`make doctor` вважає відсутній venv блокером саме тому, що без нього наступна
команда впаде з цим криптичним текстом.

### `make install` падає на збірці залежності з вихідників

Швидше за все, у тебе Python, новіший за перевірений діапазон (3.12–3.14): для нього
ще немає бінарних коліс. Перевір `python3 --version` і зроби venv на підтримуваній версії.

Верхня межа стоїть у `pyproject.toml` (`requires-python = ">=3.12,<3.15"`) свідомо.

### `lint-imports` каже, що не бачить конфіг

Конфіг має називатися `.importlinter` — це ім'я import-linter знаходить сам.
Якщо в твоїй копії лежить `importlinter.ini`, вона стара: у демо файл перейменований,
і `make arch-test` кличе `lint-imports` без прапорців.

---

## TypeScript

### `npm ci` падає: `The npm ci command can only install with an existing package-lock.json`

Лок-файл тепер закомічений у кожному з трьох `ts/` стейджів. Якщо його немає —
ти дивишся на стару копію демо. `npm install` теж працює, але тоді версії
залежностей у тебе і в лекції можуть розійтися.

### `npx` питає дозволу встановити пакет посеред роботи

Уже виправлено: Makefile кличе бінарі з `./node_modules/.bin`, а не через `npx`.
Якщо бачиш промпт — ти або в старій копії, або пропустив `make install`.

### `✗ Залежності не встановлені. Запусти: make install`

Саме те, що написано: у теці немає `node_modules`.

---

## Взагалі нічого не працює

1. `make doctor` — з теки стейджа.
2. `make clean` — прибрати контейнер і том, почати з чистого.
3. Візьми іншу мову: `ts/` і `py/` дзеркалять `go/` один-в-один, і потік команд
   ідентичний. Це нормальний обхідний шлях, а не поразка.
