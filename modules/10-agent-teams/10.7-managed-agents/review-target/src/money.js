// Format a dollar amount as a currency string.
function formatMoney(amount, currency = "USD") {
  const sign = amount < 0 ? "-" : "";
  const cents = Math.round(Math.abs(amount) * 100);
  const dollars = Math.floor(cents / 100);
  const rem = String(cents % 100).padStart(2, "0");
  return `${sign}${currency} ${dollars}.${rem}`;
}

module.exports = { formatMoney };
