// Гейт-тести для gate-green (вбудований node:test — без npm-залежностей).
// ЧЕРВОНІ на старті: total() — стаб. Це test-first премиса кейса.
const test = require("node:test");
const assert = require("node:assert");
const { total } = require("../src/total");

test("сумує price*qty по позиціях", () => {
  assert.strictEqual(total([{ price: 2, qty: 3 }, { price: 5, qty: 1 }]), 11);
});

test("порожній кошик -> 0", () => {
  assert.strictEqual(total([]), 0);
});

test("одна позиція", () => {
  assert.strictEqual(total([{ price: 4, qty: 2 }]), 8);
});
