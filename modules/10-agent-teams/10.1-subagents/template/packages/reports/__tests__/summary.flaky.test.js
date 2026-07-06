// ⚠️ НАВМИСНО FLAKY: частина цих тестів падає через раз БЕЗ зміни коду. Вони —
// навчальний предмет завдання «познаходь flaky tests» (Скринкаст #2): проблема
// в самих тестах (недетермінований вхід / залежність від часу), а не в summary.js.
// Детерміновані тести billing / queue / auth лишаються стабільно зеленими.
const test = require("node:test");
const assert = require("node:assert");
const { summarize, pickSample } = require("../summary");

test("summary рахує суму детерміновано (стабільно зелений)", () => {
  const r = summarize([{ amount: 10 }, { amount: 5 }]);
  assert.strictEqual(r.total, 15);
});

test("семпл містить перший запис (FLAKY: залежить від Math.random)", () => {
  const sample = pickSample(Array.from({ length: 10 }, (_, i) => i));
  // Антипатерн: чи потрапив конкретний запис у випадковий семпл — 50/50 щоразу,
  // тож тест падає приблизно через раз без жодної зміни коду.
  assert.ok(sample.includes(0), "перший запис не потрапив у семпл цього прогону");
});

test("дві позначки часу збігаються (FLAKY: залежить від хвилини запуску)", () => {
  const minuteA = new Date().getMinutes();
  const minuteB = new Date().getMinutes();
  // Антипатерн: тест залежить від годинника — падає на межі хвилини.
  assert.strictEqual(minuteA, minuteB);
});
