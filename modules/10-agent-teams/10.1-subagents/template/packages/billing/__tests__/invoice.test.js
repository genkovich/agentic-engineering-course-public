// Зелені тести білінгу (вбудований node:test, без npm-залежностей).
// Покривають happy-path. Ризик округлення на копійках і валідацію percent
// навмисно НЕ покривають — саме це має знайти рев'ю/воркер.
const test = require("node:test");
const assert = require("node:assert");
const { buildInvoice } = require("../invoice");

test("субтотал по позиціях", () => {
  const inv = buildInvoice([{ price: 10, qty: 2 }, { price: 5, qty: 1 }]);
  assert.strictEqual(inv.subtotal, 25);
});

test("знижка 10% і податок 20%", () => {
  const inv = buildInvoice([{ price: 100, qty: 1 }], { discountPercent: 10, taxPercent: 20 });
  assert.strictEqual(inv.total, 108);
});

test("без знижки й податку разом = субтотал", () => {
  const inv = buildInvoice([{ price: 7, qty: 3 }]);
  assert.strictEqual(inv.total, 21);
});
