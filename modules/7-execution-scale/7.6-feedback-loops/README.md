# 7.6 · Цикли зворотного зв'язку (Feedback loops) — demo + screencast

Demo-проект для лекції **7.6 Цикли зворотного зв'язку**
(Module 7 · Execution & Scale).

Цикл зворотного зв'язку — це канал, яким агент дізнається, чи його зміна справді
робить те, що треба: дія → сигнал → корекція. Різні баги ловляться різними каналами.
Тест проходить, а в браузері поламано. Форма працює, а відступ не той. Код коректний,
а стан губиться після reload. Цей пакет дає (1) **runnable** синтетику з трьома
засадженими багами — по одному під свій канал — і (2) **скрінкаст-сценарії** прогону
кожного каналу.

> **Драбина рівнів.** Демо показує **два** канали зворотного зв'язку: детермінований
> гейт (`tsc` + vitest) і розробку через Playwright. Обидва - runnable.

## Що показує

- **Детермінований гейт (story-28)** — головний канал для коду: `sortQueue` ships test-first,
  `queue-sort.test.ts` ЧЕРВОНИЙ (стаб). Гейт `npx tsc --noEmit && npm test` (= `make gate`,
  його ж ганяють `scripts/pre-commit` і Stop-hook `.claude/hooks/verify.sh`) не дає завершити/
  закомітити, поки червоно. Скіл `verify-gate` (`/verify-gate story-28`) реалізує функцію й не
  каже DONE без зеленого гейта + вставленого виводу як доказу.
- **Розробка через Playwright (CLI-first)** — головний браузерний канал: агент відкриває
  застосунок через `playwright-cli`, читає **реальний стан сторінки** (`getComputedStyle`,
  DOM), бачить розходження з критерієм і виправляє за фактом. Канонічна story — `story-26`
  (`EditCardForm`): відступ кнопки 8px замість 12px, чого юніт і поведінкові тести не ловлять.
- **Чому юніт-тест сам по собі сліпий**: `src/lib/queue.test.ts` ЗЕЛЕНИЙ попри off-by-one — він описує поточну поведінку функції, а не намір користувача. Це центральний teaching point.
- **Скіл `verify-ui`** (`/verify-ui <story>`) — CLI-first браузер-перевірка через `playwright-cli`;
  канонічна версія живе в курсовому sdlc-тулкіті як `/sdlc-verify-ui`. Опційні референси в репо:
  `screenshot-diff` (старий піксельний канал) і `/code-review` (рев'юер у чистому контексті).

Синтетичний застосунок — **абстрактна «черга карток на повторення»**: список із 3 карток,
кнопки оцінок 1–5, форма редагування. Це навмисно **kata** (урок про патерн перевірки),
а не реальний продуктовий фронтенд.

## Setup

```bash
cd modules/7-execution-scale/7.6-feedback-loops

npm install
make dev          # підняти dev-сервер на :5173 (тримати у фоні)
```

Потрібен встановлений `claude` CLI для прогону skills. Браузерний канал — **CLI-first**:

```bash
npm install -g @playwright/cli@latest   # CLI для агентів (перевірено: v0.1.13)
npx playwright install chromium          # браузер (або використає системний Chrome)
playwright-cli install --skills          # навички CLI у .claude/skills/playwright-cli
```

`.mcp.json` тримає **Playwright MCP** (`npx @playwright/mcp@latest`) для живого дебагу і
**Figma Dev Mode MCP** (`https://mcp.figma.com/mcp`, OAuth) для design-input. Локальна
альтернатива Figma — Desktop Dev Mode (Preferences → Enable Dev Mode MCP Server,
зазвичай `http://127.0.0.1:3845/mcp`).

## Як запустити

| Команда | Що робить |
|---|---|
| `make dev` | Dev-сервер (npm run dev) на :5173 — потрібен усім браузерним каналам. |
| `make verify` | Юніт-тести (vitest). story-28 (`queue-sort.test.ts`) ЧЕРВОНИЙ навмисно (test-first, премиса скринкасту #1); `queue.test.ts` (story-25) ЗЕЛЕНИЙ навмисно — teaching point. |
| `make gate` | Детермінований гейт: `npx tsc --noEmit && npm test` — той самий, що pre-commit/Stop-hook. ≠0 = червоно. |
| `make install-hooks` | Вказати git на `scripts/pre-commit` (увага: монорепо — core.hooksPath глобальний). |
| `make clean` | Прибрати `tmp/`. |

Самі канали — це slash-команди, що живуть усередині `claude` (не в чистому shell):

| Команда | Канал | Story | Баг |
|---|---|---|---|
| `/verify-gate story-28` | **детермінований гейт (tsc+vitest)** — скринкаст #1 | story-28 | `sortQueue` стаб (test-first RED) |
| `/verify-ui story-26` | **браузер (playwright-cli)** — скринкаст #2 | story-26 | відступ кнопки 8px vs 12px |
| `/verify-ui story-25` | браузер (playwright-cli) — опційний реф | story-25 | off-by-one у `removeFromQueue` |
| `/screenshot-diff story-26` | піксельний diff (старий канал) | story-26 | відступ кнопки 8px vs 12px |
| `/code-review story-27` | рев'юер у чистому контексті | story-27 | стан не зберігається в localStorage |

## Засаджені баги (де живуть)

| Story | Файл | Баг | Хто ловить | Хто сліпий |
|---|---|---|---|---|
| story-28 | `src/lib/queue.ts` + `queue-sort.test.ts` | `sortQueue` — стаб (test-first RED) | **детермінований гейт** (`make gate`/pre-commit/Stop-hook) | — (тест уже червоний) |
| story-26 | `src/components/EditCardForm.tsx` | кнопка «Скасувати» `px-2` (8px) замість `px-3` (12px) | **`verify-ui` (playwright-cli, `getComputedStyle`)** | юніт + поведінкові тести |
| story-25 | `src/lib/queue.ts` | `splice(index + 1, 1)` замість `splice(index, 1)` | браузер (`verify-ui story-25`) | юніт-тест (зелений) |
| story-27 | `src/App.tsx` + `src/lib/storage.ts` | `saveQueue` існує, але ніде не викликається | рев'юер (`/code-review`) | юніт + screenshot |

## Два канали в дії

Демо показує два канали зворотного зв'язку наживо:

- **#1** — детермінований гейт не пускає червоне (story-28): `make gate` червоний (`sortQueue`
  стаб) → `/verify-gate story-28` реалізує review-order, не каже DONE поки гейт червоний →
  зелено (`7 passed`) → коміт із виводом як доказом (`make gate` red→green;
  Stop-hook `verify.sh` дає exit 2 на червоному, exit 0 на зеленому).
- **#2** — розробка через Playwright (story-26): агент відкриває через `playwright-cli`,
  читає `getComputedStyle` кнопки (`8px`), виправляє `px-2`→`px-3`, перечитує (`12px`).

## Покриття концептів лекції

| Концепт лекції | Де у демо |
|---|---|
| Цикл дія → сигнал → корекція | `verify-ui`: дія в UI → читання живого стану → фікс |
| Розробка через Playwright (живий стан, не картинка) | `/verify-ui story-26` + `getComputedStyle` через `playwright-cli` |
| CLI за замовчуванням, MCP — на живий дебаг | `playwright-cli` у скілі + Playwright MCP у `.mcp.json` |
| Браузер як канал (юніт сліпий) | `/verify-ui story-25` + `src/lib/queue.test.ts` (зелений попри баг) |
| Design-input через Figma Dev Mode MCP | `figma` у `.mcp.json` (читає структуру макета на вході) |
| Чистий контекст рев'юера | `/code-review` (бачить лише diff + AC) |
| Дискретний вердикт по AC | pass/fail з фактичним vs очікуваним — не «ну майже» |

## Чесні примітки

- `baselines/edit-card-form.png` — **реальний** скриншот форми (512×300, знятий через
  Playwright/Chromium на :5173 у «правильній» версії з відступом 12px), а не плейсхолдер.
  Бекап-процедура генерації: тимчасово виставити `px-3`, зняти знімок, повернути `px-2`.
- `queue.test.ts` зелений на чистому checkout — це навмисно. Лекційна точка: юніт-канал
  не ловить off-by-one такого роду. Після фіксу `removeFromQueue` тест очікувано стане
  червоним і його треба переписати під реальний контракт.
- `tmp/` (знімки прогонів, diff-зображення) ігнорується git; `baselines/` комітимо.

## Як перенести у свій проєкт

1. Встанови `playwright-cli` (`npm i -g @playwright/cli@latest` → `playwright-cli install --skills`)
   або підключи канонічний `verify-ui` з sdlc-тулкіта (`/sdlc-verify-ui`).
2. Скопіюй `.mcp.json` (Playwright MCP + Figma Dev Mode MCP) і story-файли з AC у `tasks/`.
3. Запусти `/verify-ui <story>` під свій баг: агент відкриє застосунок, прочитає живий стан
   (`getComputedStyle`/DOM/`localstorage-get`) і дасть вердикт по AC. Для рев'ю diff — `/code-review`.

## Sources

- Module 7 лекція 7.6 `Sources.md` — повний список.
