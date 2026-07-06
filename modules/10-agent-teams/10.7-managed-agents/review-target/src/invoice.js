// Build an invoice from line items: subtotal -> discount -> tax -> total.
// The final total is rounded to whole cents.
const { applyDiscount } = require("./discount");

function computeSubtotal(lineItems) {
  return lineItems.reduce((sum, it) => sum + it.price * it.qty, 0);
}

function computeTax(amount, taxPercent) {
  return (amount * taxPercent) / 100;
}

function buildInvoice(lineItems, { discountPercent = 0, taxPercent = 0 } = {}) {
  for (const it of lineItems) {
    if (typeof it.price !== "number" || typeof it.qty !== "number") {
      throw new TypeError("each line item needs numeric price and qty");
    }
  }
  const subtotal = computeSubtotal(lineItems);
  const discounted = applyDiscount(subtotal, discountPercent);
  const tax = computeTax(discounted, taxPercent);
  const total = Math.round((discounted + tax) * 100) / 100;
  return { subtotal, discount: subtotal - discounted, tax, total };
}

module.exports = { buildInvoice, computeSubtotal, computeTax };
