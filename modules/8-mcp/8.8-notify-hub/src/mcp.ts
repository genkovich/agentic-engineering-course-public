// MCP-сервер notify-hub: tools і resource поверх черги подій.
// Сервер створюється заново на кожен HTTP-запит (stateless режим транспорту),
// тому ця функція - фабрика, а не singleton.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { HUB_EVENT_KINDS } from "./normalize.js";
import type { EventFilter, EventQueue } from "./queue.js";
import { sendTelegram, type TelegramConfig } from "./telegram.js";

const FILTER_VALUES = ["all", "unacked", ...HUB_EVENT_KINDS] as const;

export function buildMcpServer(queue: EventQueue, telegram: TelegramConfig): McpServer {
  const server = new McpServer({
    name: "notify-hub",
    version: "1.0.0",
  });

  server.registerTool(
    "list_events",
    {
      title: "List CI/CD events",
      description:
        "Повертає список CI/CD подій з черги (webhooks GitHub/GitLab, нормалізовані у спільний формат). " +
        "filter: 'all' (усі), 'unacked' (ще не опрацьовані) або конкретний kind " +
        "(pr_opened, pr_merged, pr_closed, pipeline_failed, pipeline_succeeded, push, other).",
      inputSchema: {
        filter: z
          .enum(FILTER_VALUES)
          .optional()
          .describe("Фільтр: all | unacked | конкретний kind. Default: all"),
      },
    },
    async ({ filter }) => {
      const events = queue.list((filter ?? "all") as EventFilter);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ count: events.length, events }, null, 2),
          },
        ],
      };
    },
  );

  server.registerTool(
    "ack_event",
    {
      title: "Acknowledge event",
      description:
        "Позначає подію опрацьованою (acked: true). Опрацьовані події зникають з фільтра 'unacked'.",
      inputSchema: {
        id: z.string().describe("id події з list_events"),
      },
    },
    async ({ id }) => {
      const event = queue.ack(id);
      if (!event) {
        return {
          isError: true,
          content: [{ type: "text", text: `Event not found: ${id}` }],
        };
      }
      return {
        content: [{ type: "text", text: JSON.stringify(event, null, 2) }],
      };
    },
  );

  server.registerTool(
    "send_notification",
    {
      title: "Send Telegram notification",
      description:
        "Шле повідомлення у Telegram-канал через Bot API. Якщо задано event_id, до тексту додається " +
        "title і url події. Без TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID працює dry-run: повідомлення йде " +
        "у лог і data/sent.json, відповідь містить dryRun: true.",
      inputSchema: {
        text: z.string().describe("Текст повідомлення"),
        event_id: z.string().optional().describe("id події, деталі якої додати до повідомлення"),
      },
    },
    async ({ text, event_id }) => {
      let message = text;
      if (event_id) {
        const event = queue.get(event_id);
        if (!event) {
          return {
            isError: true,
            content: [{ type: "text", text: `Event not found: ${event_id}` }],
          };
        }
        message = `${text}\n\n${event.title}\n${event.url}`;
      }
      const result = await sendTelegram(telegram, message);
      if (!result.ok) {
        return {
          isError: true,
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      }
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  server.registerResource(
    "recent-events",
    "events://recent",
    {
      title: "Recent CI/CD events",
      description: "Останні 20 подій з черги текстом",
      mimeType: "text/plain",
    },
    async (uri) => {
      const events = queue.recent(20);
      const lines = events.map((e) => {
        const status = e.acked ? "acked" : "unacked";
        return `[${e.receivedAt}] (${status}) ${e.source}/${e.kind} ${e.repo}: ${e.title} ${e.url}`;
      });
      const text = lines.length > 0 ? lines.join("\n") : "(черга порожня)";
      return {
        contents: [{ uri: uri.href, mimeType: "text/plain", text }],
      };
    },
  );

  return server;
}
