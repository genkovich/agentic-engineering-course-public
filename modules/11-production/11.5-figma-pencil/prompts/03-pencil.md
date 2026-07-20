# Prompt 03 · Pencil Dev

Перед prompts:

1. встанови extension `highagency.pencildev` від High Agency або Desktop app;
2. активуй Pencil через email;
3. відкрий root власного застосунку;
4. створи через Pencil `design/main-screen.pen`;
5. залиш Pencil запущеним;
6. відкрий нову Claude Code session і перевір `/mcp` → `pencil` connected.

## C0. Connection check

```text
Use only Pencil. Do not modify design or code.

Report:
1. active .pen file;
2. current frames;
3. available design, screenshot, variables, and layout operations.

Stop after the report.
```

## C1. Build design beside the code

```text
Use the open Pencil file design/main-screen.pen.

Read design/brief.md and inspect this repository only enough to understand
the current screen, reusable UI components, and existing style variables.

Create:
- a Current UI reference;
- the variables needed by this screen;
- reusable components for repeated controls;
- a desktop frame at 1440px;
- a mobile frame at 390px;
- all applicable states from the brief.

After writing:
- run layout analysis;
- take desktop and mobile screenshots;
- report clipping or overlap;
- save the .pen file.
Stop for human approval.
```

## C2. Repo checkpoint

Після `Cmd+S` / `Ctrl+S`:

```bash
git status --short design/main-screen.pen
```

`.pen` редагуй лише через Pencil, не через звичайний text editor.
