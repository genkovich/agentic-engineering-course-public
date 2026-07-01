// Мінімальний HTTP-сервіс (чистий node, без залежностей) для golden-task `route-auth`.
// Баг: роут /private відкритий — будь-хто отримує 200 і секретні дані.
// Завдання агента: закрити /private auth-перевіркою (Bearer secret-token),
//   лишивши /public відкритим.
//
// check.sh піднімає цей сервіс і curl-ить: /private без auth -> 401,
// /private з Bearer secret-token -> 200, /public -> 200.

const http = require("http");
const PORT = process.env.PORT || 7831;

function handler(req, res) {
  if (req.method === "GET" && req.url === "/public") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true, area: "public" }));
    return;
  }

  if (req.method === "GET" && req.url === "/private") {
    // FIXME(route-auth): тут має бути перевірка Authorization: Bearer secret-token.
    // Зараз приватний роут відкритий — це баг, який закриває агент.
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ ok: true, area: "private", data: "the-crown-jewels" }));
    return;
  }

  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ ok: false, error: "not found" }));
}

http.createServer(handler).listen(PORT, () => {
  console.log(`route fixture listening on ${PORT}`);
});
