// Приймач GitHub webhook для issue-worker на сервері.
// Обов'язкова перевірка підпису X-Hub-Signature-256: endpoint дивиться
// в інтернет через тунель, тому кожен запит доводить, що він від GitHub
// і що payload не змінили дорогою.

const http = require("http");
const crypto = require("crypto");
const { spawn } = require("child_process");

const PORT = Number(process.env.PORT || 3411);
const SECRET = process.env.WEBHOOK_SECRET;

if (!SECRET) {
  console.error("WEBHOOK_SECRET is required");
  process.exit(1);
}

function log(fields) {
  process.stdout.write(JSON.stringify({ ts: new Date().toISOString(), ...fields }) + "\n");
}

function validSignature(body, header) {
  if (!header || !header.startsWith("sha256=")) return false;
  const expected =
    "sha256=" + crypto.createHmac("sha256", SECRET).update(body).digest("hex");
  const a = Buffer.from(header);
  const b = Buffer.from(expected);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

const server = http.createServer((req, res) => {
  if (req.method === "GET" && req.url === "/healthz") {
    res.writeHead(200);
    return res.end("ok");
  }

  if (req.method !== "POST" || req.url !== "/webhook") {
    res.writeHead(404);
    return res.end();
  }

  const chunks = [];
  req.on("data", (c) => chunks.push(c));
  req.on("end", () => {
    const body = Buffer.concat(chunks);

    if (!validSignature(body, req.headers["x-hub-signature-256"])) {
      log({ level: "warn", msg: "signature mismatch, dropped", ip: req.socket.remoteAddress });
      res.writeHead(401);
      return res.end();
    }

    const event = req.headers["x-github-event"];
    let payload;
    try {
      payload = JSON.parse(body.toString());
    } catch {
      res.writeHead(400);
      return res.end();
    }

    const labeled =
      event === "issues" &&
      payload.action === "labeled" &&
      payload.label && payload.label.name === "agent-ready";
    const opened =
      event === "issues" &&
      payload.action === "opened" &&
      (payload.issue.labels || []).some((l) => l.name === "agent-ready");

    if (!labeled && !opened) {
      log({ level: "info", msg: "event ignored", event, action: payload.action });
      res.writeHead(204);
      return res.end();
    }

    const number = payload.issue.number;
    log({ level: "info", msg: "issue accepted", issue: number });

    const worker = spawn("bash", ["/opt/duty/run-issue.sh", String(number)], {
      stdio: "inherit",
      detached: true,
    });
    worker.unref();

    res.writeHead(202);
    res.end(JSON.stringify({ queued: number }));
  });
});

server.listen(PORT, () => log({ level: "info", msg: "webhook receiver listening", port: PORT }));
