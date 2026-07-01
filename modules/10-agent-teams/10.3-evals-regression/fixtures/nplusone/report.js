const db = require("./db");

// Баг N+1: для КОЖНОГО замовлення окремий запит користувача.
// На 5 замовленнях це 5 запитів; на 1000 — 1000. Завдання агента — звести
// до одного батч-запиту (db.findUsersByIds), зберігши коректний результат.
function buildReport(orders) {
  return orders.map((o) => {
    const user = db.findUser(o.userId); // ← N окремих запитів
    return { order: o.id, user: user.name };
  });
}

module.exports = { buildReport };
