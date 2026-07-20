# Presenter · Lecture 11.4 - карта файлів для демонстрації

Для кожного слайда з кодом, конфігом, CSS чи типографікою: яку гілку взяти, який файл відкрити на
екрані і що саме показати. Робоча тека для всіх шляхів:

```bash
cd ~/sources/claude-course-demos/11.4-first-page
```

Слайди без файлу (діаграми, лідерборд, спектр) тут пропущені навмисно — там нема чого відкривати.
Усі шляхи звірені з репо; команди копіпейст-готові.

---

## Slide 1 · Одна сторінка, два результати

- **Відкрий:** дві сторінки поруч у браузері.
- **Виконай:** ліва — `git checkout bad-run && pnpm dev` → http://localhost:5173; права — `git checkout generated && pnpm dev`.
- **Показуєш:** та сама спека даних, різний вигляд. Права — темний монітор на дизайн-системі. Кадри-страховки: `materials/{bad-page,good-page}.png`.

## Slide 4 · Анатомія дизайн-системи

- **Гілка:** `generated`.
- **Відкрий:** `src/index.css` (токени + `@theme` зі шкалою відступів і радіусів) поряд із текою `src/components/ui/`.
- **Показуєш:** чотири блоки анатомії наживо — токени, типографіка (`--font-sans`/`--font-mono`), шкала відступів у `@theme`, компоненти (`button.tsx`, `card.tsx`).

## Slide 5 · Два шари токенів: примітивні і семантичні

- **Гілка:** `generated`.
- **Відкрий:** `materials/dtcg-format-example.tokens.json`, потім `src/index.css`.
- **Показуєш:** у DTCG-прикладі — примітивний шар (`color.zinc.900`) і семантичний, що посилається на нього (`semantic.background → {color.zinc.900}`). У `index.css` — той самий двошаровий принцип у робочому проєкті: семантичні `--primary`, `--background`, `--destructive`. Наголоси: DTCG — це формат ОБМІНУ, рантайм проєкту — CSS-змінні.

## Slide 6 · Пара токенів у CSS: :root і .dark

- **Гілка:** `generated` (64 токени з темою) або `main` (62 токени scaffold).
- **Відкрий:** `src/index.css`.
- **Показуєш:** пару `--primary` / `--primary-foreground`, значення в OKLCH, блок `.dark` що перевизначає ті самі імена, блок `@theme` що підключає токени до Tailwind. Порахувати наживо: `grep -c oklch src/index.css` → 64 (на `generated`).

## Slide 7 · Registry-модель: код копіюється в проект

- **Гілка:** `generated`.
- **Відкрий:** `src/components/ui/button.tsx` (скопійований код, який ти володієш), потім `registry.json`, потім `public/r/button.json`.
- **Виконай (наживо):** `pnpm dlx shadcn@latest build` — збирає `registry.json` у статичні `public/r/*.json`.
- **Показуєш:** `add` кладе код у твій `src`; свій `registry.json` описує ті самі button/card; після `build` вони живуть у `public/r/` і ставляться командою `add <URL>` у будь-кого. Реєстр — відкритий формат, не приватний канал shadcn.

## Slide 10 · Стартовий стек за три команди

- **Гілка:** `main` (результат трьох команд).
- **Відкрий:** `components.json`, теку `.agents/skills/` (там `shadcn` і `migrate-radix-to-base`), `src/index.css`.
- **Показуєш:** `components.json` з описом проєкту й aliases; дві навички у `.agents/skills/` (інсталятор ставить обидві); `grep -c oklch src/index.css` → 62 у scaffold. Команди зі слайда: `init -t vite`, `add card`, `skills add shadcn/ui`.

## Slide 11 · Своя тема без браузера: tweakcn

- **Гілка:** `generated`.
- **Відкрий:** `materials/supabase-theme.json`, потім диф теми — `git show ae6914d -- src/index.css | head -60`.
- **Виконай (наживо):** `pnpm dlx shadcn@latest add https://tweakcn.com/r/themes/supabase.json --yes --overwrite`.
- **Показуєш:** тема — це пункт реєстру (`type: registry:style`, `cssVars.dark`), ставиться тією самою командою `add`, що й компоненти; після команди токени в `index.css` перезаписані.

## Slide 13 · Навичка frontend-design зсередини

- **Відкрий:** `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/frontend-design/skills/frontend-design/SKILL.md`.
- **Показуєш:** рольову рамку («design lead… rejected templated proposals»), калібрувальний блок трьох луків, двопрохідний механізм: спершу план-токени (палітра 4-6 кольорів, шрифти за ролями, signature), потім критика проти брифу, і лише тоді код.

## Slide 14 · Промпт по вимірах

- **Гілка:** `generated`.
- **Відкрий:** `CLAUDE.md`.
- **Показуєш:** естетичний блок як постійний гайданс проєкту — ті самі чотири виміри (типографіка, колір і тема, motion, фони), що навичка проговорює на кожній UI-задачі. Це те, що з cookbook кладуть у CLAUDE.md, щоб кожна генерація отримувала напрям автоматично.

## Slide 15 · Перша сторінка: шлях у терміналі

- **Гілка:** `generated`.
- **Відкрий:** запущену сторінку http://localhost:5173 (`pnpm dev`) + `materials/good-page-mobile.png`.
- **Показуєш:** результат наскрізного прогону; signature-елемент — 30-денна стрічка аптайму зі sparkline у панелі мережі.

## Slide 16 · Три шари дифа: токени, композиція, дані

- **Гілка:** `generated`.
- **Відкрий / виконай:**
  - `git diff main generated -- src/index.css` — шар токенів (нові кольори у `@theme`/`:root`, 0 голих hex);
  - `git diff main generated -- src/App.tsx` — шар композиції (імпорти лише з `@/components/ui`);
  - `src/App.tsx` рядок `type ServiceStatus` — шар даних (union `"online" | "down" | "updating"`);
  - `materials/negative-control.diff` — голий hex в arbitrary-класі (навмисно зламана дисципліна);
  - `materials/type-control-tsc-error.txt` — помилка компілятора на стані-самозванці.
- **Виконай (тип-контроль наживо):** заміни стан на `"rebooting"` у `INITIAL_SERVICES`, потім `pnpm exec tsc -p tsconfig.app.json --noEmit` → `not assignable to type 'ServiceStatus'`; відкоти `git checkout -- src/App.tsx`.

## Slide 17 · Claude Design: чат ліворуч, живе полотно праворуч

- **Відкрий:** https://claude.ai/design/p/4d27d1fc-c61e-4cf6-b0f3-775f6ff47cb6 (акаунт genkovi4@gmail.com).
- **Показуєш:** двопанельний екран — чат і полотно; шапка Beta. Кадр-страховка: `materials/cd-canvas.png`.

## Slide 18 · Онбординг: репозиторій стає UI-набором

- **Відкрий:** https://claude.ai/design/p/3e5e150d-2436-4af9-a762-84dbdc1fed67 → вкладка Design System.
- **Показуєш:** README, специмени (Neutral surfaces: background L 0.18 = `oklch(0.1822 0 0)` з `index.css`), Monitor UI kit, StatusBadge. Кадри-страховки: `materials/{cd-import,cd-ui-kit}.png`.

## Slide 19 · Чотири ручки ітерації навколо полотна

- **Відкрий:** той самий дизайн-проєкт `4d27d1fc-...` — файли Server Status і Header Variants, панель Tweaks (cardRadius/cardGap), панель Comments.
- **Показуєш:** чотири способи ітерації в історії чату: команда, коментар (Annotate), повзунки, варіанти 1a/1b/1c. Кадри-страховки: `materials/{cd-sliders,cd-variants}.png`.

## Slide 20 · Handoff: з полотна у свій репозиторій

- **Гілка:** `handoff`.
- **Відкрий:**
  - `design-handoff/README.md` («CODING AGENTS: READ THIS FIRST»);
  - `design-handoff/project/Server Status.dc.html` (файл дизайну);
  - `design-handoff/project/_ds/home-srv-design-system-3e5e150d-.../styles.css` (дизайн-система з токенами);
  - `git show handoff -- src/App.tsx` — реалізація одним комітом (+47/−42: шапка-метрики варіанта 1b, destructive-кнопка).
- **Виконай (прототип без Claude Design):** `python3 -m http.server 8777 -d design-handoff/project` → http://localhost:8777/Server%20Status.dc.html.

---

## Швидка звірка перед записом

```bash
cd ~/sources/claude-course-demos/11.4-first-page
git checkout generated
pnpm exec tsc -p tsconfig.app.json --noEmit     # тип-контроль чистий
pnpm dlx shadcn@latest build                    # registry збирається у public/r/
grep -c oklch src/index.css                     # 64 на generated, 62 на main
```
