// Інструментований стаб «БД» (fixture кейса fix-n-plus-one).
// Кожен виклик findUser/findUsersByIds інкрементує лічильник запитів — так
// check.sh детерміновано бачить, чи усунено N+1.
let queryCount = 0;

const USERS = {
  1: { id: 1, name: "Ada" },
  2: { id: 2, name: "Linus" },
  3: { id: 3, name: "Grace" },
};

// Один запит на одного користувача (саме так і виникає N+1).
function findUser(id) {
  queryCount++;
  return USERS[id];
}

// Батч-запит: один виклик повертає всіх користувачів за списком id.
function findUsersByIds(ids) {
  queryCount++;
  return ids.map((i) => USERS[i]);
}

function resetCount() {
  queryCount = 0;
}
function getCount() {
  return queryCount;
}

module.exports = { findUser, findUsersByIds, resetCount, getCount };
