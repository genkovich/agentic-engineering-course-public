---
paths:
  - "src/components/**/*.tsx"
  - "src/pages/**/*.tsx"
---

# React conventions

Завантажується тільки коли Claude читає, створює або редагує `.tsx` файл під `src/components/` або `src/pages/`. Решту часу не у контексті.

## Component structure

- Functional components only. No class components anywhere in the codebase.
- One component per file. Filename matches the component name in PascalCase: `Button.tsx`, `UserCard.tsx`.
- Props interface named `{ComponentName}Props`. Always typed, never `any`.
- Default-export the component. Named exports for related types and helpers.

## Hooks discipline

- Custom hooks live in `src/hooks/` and start with `use`. Component-local state stays inline.
- Never call hooks conditionally or inside loops. ESLint `react-hooks/rules-of-hooks` is enforced.
- For data fetching use react-query, never raw `useEffect + fetch`. Server state belongs to the cache, not component state.
- Memoize only when a profiler shows a measurable cost. Premature `useMemo` and `useCallback` add noise without benefit.

## Styling

- No inline styles except for dynamic values (transform, computed positions). Static styling goes to a sibling `.css` file.
- Component styles live in `src/styles/`, one file per component with a lowercase name: `Button.tsx` imports `../styles/button.css` at the top of the file.
- Tailwind utility classes are allowed in components. Custom CSS lives in `src/styles/`.

## Tests

- Unit tests live next to the component: `Button.test.tsx`. Use Vitest plus Testing Library.
- Test behavior, not implementation. Query by accessible role and label, not by class names or test ids.
