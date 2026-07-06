// Простий стор сесій у памʼяті: токен -> час видачі. Токен валідний, поки не
// сплив TTL. (Демо-стор; у проді це Redis або БД.) Демо-токен secret-token
// видається на старті модуля, тож у тестах він свіжий і валідний.
const TTL_MS = 15 * 60 * 1000; // 15 хвилин

const issuedAt = new Map([["secret-token", Date.now()]]);

function isValidToken(token, now = Date.now()) {
  if (!issuedAt.has(token)) return false;
  return now - issuedAt.get(token) < TTL_MS;
}

function issueToken(token, now = Date.now()) {
  issuedAt.set(token, now);
}

module.exports = { isValidToken, issueToken, TTL_MS };
