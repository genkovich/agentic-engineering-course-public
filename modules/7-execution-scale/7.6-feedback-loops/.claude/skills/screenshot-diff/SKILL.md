---
name: screenshot-diff
description: Compare a rendered component against a design baseline pixel by pixel. Triggers on '/screenshot-diff <story-id>' (e.g. '/screenshot-diff story-26'), or when the user asks to 'звір з Figma-еталоном', 'screenshot diff проти baseline', 'перевір верстку по скриншоту'. Reads baselines/<feature>.png, renders the component on :5173, snapshots to tmp/, computes the diff, returns pass/fail plus a diff image.
argument-hint: <story-id> (e.g. story-26)
allowed-tools: Read, Glob, Bash, mcp__playwright__browser_navigate, mcp__playwright__browser_click, mcp__playwright__browser_take_screenshot
disable-model-invocation: false
---

# screenshot-diff — звірити компонент із дизайн-еталоном

Канал зворотного зв'язку #2 для лекції 7.6: візуальна регресія, яку не видно ні
юніт-тестом, ні навіть Playwright-сценарієм поведінки (форма зберігає й скасовує
коректно). Ловиться вона лише попіксельним порівнянням рендера з еталоном.

Канонічна story — `story-26`: кнопка «Скасувати» має 8px замість 12px на еталоні
`baselines/edit-card-form.png`.

## Аргументи

- `<story-id>` — story з полем `channel: screenshot-diff` у frontmatter (напр. `story-26`).
  Skill читає story, щоб дізнатися, який саме `baselines/<feature>.png` еталон і яку
  частину UI знімати.

## Передумова

Dev-сервер на :5173. Еталон лежить у `baselines/`. Скрипти кладуть знімки в `tmp/`
(ігнорується git).

## Кроки

1. **Read** `tasks/<story-id>.md` → визначити еталон (`baselines/edit-card-form.png`)
   і як дістатися компонента (story-26: клік «Редагувати» → форма).
2. `browser_navigate` → `:5173`, дістатися екрана (для форми — `browser_click` на
   `[data-testid="edit-link"]`).
3. `browser_take_screenshot` елемента `[data-testid="edit-card-form"]` → `tmp/edit-card-form.png`.
4. Порахувати попіксельну різницю проти еталона (через `Bash`, напр. невеликим
   node-скриптом або `compare` з ImageMagick), записати `tmp/edit-card-form.diff.png`.
5. Порівняти частку відмінних пікселів із порогом (`THRESHOLD`, дефолт 0.5%).

## Output

```
story-26 · screenshot-diff (baseline: baselines/edit-card-form.png)
  diff pixels: 1.8%  (поріг 0.5%)  → FAIL
  розбіжність локалізована: ліва межа кнопки «Скасувати» (відступ 8px vs 12px)
  знімок:   tmp/edit-card-form.png
  diff-мапа: tmp/edit-card-form.diff.png
Підсумок: FAIL
```

Після фіксу (`px-2` → `px-3`) — повторний прогін має дати `diff pixels: 0.0% → PASS`.

## Acceptance criteria

- Еталон береться з `baselines/`, новий знімок — у `tmp/` (еталон не перезаписуємо).
- Вердикт = частка відмінних пікселів проти порогу + diff-зображення.
- На FAIL skill називає, ДЕ розбіжність (а не просто «не збігається»).

## Anti-patterns

- **Не оновлюй baseline під поточний рендер** — це сховає баг. Baseline = джерело правди.
- **Не став поріг 0** — антиаліасинг шрифтів дає крихітний шум; тримай маленький поріг.
- **Не плутай із поведінкою** — цей канал про пікселі, не про логіку форми.
