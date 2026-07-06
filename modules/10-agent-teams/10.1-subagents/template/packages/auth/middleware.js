// Bearer-перевірка для приватних роутів. Очікує заголовок
// Authorization: Bearer <token>; токен звіряється зі стором сесій (session.js).
const { isValidToken } = require("./session");

function requireAuth(req) {
  const header = (req.headers && req.headers["authorization"]) || "";
  const match = header.match(/^Bearer (.+)$/);
  if (!match) return { ok: false, status: 401, reason: "no bearer token" };
  if (!isValidToken(match[1])) return { ok: false, status: 401, reason: "invalid or expired token" };
  return { ok: true, status: 200 };
}

module.exports = { requireAuth };
