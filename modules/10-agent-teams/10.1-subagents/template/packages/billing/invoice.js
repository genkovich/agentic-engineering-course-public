// Збирає інвойс із позицій: субтотал -> знижка -> податок -> разом.
// Ризик округлення: округлюємо лише фінальну суму, тож на копійках сумарний
// податок може розійтися з по-позиційним округленням. Предмет для рев'ю
// (Скринкаст #3) і для воркера billing (Скринкаст #2).
const { applyDiscount } = require("./discount");

function buildInvoice(lineItems, { discountPercent = 0, taxPercent = 0 } = {}) {
  const subtotal = lineItems.reduce((sum, it) => sum + it.price * it.qty, 0);
  const discounted = applyDiscount(subtotal, discountPercent);
  const tax = (discounted * taxPercent) / 100;
  const total = discounted + tax;
  return {
    subtotal,
    discount: subtotal - discounted,
    tax,
    total: Math.round(total * 100) / 100,
  };
}

module.exports = { buildInvoice };
