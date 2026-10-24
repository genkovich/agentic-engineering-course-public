# claude-rules-demo

Demo monorepo до уроку «Claude Code Rules». Показує модульні правила в `.claude/rules/` з YAML frontmatter `paths:`.

Стек: Go API + React web + Terraform infra. Кожна частина тригерить свій набір scoped rules.

## How to work in this repository

Це fullstack monorepo з трьома незалежними частинами. Перш ніж щось редагувати - визнач, у якій ти зоні. Кожна зона має власні rules з конкретикою.

Цей AGENTS.md - router. Він орієнтує: дає мапу, де які правила лежать. Конкретика живе у scoped rules і підтягується автоматично, коли Claude читає matching файли. Самі правила тут не повторюються: кожне живе в одному файлі в `.claude/rules/`.

### Always loaded

- `.claude/rules/general.md` - baseline coding, security non-negotiables, project assumptions. Завантажується кожну сесію, бо в ньому немає `paths`.

### Backend work (Go API)

Якщо ти у `api/` - підтягнуться:

- `.claude/rules/backend/api.md` - input validation, error codes, sentinel errors, structured logging.
- `.claude/rules/backend/database.md` - якщо чіпаєш `migrations/` чи `models/`: міграції, обмеження схеми, ID, індекси.

### Frontend work (React web)

Якщо ти у `src/components/` чи `src/pages/` - підтягнуться:

- `.claude/rules/frontend/react.md` - functional components, typed props, react-query замість `useEffect + fetch`.
- `.claude/rules/frontend/styling.md` - якщо чіпаєш `.css` чи `.scss`. BEM, no `!important`, design tokens.

### Infra work (Terraform)

Якщо ти у `infra/` - підтягнеться:

- `.claude/rules/infra/terraform.md` - state у S3, теги обов'язкові, no `local-exec`.

## What lives where

```
api/                    Go services - handlers, migrations
src/                    React web - components, pages, styles
infra/                  Terraform
.claude/rules/          Modular rules tree
.claude/settings.json   claudeMdExcludes + хук InstructionsLoaded (журнал завантажень)
```

## Conventions across the whole repo

- All code in English. Comments українською дозволені для складних шматків бізнес-логіки.
- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`. Scope optional.
- One concern per PR. Adding a feature і refactor - окремі PR.
- Tests run on every PR. Failing CI blocks merge - ніяких `--no-verify` обходів.

## What this repo intentionally does NOT include

- Real backing services. Postgres, AWS, Redis - тільки згадуються у правилах, не запускаються.
- Build files. Немає `go.mod`, `package.json` і Terraform state: код не збирається, він потрібен, щоб правила мали реальні файли-тригери.
- Real auth. Endpoints не захищені - це демо.
