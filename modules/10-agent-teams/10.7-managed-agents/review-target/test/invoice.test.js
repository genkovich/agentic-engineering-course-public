const test = require("node:test");
const assert = require("node:assert");
const { buildInvoice } = require("../src/invoice");

// These tests all pass. None of them exercises the fractional-cent path
// where the double-rounding bug bites, so the suite is green and the bug ships.
test("subtotal sums line items", () => {
  const inv = buildInvoice([{ price: 10, qty: 2 }, { price: 5, qty: 1 }]);
  assert.strictEqual(inv.subtotal, 25);
});

test("no discount or tax means total equals subtotal", () => {
  const inv = buildInvoice([{ price: 7, qty: 3 }]);
  assert.strictEqual(inv.total, 21);
});

test("discount and tax on a whole-dollar item", () => {
  const inv = buildInvoice([{ price: 100, qty: 1 }], { discountPercent: 10, taxPercent: 20 });
  assert.strictEqual(inv.total, 108);
});
