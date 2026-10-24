# Claude Code Rules: демо

Демо-проєкт до уроку **Claude Code Rules** з курсу «Agentic Engineering». Той самий проєкт, що у відео, з трьома відмінностями. Кореневий файл називається `AGENTS.md`, у відео це `CLAUDE.md`. У frontmatter правил немає поля `description`, бо Claude Code його не читає. У `.claude/settings.json` додано хук журналу завантажень.

## Що це

Невеликий fullstack-монорепо: Go API, React і Terraform. Конвенції кожної частини лежать окремими правилами в `.claude/rules/`, а кореневий `AGENTS.md` лише показує, де яке правило.

Код тут не збирається і не запускається: `go.mod`, `package.json` і Terraform state у демо немає. Файли потрібні для того, щоб у кожного правила з `paths` був справжній файл, на якому воно спрацює. Деякі файли, які згадують правила (`src/styles/tokens.css`, `infra/backend.tf`), у демо відсутні навмисно: правила описують конвенції більшого проєкту.

```text
AGENTS.md                        кореневий файл: роутер по правилах
.claude/
  settings.json                  claudeMdExcludes і хук InstructionsLoaded
  rules/
    general.md                   без paths: вантажиться на старті кожної сесії
    backend/api.md               paths: api/**/*.go
    backend/database.md          paths: **/migrations/**, **/models/**
    frontend/react.md            paths: src/components/**/*.tsx, src/pages/**/*.tsx
    frontend/styling.md          paths: **/*.css, **/*.scss
    infra/terraform.md           paths: infra/**/*.tf
api/
  main.go                        під api.md
  handlers/users.go              під api.md
  migrations/001_init.sql        під database.md
src/
  components/Button.tsx          під react.md
  pages/Home.tsx                 під react.md
  styles/button.css              під styling.md
infra/main.tf                    під terraform.md
```

У frontmatter правил стоїть лише `paths`. Claude Code читає з frontmatter тільки це поле. `description:` нічого не дає. Правило, у якому замість `paths` стоїть `globs:` (як у Cursor) чи `applyTo:` (як у Copilot), вантажиться в кожну сесію.

## Як запустити

Потрібен лише Claude Code свіжої версії. `AGENTS.md` без `CLAUDE.md` Claude Code читає лише в нових версіях, а на старих правило з `paths` вантажилось тільки через інструмент Read.

```bash
git clone https://github.com/genkovich/agentic-engineering-course-public   # якщо репозиторію курсу ще немає
cd agentic-engineering-course-public/modules/4-prompting-mastery/4.5-rules
claude
```

Якщо репозиторій курсу вже клонували, зробіть у ньому `git pull` і просто перейдіть у теку. Запускайте `claude` саме з цієї теки: шляхи в `paths` рахуються від теки, де лежить `.claude`.

Якщо Claude Code спитає, чи довіряєте ви теці, погодьтесь: у `.claude/settings.json` лежить хук журналу, і налаштування проєкту працюють лише в теці, якій ви довіряєте.

## Що перевірити

### 1. Старт сесії

Одразу після запуску введіть `/context`. У Memory files будуть `AGENTS.md` і `.claude/rules/general.md`, а також ваші особисті файли з `~/.claude/`, якщо вони є. Правил з `paths` там немає, бо Claude ще не читав жодного файла під їхні glob. `/memory` для перевірки не підходить: правила з `paths` там не буде ніколи.

Якщо `AGENTS.md` у Memory files немає, пошукайте `CLAUDE.md` у теках вище: у теці, куди ви клонуєте проєкти, чи в домашній теці. Коли в робочій теці або вище є `CLAUDE.md`, Claude Code читає його замість `AGENTS.md`. Правила з `.claude/rules/` вантажаться в обох випадках.

### 2. Рядок `Loaded`

Спершу файл поза всіма glob:

```text
Прочитай README.md і нічого не міняй. Відповідай одним реченням: що в цьому файлі.
```

Під результатом читання рядка `Loaded` немає. Тепер файл під glob правила `backend/api.md`:

```text
Прочитай api/handlers/users.go і нічого не міняй. Відповідай одним реченням: що в цьому файлі.
```

Під результатом читання з'явиться:

```text
⎿  Loaded .claude/rules/backend/api.md
```

Те саме працює, коли Claude створює чи редагує файл або читає один файл через `cat`: попросіть виконати `cat src/styles/button.css`, і під виводом буде `Loaded .claude/rules/frontend/styling.md`. Порядок важливий: завантажене правило лишається в контексті до `/clear` чи `/compact`, тож файл поза glob читайте першим. Файл, який ви відкрили у своєму редакторі, не рахується, бо Claude його не читав.

### 3. Журнал хука `InstructionsLoaded`

Хук з `.claude/settings.json` дописує кожне завантаження правила в `.claude/instructions-loaded.jsonl` (файл у `.gitignore`). В іншому терміналі в цій самій теці:

```bash
tail -n 3 .claude/instructions-loaded.jsonl
```

Після кроку 2 там буде запис з `"load_reason":"path_glob_match"`, `"globs":["api/**/*.go"]` і `trigger_file_path`, що закінчується на `api/handlers/users.go`. Запису з `README.md` у `trigger_file_path` немає. На початку журналу стоїть `session_start` для `general.md`. Якщо у вас є особисті `~/.claude/CLAUDE.md` чи `~/.claude/rules/`, їхні записи теж там, їх розрізняє поле `memory_type`. `AGENTS.md`, прочитаний напряму, у журнал не потрапляє, і це нормально.

Журнал корисний там, де рядка `Loaded` немає: у `claude -p` (неінтерактивний запуск одним промптом), а також у розширенні для VS Code чи Desktop, де ми рядок не перевіряли.

### 4. Пастка `globs:`

Вийдіть із сесії, у `.claude/rules/backend/database.md` замініть `paths:` на `globs:`, запустіть `claude` знову і одразу введіть `/context`. `database.md` з'явиться в Memory files ще до будь-якого читання, а в журналі буде його запис з `session_start`. Так виглядає правило, перенесене з Cursor без заміни поля.

Поверніть файл:

```bash
git restore .claude/rules/backend/database.md
```

## `claudeMdExcludes`

У `.claude/settings.json` лежать два приклади патернів для монорепо, де Claude підхоплює чужі `CLAUDE.md`. У самому демо вони нічого не виключають, бо таких тек тут немає. Патерни порівнюються з абсолютними шляхами, тому в робочому проєкті починайте їх з `**/` або пишіть повний шлях на своїй машині.

## Як повернути теку в початковий стан

```bash
git restore .
rm -f .claude/instructions-loaded.jsonl
```
