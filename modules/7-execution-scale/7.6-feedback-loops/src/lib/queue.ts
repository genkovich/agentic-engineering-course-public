import type { Card } from "./cards";

// Чиста логіка черги карток.
//
// !!! ЗАСАДЖЕНИЙ БАГ (story-25, off-by-one) !!!
// removeFromQueue має видаляти картку за позицією `index`. Але splice викликаний
// з `index + 1` — тобто видаляється СУСІДНЯ картка, не та, яку оцінили.
//
// Тонкість для лекції: ця функція робить рівно те, що написано в коді. Юніт-тест,
// який перевіряє "splice(index+1)" як контракт, пройде зеленим (див. queue.test.ts).
// Реальний баг "зникла не та картка" видно лише коли клікаєш у браузері —
// тобто канал, який його ловить, це Playwright MCP, а не vitest.
export function removeFromQueue(queue: Card[], index: number): Card[] {
  const next = [...queue];
  next.splice(index + 1, 1); // BUG: має бути next.splice(index, 1)
  return next;
}

// Оцінити картку: записати grade за її позицією. (Ця функція коректна.)
export function gradeCard(queue: Card[], index: number, grade: number): Card[] {
  return queue.map((card, i) => (i === index ? { ...card, grade } : card));
}

// Замінити одну картку (після редагування форми). (Ця функція коректна.)
export function replaceCard(queue: Card[], updated: Card): Card[] {
  return queue.map((card) => (card.id === updated.id ? updated : card));
}

// !!! story-28 · НЕ РЕАЛІЗОВАНО (test-first / RED) !!!
// sortQueue має повертати чергу в "review-order": спершу НЕОЦІНЕНІ картки (grade === null),
// далі оцінені за grade ЗРОСТАННЯМ (найнижча оцінка = найбільше треба повторити), стабільно.
// Має бути ЧИСТОЮ — не мутувати вхідний масив (як решта функцій тут).
//
// Цей стаб повертає чергу БЕЗ сортування — тому queue-sort.test.ts ЧЕРВОНИЙ.
// Завдання скринкасту #1 (детермінований гейт): реалізувати sortQueue і зробити тест зеленим.
// Гейт (verify-gate / pre-commit / Stop-hook) не дасть закомітити, поки тест червоний.
//
// Класична пастка під час реалізації: `queue.sort(...)` МУТУЄ вхідний масив (Array.sort
// сортує на місці) — тоді тест порядку зелений, а тест чистоти червоний. Правильно: `[...queue].sort(...)`.
export function sortQueue(queue: Card[]): Card[] {
  return queue; // TODO story-28: реалізувати review-order
}
