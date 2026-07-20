'use strict';

const test = require('node:test');
const assert = require('node:assert');
const { seedAccount, requestWithdrawal, maskAccount } = require('./payments');

test('успішне виведення списує баланс', () => {
  seedAccount('acc-1001', 5000);
  const r = requestWithdrawal('acc-1001', 2000, 'key-a');
  assert.strictEqual(r.status, 'queued');
  assert.strictEqual(r.remaining, 3000);
});

test('той самий idempotency key не списує двічі', () => {
  seedAccount('acc-1002', 5000);
  requestWithdrawal('acc-1002', 2000, 'key-b');
  const second = requestWithdrawal('acc-1002', 2000, 'key-b');
  assert.strictEqual(second.status, 'duplicate');
});

test('запит без idempotency key падає', () => {
  seedAccount('acc-1003', 5000);
  assert.throws(() => requestWithdrawal('acc-1003', 2000, ''), /idempotency key is required/);
});

test('нульовий і від\'ємний amount - помилка, не no-op', () => {
  seedAccount('acc-1004', 5000);
  assert.throws(() => requestWithdrawal('acc-1004', 0, 'key-c'), /positive integer/);
  assert.throws(() => requestWithdrawal('acc-1004', -100, 'key-d'), /positive integer/);
});

test('маскування рахунку лишає тільки останні 4 символи', () => {
  assert.strictEqual(maskAccount('acc-9999'), '****9999');
});
