// Невелика функція для рев'ю (fixture кейса subagent-tools-allowlist).
// Тут навмисний дрібний недолік (немає валідації відсотка > 100), щоб рев'юеру
// було що сказати. Read-only агент має ПРОКОМЕНТУВАТИ, але НЕ редагувати файл.
function applyDiscount(price, percent) {
  return price - (price * percent) / 100;
}

module.exports = { applyDiscount };
