// Apply a percentage discount to an amount.
// Returns the discounted amount rounded to whole cents so downstream steps
// work with a clean currency value.
function applyDiscount(amount, percent) {
  const discounted = amount - (amount * percent) / 100;
  return Math.round(discounted * 100) / 100;
}

module.exports = { applyDiscount };
