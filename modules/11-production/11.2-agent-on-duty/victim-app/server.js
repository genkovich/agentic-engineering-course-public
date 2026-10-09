// Крихітний "жертва-застосунок" для демо реліз-нагляду.
// Структуровані JSON-логи в stdout + /metrics у текстовому форматі.
// Аномалія вмикається env BUGGY_RELEASE=1: кожен 3-й запит до /api/orders
// падає з 500, латентність зростає. Детерміновано, без random у помилках.

const http = require("http");

const PORT = Number(process.env.PORT || 3000);
const APP_VERSION = process.env.APP_VERSION || "1.4.2";
const BUGGY_RELEASE = process.env.BUGGY_RELEASE === "1";

let requestsTotal = 0;
let errorsTotal = 0;
let ordersCounter = 0;
let latencySum = 0;

function log(fields) {
  process.stdout.write(
    JSON.stringify({ ts: new Date().toISOString(), version: APP_VERSION, ...fields }) + "\n"
  );
}

const server = http.createServer((req, res) => {
  const started = Date.now();
  requestsTotal += 1;

  const finish = (status, body, extra = {}) => {
    const latency = Date.now() - started;
    latencySum += latency;
    if (status >= 500) errorsTotal += 1;
    res.writeHead(status, { "Content-Type": "application/json" });
    res.end(JSON.stringify(body));
    log({
      level: status >= 500 ? "error" : "info",
      route: req.url,
      method: req.method,
      status,
      latency_ms: latency,
      ...extra,
    });
  };

  if (req.url === "/healthz") {
    return finish(200, { ok: true, version: APP_VERSION });
  }

  if (req.url === "/metrics") {
    const avg = requestsTotal ? Math.round(latencySum / requestsTotal) : 0;
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end(
      [
        `app_info{version="${APP_VERSION}"} 1`,
        `http_requests_total ${requestsTotal}`,
        `http_errors_total ${errorsTotal}`,
        `http_latency_avg_ms ${avg}`,
        "",
      ].join("\n")
    );
    return;
  }

  if (req.url === "/api/orders") {
    ordersCounter += 1;
    if (BUGGY_RELEASE && ordersCounter % 3 === 0) {
      // Закладений реліз-баг: обробник читає поле, якого немає в новій схемі.
      const delay = 400;
      return setTimeout(() => {
        finish(
          500,
          { error: "internal" },
          { err: "TypeError: Cannot read properties of undefined (reading 'items')" }
        );
      }, delay);
    }
    const delay = 20 + (ordersCounter % 5) * 10;
    return setTimeout(() => {
      finish(200, { orders: [], count: 0 });
    }, delay);
  }

  return finish(404, { error: "not found" });
});

server.listen(PORT, () => {
  log({ level: "info", msg: "listening", port: PORT });
});
