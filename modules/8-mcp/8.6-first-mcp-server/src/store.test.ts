// Unit-тести сховища: чиста логіка, без MCP і без транспорту.
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import * as fs from "node:fs";
import * as os from "node:os";
import * as path from "node:path";
import { TaskStore, TaskNotFoundError } from "./store.js";

describe("TaskStore (in-memory)", () => {
  let store: TaskStore;

  beforeEach(() => {
    store = new TaskStore(); // без filePath: тільки пам'ять
  });

  it("addTask створює відкриту задачу з послідовним id", () => {
    const first = store.addTask("Write lecture", "high");
    const second = store.addTask("Record screencast", "low");

    expect(first.id).toBe("task-1");
    expect(second.id).toBe("task-2");
    expect(first.status).toBe("open");
    expect(first.priority).toBe("high");
    expect(first.createdAt).toBeTruthy();
  });

  it("completeTask закриває задачу і ставить completedAt", () => {
    const task = store.addTask("Ship demo", "medium");
    const completed = store.completeTask(task.id);

    expect(completed.status).toBe("done");
    expect(completed.completedAt).toBeTruthy();
    expect(store.listTasks("done")).toHaveLength(1);
  });

  it("completeTask кидає TaskNotFoundError для неіснуючого id", () => {
    expect(() => store.completeTask("task-999")).toThrow(TaskNotFoundError);
    expect(() => store.completeTask("task-999")).toThrow('task-999');
  });

  it("listTasks фільтрує за статусом", () => {
    store.addTask("A", "low");
    const b = store.addTask("B", "high");
    store.completeTask(b.id);

    expect(store.listTasks("all")).toHaveLength(2);
    expect(store.listTasks("open").map((t) => t.title)).toEqual(["A"]);
    expect(store.listTasks("done").map((t) => t.title)).toEqual(["B"]);
  });

  it("summary рахує задачі і знаходить найстарішу відкриту", () => {
    const a = store.addTask("Oldest open", "medium");
    store.addTask("Newer open", "medium");
    const c = store.addTask("Closed", "medium");
    store.completeTask(c.id);

    const summary = store.summary();
    expect(summary.open).toBe(2);
    expect(summary.done).toBe(1);
    expect(summary.oldestOpen?.id).toBe(a.id);
  });

  it("summary без відкритих задач не має oldestOpen", () => {
    const summary = store.summary();
    expect(summary.open).toBe(0);
    expect(summary.oldestOpen).toBeUndefined();
  });
});

describe("TaskStore (persistence у JSON-файл)", () => {
  let dir: string;
  let filePath: string;

  beforeEach(() => {
    dir = fs.mkdtempSync(path.join(os.tmpdir(), "task-store-"));
    filePath = path.join(dir, "tasks.json");
  });

  afterEach(() => {
    fs.rmSync(dir, { recursive: true, force: true });
  });

  it("зберігає задачі на диск і відновлює їх після перезапуску", () => {
    const store = new TaskStore(filePath);
    store.load();
    const task = store.addTask("Survive restart", "high");
    store.completeTask(task.id);

    // "Перезапуск": новий інстанс читає той самий файл.
    const reloaded = new TaskStore(filePath);
    reloaded.load();

    const tasks = reloaded.listTasks("all");
    expect(tasks).toHaveLength(1);
    expect(tasks[0].title).toBe("Survive restart");
    expect(tasks[0].status).toBe("done");

    // Лічильник id теж відновлюється: нова задача не конфліктує зі старою.
    const next = reloaded.addTask("After restart", "low");
    expect(next.id).toBe("task-2");
  });

  it("load без файлу не падає (перший запуск)", () => {
    const store = new TaskStore(filePath);
    expect(() => store.load()).not.toThrow();
    expect(store.listTasks("all")).toHaveLength(0);
  });
});
