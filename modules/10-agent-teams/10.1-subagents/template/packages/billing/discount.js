// Застосовує відсоткову знижку до ціни.
// Навмисний дрібний недолік: немає валідації percent. Понад 100 робить суму
// відʼємною, відʼємний percent перетворює знижку на націнку. Це предмет
// voting-рев'ю у Скринкасті #3 (ймовірний спільний REJECT).
function applyDiscount(price, percent) {
  return price - (price * percent) / 100;
}

module.exports = { applyDiscount };
