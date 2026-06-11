// Черга подій: in-memory масив + персист у JSON-файл.
// Після рестарту сервер піднімає чергу з файлу, тому події не губляться.
// Для demo цього достатньо. У production тут була б база або повноцінна черга.

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";
import type { HubEvent, HubEventKind } from "./normalize.js";

export type EventFilter = "all" | "unacked" | HubEventKind;

export class EventQueue {
  private events: HubEvent[] = [];

  constructor(private readonly file: string) {
    if (existsSync(file)) {
      try {
        const parsed = JSON.parse(readFileSync(file, "utf8"));
        if (Array.isArray(parsed)) this.events = parsed;
      } catch {
        // Битий файл не валить сервер: стартуємо з порожньої черги
        console.warn(`[queue] failed to parse ${file}, starting with empty queue`);
      }
    }
  }

  add(event: HubEvent): HubEvent {
    this.events.push(event);
    this.persist();
    return event;
  }

  list(filter: EventFilter = "all"): HubEvent[] {
    if (filter === "all") return [...this.events];
    if (filter === "unacked") return this.events.filter((e) => !e.acked);
    return this.events.filter((e) => e.kind === filter);
  }

  get(id: string): HubEvent | undefined {
    return this.events.find((e) => e.id === id);
  }

  // Повертає undefined якщо події з таким id нема. Помилку формує викликач (MCP tool).
  ack(id: string): HubEvent | undefined {
    const event = this.get(id);
    if (!event) return undefined;
    event.acked = true;
    this.persist();
    return event;
  }

  // Останні n подій, найновіші у кінці
  recent(n = 20): HubEvent[] {
    return this.events.slice(-n);
  }

  size(): number {
    return this.events.length;
  }

  private persist(): void {
    mkdirSync(dirname(this.file), { recursive: true });
    writeFileSync(this.file, JSON.stringify(this.events, null, 2) + "\n", "utf8");
  }
}
