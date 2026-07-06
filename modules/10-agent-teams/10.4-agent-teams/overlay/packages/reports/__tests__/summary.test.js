// Детермінована заміна flaky-тестів з 10.1. Командний прогін 10.4 їде на стабільно
// зеленому сьюті: TaskCompleted-гейт ганяє node --test на кожне закриття задачі,
// і випадковий червоний зробив би його рандомним. pickSample лишається
// недетермінованим helper-ом, тож тести перевіряють його властивості
// (семпл — підмножина входу), а не конкретний вміст.
const test = require("node:test");
const assert = require("node:assert");
const { summarize, pickSample } = require("../summary");

test("summary рахує кількість і суму", () => {
  const r = summarize([{ amount: 10 }, { amount: 5 }]);
  assert.strictEqual(r.count, 2);
  assert.strictEqual(r.total, 15);
});

test("summary на порожньому списку дає нулі", () => {
  const r = summarize([]);
  assert.strictEqual(r.count, 0);
  assert.strictEqual(r.total, 0);
});

test("семпл — завжди підмножина вихідних записів", () => {
  const items = Array.from({ length: 10 }, (_, i) => i);
  const sample = pickSample(items);
  assert.ok(sample.every((x) => items.includes(x)));
  assert.ok(sample.length <= items.length);
});
