// Зводить події у денний дайджест. Сам код детермінований і коректний —
// це доводить зелений тест нижче. Flaky-поведінка живе ВИКЛЮЧНО в тестах, що
// спираються на pickSample (Math.random) і на поточний час.
function summarize(events) {
  return {
    count: events.length,
    total: events.reduce((sum, e) => sum + (e.amount || 0), 0),
  };
}

// Навмисно недетерміноване семплування — джерело flaky-поведінки в тесті.
function pickSample(items) {
  return items.filter(() => Math.random() > 0.5);
}

module.exports = { summarize, pickSample };
