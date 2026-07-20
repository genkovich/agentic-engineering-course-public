# Модуль 11.5 · Figma та Pencil для власного застосунку

Це універсальний handout до Lecture 11.5. Він не містить і не встановлює demo-застосунок викладача.
Кожен студент проходить інструкцію у власному frontend-проєкті.

```text
власний екран
  → короткий brief
  → Official Figma / Figma Console / Pencil
  → затверджений desktop + mobile design
  → реалізація у власному коді
  → browser + project checks + git diff
```

## Що є у пакеті

| Файл | Для чого |
|---|---|
| `examples/screen-brief.md` | мінімальний brief одного екрана |
| `examples/definition-of-done.md` | проста перевірка практики |
| `student-workbook.md` | маршрут для власного застосунку |
| `prompts/01-official-figma.md` | Official Figma: connection, capture, design |
| `prompts/02-figma-console.md` | PAT, Console MCP і Desktop Bridge |
| `prompts/03-pencil.md` | Pencil Dev: `.pen` поруч із кодом |
| `prompts/04-implement-and-verify.md` | затверджений design → code → browser |
| `scripts/verify-materials.sh` | локальна перевірка комплекту |

## Перевір handout

```bash
cd ~/sources/agentic-engineering-course/modules/11-production/11-5
make verify
```

Очікуваний фінал:

```text
PASS: module 11-5 generic materials are ready.
```

## Підготуй власний застосунок

1. Відкрий root свого frontend-проєкту.
2. Запусти його звичайною dev-командою.
3. Обери один екран.
4. Створи папку `design`.
5. Скопіюй brief і DoD:

```bash
cd /path/to/your-app
mkdir -p design

cp ~/sources/agentic-engineering-course/modules/11-production/11-5/examples/screen-brief.md \
  design/brief.md

cp ~/sources/agentic-engineering-course/modules/11-production/11-5/examples/definition-of-done.md \
  design/definition-of-done.md
```

Заповни placeholder-и у двох файлах. Не копіюй структуру чи поведінку demo-застосунку викладача.

## Обери маршрут

### Найпростіше почати з Official Figma

```bash
claude plugin install figma@claude-plugins-official
cd /path/to/your-app
claude
```

У Claude Code виконай `/mcp` → `figma` → `Authenticate`.

Далі використовуй `prompts/01-official-figma.md` по одному блоку.

### Console — optional advanced

Console потрібен, якщо тобі важлива локальна робота з активним Figma Desktop file. Він вимагає PAT,
Node process і Desktop Bridge. Setup та cleanup є у `prompts/02-figma-console.md`.

### Pencil — якщо дизайн має жити у Git

1. Встанови extension `highagency.pencildev` від High Agency або Desktop app.
2. Активуй Pencil через email.
3. Відкрий root свого застосунку.
4. Створи `design/main-screen.pen` через Pencil.
5. Запусти Claude Code й перевір `/mcp` → `pencil` connected.
6. Виконуй `prompts/03-pencil.md`.

## Поверни design у код

Незалежно від інструмента, використовуй `prompts/04-implement-and-verify.md`.

Перед прийманням результату:

```bash
git status --short
git diff --stat
```

Потім запусти перевірки, які реально є у твоєму проєкті. Наприклад:

```bash
npm run lint
npm test
npm run build
```

Відкрий застосунок у browser і пройди чинну поведінку екрана руками.

## Важливе правило

Handout навчає підключати інструмент до власного застосунку. Він не розповсюджує готовий продукт,
backend, базу даних або implementation викладача.
