# Workbook · Підключи Figma або Pencil до власного застосунку

## 1. Обери маленький екран

Не бери весь продукт. Обери один route або один незалежний UI-блок:

- login form;
- profile card;
- settings screen;
- dashboard header;
- editor panel;
- landing hero.

Запиши:

```text
Project path:
Dev command:
Local URL:
Screen name:
```

## 2. Заповни короткий brief

Скопіюй `examples/screen-brief.md` у свій проєкт як `design/brief.md`.

Відповідай лише на п’ять питань:

1. Який екран змінюємо?
2. Що має стати зручнішим?
3. Яка чинна поведінка повинна залишитися?
4. Які стани треба показати?
5. Які desktop/mobile widths перевіряємо?

Не описуй всю архітектуру, backend або базу даних, якщо зміна їх не стосується.

## 3. Зафіксуй стан «до»

- [ ] застосунок запущений;
- [ ] екран відкритий у browser;
- [ ] зроблено desktop screenshot;
- [ ] зроблено mobile screenshot;
- [ ] поточна поведінка перевірена руками;
- [ ] `git status --short` зрозумілий.

## 4. Підключи один інструмент

Обери один основний маршрут:

- Official Figma — якщо працюєш із Figma;
- Pencil — якщо хочеш `.pen` у Git;
- Console — лише якщо потрібен Desktop Bridge і розширене authoring.

Не встановлюй усі три заради галочки.

## 5. Створи design

- [ ] connection перевірений read-only prompt-ом;
- [ ] створені або перевикористані variables;
- [ ] повторювані controls стали components;
- [ ] є desktop frame;
- [ ] є mobile frame;
- [ ] є loading/error/disabled або вони позначені N/A;
- [ ] зроблено screenshot design;
- [ ] людина затвердила frame перед implementation.

## 6. Поверни design у code

Використай `prompts/04-implement-and-verify.md`. Після роботи:

- [ ] відкрий `git diff --stat`;
- [ ] запусти доступні project checks;
- [ ] відкрий screen у browser;
- [ ] перевір чинну поведінку;
- [ ] порівняй desktop/mobile з design;
- [ ] не приймай відповідь агента як єдиний доказ.
