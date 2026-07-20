'use strict';

// payments-service - демо для лекції 11.5.
// Гроші тримаємо в мінорних одиницях (копійки), цілим числом. Ніяких float.

const balances = new Map(); // account -> копійки
const seenKeys = new Set(); // idempotency keys, які вже застосовано

function seedAccount(account, amountMinor) {
  balances.set(account, amountMinor);
}

function maskAccount(account) {
  // У логах - тільки останні 4 символи.
  return '****' + String(account).slice(-4);
}

function requestWithdrawal(account, amountMinor, idempotencyKey) {
  if (!Number.isInteger(amountMinor) || amountMinor <= 0) {
    throw new Error('amount must be a positive integer (minor units)');
  }
  if (!idempotencyKey) {
    throw new Error('idempotency key is required for every balance mutation');
  }
  if (seenKeys.has(idempotencyKey)) {
    // Повторний запит з тим самим ключем не списує двічі.
    return { status: 'duplicate', account: maskAccount(account) };
  }
  const current = balances.get(account) ?? 0;
  if (current < amountMinor) {
    throw new Error('insufficient funds');
  }
  balances.set(account, current - amountMinor);
  seenKeys.add(idempotencyKey);
  return { status: 'queued', account: maskAccount(account), remaining: current - amountMinor };
}

module.exports = { seedAccount, requestWithdrawal, maskAccount };
