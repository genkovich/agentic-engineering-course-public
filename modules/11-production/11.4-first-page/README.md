# Demo 11.4 · Дизайн з Claude: від дизайн-системи до першої сторінки

**Module:** 11, Production
**Lecture:** 11.4

Демо-кіт лекції 11.4. Лекція багато де посилається на конкретні артефакти (токени в `index.css`,
пара `:root` / `.dark`, `@theme`, `components.json`, власний `registry.json`, формат DTCG, три шари
дифа, handoff-пакунок). Тут лежать дві речі: готовий знімок коду, який можна відкрити й підняти
одразу, і презентерська карта «слайд → який файл відкрити на екрані і що саме показати».

## З чого почати

| Ти | Куди йти |
|---|---|
| проходиш урок | [`demo-snapshot/`](demo-snapshot/) - готовий код фінального прогону, підіймається трьома командами (нижче) |
| хочеш побачити контраст «до / після» | демо-репо з гілками (нижче) - без гілок контрасту не побачити |
| записуєш лекцію | [`PRESENTER.md`](PRESENTER.md) - карта «слайд → файл» |

### Підняти знімок

```bash
cd demo-snapshot
pnpm install                    # corepack падає → export COREPACK_INTEGRITY_KEYS=0
pnpm dev                        # http://localhost:5173
```

## Демо-репо з гілками

`demo-snapshot/` - це знімок однієї гілки (`generated`), тож він показує фінальний результат, але не
показує шляху до нього. Контраст «наївний промпт проти повного протоколу» живе на гілках, і за ним
треба йти в окремий репозиторій:

```bash
git clone git@github.com:genkovich/11.4-first-page.git
cd 11.4-first-page
git checkout generated          # основна демо-гілка
```

Локальна копія: `~/sources/claude-course-demos/11.4-first-page`.

Окремий репозиторій потрібен ще й тому, що онбординг Claude Design тягне репозиторій саме з GitHub.
Він лишається джерелом правди: `demo-snapshot/` перезнімається з гілки `generated` командою

```bash
git -C ~/sources/claude-course-demos/11.4-first-page archive generated | tar -x -C demo-snapshot
```

### Гілки

| Гілка | Що містить | Для яких слайдів |
|---|---|---|
| `main` | чистий scaffold трьох команд + навичка shadcn + `materials/` | 10 (три команди), 16 (baseline дифа) |
| `bad-run` | наївний промпт без навичок: світлий generic-дашборд | 1 (ліва половина), 12 |
| `generated` | повний протокол: тема supabase → шрифти → генерація → ітерація → скрипт скріншотів → демо-файли | 1 (права), 4-7, 11, 14-16 |
| `handoff` | реалізація handoff-пакунка Claude Design | 20 |
| `generated-old-cyberpunk`, `handoff-old-cyberpunk` | бекапи попереднього прогону | — |

## Що додано під демонстрацію (гілка `generated`)

Ці файли створені спеціально, щоб раніше «тільки згадані» слайди стали демонстровними:

| Файл | Слайд | Показує |
|---|---|---|
| `registry.json` + `public/r/{button,card,registry}.json` | 7 | власний реєстр: `shadcn build` пакує компоненти у статичний JSON, який ставиться командою `add` за URL |
| `CLAUDE.md` | 14 | естетичний блок у проєкті: чотири виміри як постійний гайданс вигляду |
| `materials/dtcg-format-example.tokens.json` | 5 | формат обміну DTCG 2025.10: примітивний і семантичний шари з `{reference}` |
| `materials/supabase-theme.json` | 11 | тема tweakcn як пункт реєстру (`type: registry:style`, `cssVars.dark`) |

Решта відкриваних файлів (`src/index.css`, `components.json`, `src/components/ui/*`, `src/App.tsx`,
`.agents/skills/*`, `materials/negative-control.diff`, `materials/type-control-tsc-error.txt`,
`design-handoff/*`) вже жили в репо.

Живі проєкти Claude Design (акаунт **genkovi4@gmail.com**):
- дизайн-система: https://claude.ai/design/p/3e5e150d-2436-4af9-a762-84dbdc1fed67
- дизайн: https://claude.ai/design/p/4d27d1fc-c61e-4cf6-b0f3-775f6ff47cb6
