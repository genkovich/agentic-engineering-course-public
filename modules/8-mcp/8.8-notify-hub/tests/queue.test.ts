// Тести черги: фільтри, ack, персист у файл і відновлення після "рестарту"

import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import type { HubEvent, HubEventKind } from "../src/normalize.js";
import { EventQueue } from "../src/queue.js";

let dir: string;
let file: string;

beforeEach(() => {
  dir = mkdtempSync(join(tmpdir(), "notify-hub-queue-"));
  file = join(dir, "events.json");
});

afterEach(() => {
  rmSync(dir, { recursive: true, force: true });
});

let counter = 0;
function makeEvent(kind: HubEventKind = "pr_opened"): HubEvent {
  counter += 1;
  return {
    id: `evt-${counter}`,
    source: "github",
    kind,
    title: `Event ${counter}`,
    repo: "acme/billing-api",
    url: "https://github.com/acme/billing-api",
    receivedAt: new Date().toISOString(),
    acked: false,
  };
}

describe("EventQueue", () => {
  it("add зберігає подію і персистить у файл", () => {
    const queue = new EventQueue(file);
    const event = queue.add(makeEvent());

    expect(queue.size()).toBe(1);
    expect(existsSync(file)).toBe(true);
    const onDisk = JSON.parse(readFileSync(file, "utf8"));
    expect(onDisk).toHaveLength(1);
    expect(onDisk[0].id).toBe(event.id);
  });

  it("list фільтрує: all, unacked, за kind", () => {
    const queue = new EventQueue(file);
    const a = queue.add(makeEvent("pr_opened"));
    queue.add(makeEvent("pipeline_failed"));
    queue.add(makeEvent("pipeline_failed"));
    queue.ack(a.id);

    expect(queue.list("all")).toHaveLength(3);
    expect(queue.list("unacked")).toHaveLength(2);
    expect(queue.list("pipeline_failed")).toHaveLength(2);
    expect(queue.list("pr_opened")).toHaveLength(1);
    expect(queue.list("push")).toHaveLength(0);
  });

  it("ack позначає подію і персистить зміну", () => {
    const queue = new EventQueue(file);
    const event = queue.add(makeEvent());

    const acked = queue.ack(event.id);
    expect(acked?.acked).toBe(true);

    const onDisk = JSON.parse(readFileSync(file, "utf8"));
    expect(onDisk[0].acked).toBe(true);
  });

  it("ack на неіснуючий id повертає undefined", () => {
    const queue = new EventQueue(file);
    queue.add(makeEvent());
    expect(queue.ack("no-such-id")).toBeUndefined();
  });

  it("черга відновлюється з файлу після рестарту", () => {
    const first = new EventQueue(file);
    const event = first.add(makeEvent());
    first.ack(event.id);

    // "Рестарт": новий instance читає той самий файл
    const second = new EventQueue(file);
    expect(second.size()).toBe(1);
    expect(second.get(event.id)?.acked).toBe(true);
  });

  it("битий файл не валить чергу, стартуємо з порожньої", () => {
    writeFileSync(file, "{ this is not valid json", "utf8");
    const queue = new EventQueue(file);
    expect(queue.size()).toBe(0);
  });

  it("recent повертає не більше 20 останніх подій", () => {
    const queue = new EventQueue(file);
    for (let i = 0; i < 25; i++) queue.add(makeEvent());

    const recent = queue.recent(20);
    expect(recent).toHaveLength(20);
    // Найновіша подія у кінці списку
    expect(recent[19].id).toBe(queue.list("all")[24].id);
  });
});
