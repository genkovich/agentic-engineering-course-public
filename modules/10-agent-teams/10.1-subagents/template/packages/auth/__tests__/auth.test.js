// Зелені тести автентифікації (node:test). Покривають три гілки middleware:
// немає токена, валідний Bearer, невідомий токен.
const test = require("node:test");
const assert = require("node:assert");
const { requireAuth } = require("../middleware");

test("без заголовка -> 401", () => {
  assert.strictEqual(requireAuth({ headers: {} }).status, 401);
});

test("валідний Bearer -> 200", () => {
  const res = requireAuth({ headers: { authorization: "Bearer secret-token" } });
  assert.strictEqual(res.status, 200);
});

test("невідомий токен -> 401", () => {
  assert.strictEqual(requireAuth({ headers: { authorization: "Bearer nope" } }).status, 401);
});
