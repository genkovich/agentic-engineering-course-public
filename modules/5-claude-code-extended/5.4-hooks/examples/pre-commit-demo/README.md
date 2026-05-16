# pre-commit-demo

Копі-паст-готовий міні-репозиторій для **Slide 7 (Pre-commit paradox)** і **Slide 12 Variant D (pre-commit gate на CRUD-комітах)** лекції 5.4.

Стек: **Husky + lint-staged + tsc + Vitest** на CRUD-сутності `src/notes.ts`. Покажи студенту як pre-commit блокує коміт із зламаним кодом — і як цей же стек переноситься у власний SaaS-репо.

## Що всередині

```
pre-commit-demo/
├── package.json                    — scripts (prepare/test/tsc) + devDeps
├── .husky/pre-commit               — npx lint-staged && npx tsc --noEmit && npm test
├── lint-staged.config.json         — prettier --write на *.{ts,tsx,js,json,md,css}
├── tsconfig.json                   — strict, ES2022, ESNext, Vitest globals
├── .gitignore                      — node_modules/, dist/
└── src/
    ├── notes.ts                    — CRUD entity (create/read/update/delete/list)
    ├── notes.test.ts               — Vitest, 5 passing tests
    └── notes-broken.example.ts     — копія notes.ts з багом у updateNote (для fail-демо)
```

## Quick start (happy path → pre-commit пройшов)

```bash
cd hooks-toolkit/examples/pre-commit-demo

npm install         # ставить husky/lint-staged/prettier/typescript/vitest
                    # postinstall script (prepare = "husky") активує hook у .git/hooks/

git init
git add -A
git commit -m "demo: initial commit"
# → pre-commit запускає lint-staged → tsc --noEmit → npm test
# → 5/5 tests pass → коміт зелений
```

## Fail path (pre-commit блокує коміт)

```bash
mv src/notes.ts src/notes-original.ts
mv src/notes-broken.example.ts src/notes.ts

git add -A
git commit -m "demo: try to commit broken updateNote"
# → pre-commit падає на npm test:
#     × notes CRUD > updates a note via patch
#       AssertionError: expected 'old title' to be 'new title'
# → коміт ЗАБЛОКОВАНИЙ
```

Студент бачить, що **detection happens before history pollution**: main гілка не отримала зламаний `updateNote`.

Щоб повернути happy path:

```bash
mv src/notes.ts src/notes-broken.example.ts
mv src/notes-original.ts src/notes.ts
git add -A
git commit -m "demo: restore working updateNote"
```

## Як перенести у власний SaaS-репо

```bash
cp -r examples/pre-commit-demo/{.husky,lint-staged.config.json,tsconfig.json} <your-repo>/
```

Потім у власному `package.json`:

```jsonc
{
  "scripts": {
    "prepare": "husky",
    "test": "vitest run",
    "tsc": "tsc --noEmit"
  },
  "devDependencies": {
    "husky": "^9",
    "lint-staged": "^15",
    "prettier": "^3",
    "typescript": "^5",
    "vitest": "^2"
  }
}
```

Один `npm install` — і hook активується через `prepare`-скрипт. Заміни `src/notes.ts` на свою CRUD-сутність із 5.3 і налаштуй фокус тестів через `--testPathPattern=src/<your-entity>` у `npm test` (як описує Variant D).

## Чому це найдешевший quality gate (math зі Slide 7)

- Людина чекає 30-180 секунд на кожен коміт → шукає `--no-verify` → main ламається.
- Claude чекає 3 хвилини без скарг → отримує `passed/failed` як feedback → реагує.
- Ваші гроші, не його час.
- Один pre-commit hook покриває tests + lint + types + format **на final state** коміту, а не на проміжних PostToolUse-викликах (Slide 9 — context economy).

## Гачки для глибшого занурення

- Slide 4 (matcher vs if): pre-commit hook не використовує Claude Code hooks API — це Git-рівневий gate, який реагує на `git commit` від Claude через `Bash` tool. Hook рівня Claude (`PreToolUse` із `if "Bash(git commit *)"`) — комплементарний шар.
- Slide 9 (Context economy): pre-commit замість PostToolUse-quality-gates — один сигнал на final state замість 10 на проміжні writes.
- Slide 13 (Підсумок): «pre-commit замість PostToolUse» = takeaway #4 уроку.

## Troubleshooting

- `husky - command not found` → `npm install` ще не пройшов / `prepare` не виконався → запусти вручну: `npx husky init` (але краще: ще раз `npm install` після `git init`, бо husky шукає `.git`).
- pre-commit «нічого не робить» → перевір, що `.husky/pre-commit` має `+x`: `ls -la .husky/`.
- Тест проходить навіть із зламаним `notes.ts` → перевір, що `notes.test.ts` імпортує `./notes.js` (Node ESM resolution з `tsconfig.json`'s `moduleResolution: "Bundler"` через Vitest).
