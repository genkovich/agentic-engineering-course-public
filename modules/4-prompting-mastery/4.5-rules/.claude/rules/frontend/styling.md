---
paths:
  - "**/*.css"
  - "**/*.scss"
---

# Styling conventions

Завантажується для будь-якого `.css` або `.scss` файлу у проекті. Покриває і компонентні стилі, і глобальні.

## Naming

- BEM convention for component classes: `.button`, `.button__icon`, `.button--primary`.
- One root class per file. The file name matches the root: `button.css` defines `.button`.
- Avoid generic names like `.container`, `.wrapper`, `.box` at the global level. Scope them to a component.

## Specificity and structure

- No `!important`. If you reach for it, the cascade is wrong - fix the source instead.
- Flat selectors. Nesting deeper than two levels signals a missing component boundary.
- Custom properties for design tokens: `--color-brand`, `--space-md`, `--radius-sm`. Defined in `src/styles/tokens.css`, consumed elsewhere.
- Media queries co-locate with the rule they modify, not at the bottom of the file.

## Layout

- Prefer flexbox and grid over absolute positioning. Absolute positioning is for tooltips and overlays only.
- Use logical properties: `margin-inline-start` instead of `margin-left`. Future i18n stays cheap.
- Spacing through tokens, not raw pixels. `padding: var(--space-md)`, not `padding: 12px`.

## What to avoid

- No `@import` between component CSS files. Each component owns its styles.
- No global `* { }` resets beyond the project-wide reset in `src/styles/reset.css`.
- No vendor prefixes by hand. Autoprefixer handles them at build time.
