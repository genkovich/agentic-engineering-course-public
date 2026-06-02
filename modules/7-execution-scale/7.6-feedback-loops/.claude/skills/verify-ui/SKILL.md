---
name: verify-ui
description: Verify a story's acceptance criteria through a LIVE browser run via playwright-cli (CLI-first, token-efficient). Triggers on '/verify-ui <story-id>' (e.g. '/verify-ui story-26'), or 'перевір UI у браузері', 'прокликай story через Playwright', 'розробка через Playwright'. Reads tasks/<story-id>.md, opens :5173, drives the scenario, reads real page state (DOM + computed styles), returns a per-AC pass/fail with a screenshot artefact. Does NOT fix code — only renders a verdict.
argument-hint: <story-id> (e.g. story-26)
allowed-tools: Read, Glob, Bash(playwright-cli:*), Bash(npx:*), Bash(npm:*)
disable-model-invocation: false
---

# verify-ui — перевірити AC story живим прогоном у браузері (CLI-first)

Браузерний канал зворотного зв'язку лекції 7.6. Ловить те, де детермінований гейт безсилий:
компілюється, юніт-тест зелений, а в живому браузері відступ з'їхав, стан не зберігається, поле
не реагує. Skill бере story з AC у форматі Given/When/Then і проганяє сценарій через
**`playwright-cli`** (не MCP) проти запущеного dev-сервера на :5173, читає **справжній стан
сторінки** і ставить вердикт.

> Це self-contained дзеркало канонічного скіла `verify-ui` з курсового sdlc-тулкіта
> (`/sdlc-verify-ui`). Тут — для демо, що працює без встановленого плагіна.

Команди `playwright-cli` задокументовані у сусідньому скілі `.claude/skills/playwright-cli/`
(встановлений через `playwright-cli install --skills`). Канонічна story цього каналу —
**`story-26`** (`EditCardForm`): кнопка «Скасувати» має відступ 8px замість 12px за еталоном —
юніт і навіть Playwright-сценарій поведінки сліпі, бо форма зберігає/скасовує коректно; ловить
лише читання **обчисленого стилю** в живому прогоні.

## Аргументи

- `<story-id>` — ім'я файлу story без `.md` (напр. `story-26`). Шукається у `tasks/`.

## Передумова (GATE)

Dev-сервер на :5173 (`make dev` або `npm run dev`). Якщо `playwright-cli open
http://localhost:5173` падає на конекті — **не вигадуй стан**, спочатку підніми сервер.

## Кроки (цикл «відкрив → прочитав стан → виправив за фактом»)

1. **Read** `tasks/<story-id>.md` — витягни блоки AC (Given/When/Then). Перевіряй тільки те, що там є.
2. **Відкрити:** `playwright-cli open http://localhost:5173`.
3. **Зчитати стан:** `playwright-cli snapshot` — текстове дерево елементів із рефами (`e21`).
   Знайди елементи, на які посилаються AC (напр. `[data-testid="cancel-button"]`).
4. **Для кожного AC** відтвори When і прочитай Then із **реального** стану:
   - дія: `playwright-cli click <ref>`, `type <text>`, `fill <ref> <text> --submit`, `press <key>`;
   - перевірка стану: `playwright-cli eval "<js>"` для обчислених стилів/значень
     (для story-26: прочитати `getComputedStyle(document.querySelector('[data-testid=cancel-button]')).paddingLeft`
     → очікуємо `12px`, баг дає `8px`); `snapshot` для DOM; `reload` для персистенції.
5. **Доказ:** `playwright-cli screenshot` → знімок прогону (у `tmp/`).

## Output — дискретний вердикт по AC (evidence-before-assertion)

```
story-26 · verify-ui
  AC-1  FAIL — paddingLeft кнопки «Скасувати» = 8px, еталон 12px (getComputedStyle)
  AC-2  PASS — кнопка «Зберегти» й поля без змін
  AC-3  PASS — форма зберігає й закривається коректно
Підсумок: FAIL (1/3). Доказ: tmp/story-26-after.png
```

Після фіксу (`px-2` → `px-3` у `src/components/EditCardForm.tsx`) повторний прогін → `AC-1 PASS`.

## Acceptance criteria

- Вердикт прив'язаний до конкретних AC зі story-файлу, з фактичним vs очікуваним значенням,
  прочитаним зі сторінки (`eval`/`snapshot`), а не «на око».
- Прогін через `playwright-cli` (CLI), не Playwright MCP.
- Є посилання на screenshot-доказ.

## Anti-patterns

- **Не вигадуй AC** — лише те, що у story-файлі.
- **Не «лагодь» код тут** — skill лише ставить вердикт; фікс — окремий крок.
- **Не рапортуй PASS без прочитаного стану** — без `eval`/`snapshot` це здогад, не доказ.
- **Не тягни Playwright MCP у цикл** — CLI дешевший; MCP лиши на живий дебаг.
