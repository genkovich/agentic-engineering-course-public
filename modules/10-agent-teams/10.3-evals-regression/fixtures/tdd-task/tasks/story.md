# Story: slugify(input)

Реалізувати `slugify(input: string): string` у `src/slug.js` за TDD (RED → GREEN → REFACTOR).

## Acceptance criteria (Given/When/Then)

- `slugify("Hello World")` → `"hello-world"`
- `slugify("  Trim  Me  ")` → `"trim-me"`
- `slugify("a@@@b")` → `"a-b"`
- `slugify("")` → `""`

## Правила реалізації

1. Привести до нижнього регістру.
2. Будь-який непустий пробіг символів поза `[a-z0-9]` → один дефіс.
3. Прибрати дефіси на початку й у кінці.

## Definition of Done

- `node --test` зелений.
- Рівно **3 атомарні коміти**: `test(slug): …`, `feat(slug): …`, `refactor(slug): …`.
- Після фази RED `test/` більше не змінюється (тести — незмінний контракт).
