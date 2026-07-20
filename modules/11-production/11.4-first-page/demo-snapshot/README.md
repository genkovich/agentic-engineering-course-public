# 11.4-first-page — демо Lecture 11.4 «Дизайн з Claude»

Greenfield-ґрунт для лекції 11.4: Vite + React + Tailwind v4 + shadcn/ui (пресет nova).

Створено трьома командами з лекції (2026-07-12):

```bash
pnpm dlx shadcn@latest init -t vite   # каркас: ~307 пакетів, components.json, index.css з 62 oklch-токенами
pnpm dlx shadcn@latest add card       # card.tsx у src/components/ui
pnpm dlx skills add shadcn/ui         # навичка shadcn у .agents/skills (+ migrate-radix-to-base)
```

Сценарії запису: `screencast-prompts.md` (5 сценаріїв, ітерація 2). Дзеркало на GitHub потрібне для онбордингу Claude Design (сценарії #3-#5).

## Гілки і матеріали

| Гілка | Що містить |
|---|---|
| `main` | чистий scaffold + навичка shadcn + `materials/` |
| `bad-run` | наївний промпт без навичок: дефолт-тема, generic-дашборд |
| `generated` | повний протокол: tweakcn cyberpunk → бриф за 4 вимірами → генерація → ітерація |
| `handoff` | (після браузерної сесії Claude Design) реалізація handoff-пакунка |

`materials/`: скріншоти обох прогонів (bad/good, + mobile), `negative-control.diff` (голий hex в arbitrary-класах), `type-control-tsc-error.txt` (union-тип ловить `"rebooting"`).

## Чесні нотатки

- Вивід агента недетермінований: палітра і шрифти відрізняються між прогонами.
- corepack pnpm може падати на signature verification → `export COREPACK_INTEGRITY_KEYS=0`.
- Claude Design = research preview: кроки меню звіряти на дату запису; CLI-факти (`/design import|export|sync`) звірені з білдом 2.1.207.
- `pnpm typecheck` зі scaffold-у нічого не перевіряє (solution-style tsconfig): користуйся `pnpm exec tsc -p tsconfig.app.json --noEmit`.
