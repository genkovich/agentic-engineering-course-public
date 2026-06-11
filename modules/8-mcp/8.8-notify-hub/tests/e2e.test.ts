// E2E: повний demo-flow через реальні транспорти.
// 1. POST /webhook (supertest) кладе подію у чергу
// 2. MCP-клієнт з SDK підключається до /mcp через StreamableHTTPClientTransport
// 3. list_events бачить подію → ack_event → send_notification у dry-run
// 4. Resource events://recent віддає текстовий зріз черги

import { existsSync, mkdtempSync, readFileSync, rmSync } from "node:fs";
import { createHmac } from "node:crypto";
import type { Server } from "node:http";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";
import request from "supertest";
import { afterAll, beforeAll, describe, expect, it } from "vitest";
import { createApp } from "../src/server.js";

const examplesDir = join(import.meta.dirname, "..", "examples");
const loadExample = (name: string) => readFileSync(join(examplesDir, name), "utf8");

// Дістає текст з результату tool call (контент MCP завжди масив блоків)
function textOf(result: any): string {
  const block = (result.content as Array<{ type: string; text?: string }>).find((c) => c.type === "text");
  return block?.text ?? "";
}

describe("notify-hub e2e (webhook → MCP через Streamable HTTP)", () => {
  let dataDir: string;
  let httpServer: Server;
  let baseUrl: string;
  let client: Client;

  beforeAll(async () => {
    dataDir = mkdtempSync(join(tmpdir(), "notify-hub-e2e-"));
    const { app } = createApp({ dataDir });

    // MCP-клієнту потрібен реальний TCP-порт, supertest сам по собі його не відкриває
    httpServer = app.listen(0);
    const address = httpServer.address();
    if (address === null || typeof address === "string") throw new Error("no port");
    baseUrl = `http://127.0.0.1:${address.port}`;

    client = new Client({ name: "e2e-test-client", version: "1.0.0" });
    const transport = new StreamableHTTPClientTransport(new URL(`${baseUrl}/mcp`));
    await client.connect(transport);
  });

  afterAll(async () => {
    await client?.close();
    await new Promise<void>((resolve) => httpServer?.close(() => resolve()));
    rmSync(dataDir, { recursive: true, force: true });
  });

  let eventId: string;

  it("POST /webhook приймає GitHub подію і кладе у чергу", async () => {
    const response = await request(baseUrl)
      .post("/webhook")
      .set("Content-Type", "application/json")
      .set("X-GitHub-Event", "pull_request")
      .send(loadExample("github-pr-opened.json"));

    expect(response.status).toBe(202);
    expect(response.body.ok).toBe(true);
    expect(response.body.kind).toBe("pr_opened");
    eventId = response.body.id;
  });

  it("POST /webhook без службових заголовків відхиляється", async () => {
    const response = await request(baseUrl)
      .post("/webhook")
      .set("Content-Type", "application/json")
      .send("{}");
    expect(response.status).toBe(400);
  });

  it("MCP-клієнт бачить tools сервера", async () => {
    const { tools } = await client.listTools();
    const names = tools.map((t) => t.name).sort();
    expect(names).toEqual(["ack_event", "list_events", "send_notification"]);
  });

  it("list_events повертає подію з webhook", async () => {
    const result = await client.callTool({ name: "list_events", arguments: { filter: "unacked" } });
    const parsed = JSON.parse(textOf(result));
    expect(parsed.count).toBe(1);
    expect(parsed.events[0].id).toBe(eventId);
    expect(parsed.events[0].kind).toBe("pr_opened");
    expect(parsed.events[0].source).toBe("github");
    expect(parsed.events[0].acked).toBe(false);
  });

  it("ack_event позначає подію опрацьованою", async () => {
    const result = await client.callTool({ name: "ack_event", arguments: { id: eventId } });
    expect(result.isError).toBeFalsy();
    expect(JSON.parse(textOf(result)).acked).toBe(true);

    const after = await client.callTool({ name: "list_events", arguments: { filter: "unacked" } });
    expect(JSON.parse(textOf(after)).count).toBe(0);
  });

  it("ack_event на неіснуючий id повертає помилку", async () => {
    const result = await client.callTool({ name: "ack_event", arguments: { id: "no-such-id" } });
    expect(result.isError).toBe(true);
    expect(textOf(result)).toContain("Event not found");
  });

  it("send_notification без Telegram env працює у dry-run", async () => {
    const result = await client.callTool({
      name: "send_notification",
      arguments: { text: "CI впав, подивись", event_id: eventId },
    });
    expect(result.isError).toBeFalsy();
    expect(JSON.parse(textOf(result))).toEqual({ ok: true, dryRun: true });

    // dry-run лишає слід у data/sent.json
    const sentFile = join(dataDir, "sent.json");
    expect(existsSync(sentFile)).toBe(true);
    const sent = JSON.parse(readFileSync(sentFile, "utf8"));
    expect(sent).toHaveLength(1);
    expect(sent[0].dryRun).toBe(true);
    expect(sent[0].text).toContain("CI впав, подивись");
    expect(sent[0].text).toContain("Add rate limiting to login endpoint");
  });

  it("resource events://recent віддає останні події текстом", async () => {
    const result = await client.readResource({ uri: "events://recent" });
    const content = result.contents[0];
    expect(content.mimeType).toBe("text/plain");
    expect(content.text).toContain("github/pr_opened");
    expect(content.text).toContain("acme/billing-api");
  });

  it("GET /mcp у stateless режимі відповідає 405", async () => {
    const response = await request(baseUrl).get("/mcp");
    expect(response.status).toBe(405);
  });
});

describe("перевірка підпису webhook (WEBHOOK_SECRET заданий)", () => {
  const secret = "test-secret-123";
  let dataDir: string;
  let app: ReturnType<typeof createApp>["app"];

  beforeAll(() => {
    dataDir = mkdtempSync(join(tmpdir(), "notify-hub-sig-"));
    app = createApp({ dataDir, webhookSecret: secret }).app;
  });

  afterAll(() => {
    rmSync(dataDir, { recursive: true, force: true });
  });

  it("GitHub з валідним X-Hub-Signature-256 приймається", async () => {
    const body = loadExample("github-pr-opened.json");
    const signature = `sha256=${createHmac("sha256", secret).update(body).digest("hex")}`;

    const response = await request(app)
      .post("/webhook")
      .set("Content-Type", "application/json")
      .set("X-GitHub-Event", "pull_request")
      .set("X-Hub-Signature-256", signature)
      .send(body);
    expect(response.status).toBe(202);
  });

  it("GitHub з невалідним підписом відхиляється з 401", async () => {
    const response = await request(app)
      .post("/webhook")
      .set("Content-Type", "application/json")
      .set("X-GitHub-Event", "pull_request")
      .set("X-Hub-Signature-256", "sha256=deadbeef")
      .send(loadExample("github-pr-opened.json"));
    expect(response.status).toBe(401);
  });

  it("GitLab з правильним X-Gitlab-Token приймається", async () => {
    const response = await request(app)
      .post("/webhook")
      .set("Content-Type", "application/json")
      .set("X-Gitlab-Event", "Pipeline Hook")
      .set("X-Gitlab-Token", secret)
      .send(loadExample("gitlab-pipeline-failed.json"));
    expect(response.status).toBe(202);
    expect(response.body.kind).toBe("pipeline_failed");
  });

  it("GitLab без токена відхиляється з 401", async () => {
    const response = await request(app)
      .post("/webhook")
      .set("Content-Type", "application/json")
      .set("X-Gitlab-Event", "Pipeline Hook")
      .send(loadExample("gitlab-pipeline-failed.json"));
    expect(response.status).toBe(401);
  });
});
