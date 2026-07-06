// Зелені тести черги (node:test). Покривають happy-path: успіх -> ack,
// перша невдача -> requeue з backoff, зростання backoff. Баг дублювання на
// межі вичерпаних спроб навмисно НЕ покритий — це знаходить воркер (Скринкаст #2).
const test = require("node:test");
const assert = require("node:assert");
const { processOnce, backoffDelay } = require("../consumer");

test("успішна обробка -> ack", () => {
  const queues = { main: [], deadLetter: [] };
  const res = processOnce({ id: 1 }, queues, () => {});
  assert.strictEqual(res.action, "ack");
  assert.strictEqual(queues.main.length, 0);
  assert.strictEqual(queues.deadLetter.length, 0);
});

test("перша невдача -> requeue з backoff", () => {
  const queues = { main: [], deadLetter: [] };
  const boom = () => { throw new Error("boom"); };
  const res = processOnce({ id: 2 }, queues, boom);
  assert.strictEqual(res.action, "requeue");
  assert.ok(res.delayMs >= backoffDelay(1));
});

test("backoff росте експоненційно", () => {
  assert.strictEqual(backoffDelay(0), 100);
  assert.strictEqual(backoffDelay(1), 200);
  assert.strictEqual(backoffDelay(2), 400);
});
