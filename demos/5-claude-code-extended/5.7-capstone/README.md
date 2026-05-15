# M5 Capstone — Two Features as Proof

Capstone модуля 5 «Agentic Engineering з Claude». Повний опис у vault: `Own Brand/AI Course/Claude Course/Module 5/_Capstone.md`.

## Головна ідея

Capstone доводить корисність плагіна через **дві фічі** того ж типу:

- **F1** — vertical slice руками, без плагіна. Лог повторюваностей.
- **Extract** — все повторюване виноситься у `plugin/`.
- **F2** — vertical slice з плагіном. Фіксуємо: швидше, з меншою кількістю prompts.

Якщо F2 не швидша — плагін не покрив справді повторюване, ітеруй екстракцію.

## Три фази

### Phase A — Feature 1 manually (~2 год)

1. Обери vertical slice фічу під свій scaffold з M4.12 (наприклад: `Note` CRUD = міграція + endpoint + tests).
2. Реалізуй у `feature-1/` без плагіна.
3. Веди `CAPSTONE_LOG.md` — записуй prompts, ручні перевірки, повернення назад.

### Phase B — Extract to plugin (~30-45 хв)

З логу Phase A витягни повторюване у `plugin/`:
- 2-3 skills (паттерн з 5.2 `pdf-form-filler`, 5.3 `audit-api-endpoint`)
- 1 hook (BC integrity, pre-commit tests — лекція 5.4)
- опційно: MCP / sub-agent

### Phase C — Feature 2 with plugin (~30 хв)

1. Інша сутність, той самий тип slice (наприклад: `Bookmark` CRUD).
2. Реалізуй у `feature-2/` через команди плагіна.
3. Фіксуй у `CAPSTONE_LOG.md`: час, prompts, спрацювання hook.

## Definition of Done

- [ ] F1 vertical slice end-to-end (DB → API → tests)
- [ ] F2 vertical slice end-to-end того самого типу
- [ ] Плагін викликається у ≥3 ключових кроках F2
- [ ] F2 час < F1 час, зафіксовано у `CAPSTONE_LOG.md`
- [ ] Hook реально щось зловив (≥1 запис у логу)
- [ ] Плагін опублікований на GitHub
- [ ] README плагіна: Purpose / Install / Commands / Skills / Hooks

## Скрінкаст-маркери

- 🎬 F1 manual — де prompt повторюється
- 🎬 Extract — як вирішив, що саме виносити у скіл / hook
- 🎬 F2 with plugin — той самий slice, помітно швидше
- 🎬 Метрики F1 vs F2 поряд з `CAPSTONE_LOG.md`

## Cross-references на лекції M5

| Компонент | Лекція |
|---|---|
| Custom command | 5.1 |
| Skill | 5.2, 5.3 |
| Hook | 5.4 |
| Packaging | 5.5, 5.6 |
| Огляд плагінів | 5.7 |
| SDK | 5.8 |
