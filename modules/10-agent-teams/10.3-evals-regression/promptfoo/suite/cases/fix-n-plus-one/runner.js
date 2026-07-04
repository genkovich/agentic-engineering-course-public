// Довірений раннер для кейса fix-n-plus-one (копіюється у пісочницю в check.sh,
// щоб агент не міг його «підправити»). Виконує buildReport на фіксованих даних і
// перевіряє: (1) рядки коректні, (2) кількість SQL-викликів ≤ 2 (N+1 усунено).
const db = require("./db");
const { buildReport } = require("./report");

const orders = [
  { id: 1, userId: 1 },
  { id: 2, userId: 2 },
  { id: 3, userId: 3 },
  { id: 4, userId: 1 },
  { id: 5, userId: 3 },
];

db.resetCount();
const rows = buildReport(orders);
const queries = db.getCount();

// Коректність: 5 рядків, кожен з іменем користувача.
const expected = { 1: "Ada", 2: "Linus", 3: "Grace", 4: "Ada", 5: "Grace" };
let correct = rows.length === orders.length;
for (const r of rows) {
  if (!r || expected[r.order] !== r.user) correct = false;
}

console.log(`rows=${rows.length} queries=${queries} correct=${correct}`);

if (!correct) {
  console.error("FAIL: звіт некоректний (рядки/імена не збігаються).");
  process.exit(2);
}
if (queries > 2) {
  console.error(`FAIL: ${queries} SQL-викликів (>2) — N+1 не усунено.`);
  process.exit(1);
}
process.exit(0);
