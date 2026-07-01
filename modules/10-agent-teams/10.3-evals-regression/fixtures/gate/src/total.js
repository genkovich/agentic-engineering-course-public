// Стаб для golden-task gate-green. Реалізації немає — гейт (`node --test`) ЧЕРВОНИЙ
// на старті (test-first). Завдання агента — реалізувати total(), щоб гейт позеленів,
// НЕ редагуючи тести.
function total(items) {
  throw new Error("not implemented");
}

module.exports = { total };
