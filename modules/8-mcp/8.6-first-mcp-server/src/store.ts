// store.ts: логіка сховища задач, повністю відокремлена від MCP-шару.
// Тут немає жодного import з SDK. Це звичайний TypeScript-клас,
// який можна тестувати без транспорту і протоколу.

import * as fs from "node:fs";
import * as path from "node:path";

export type Priority = "low" | "medium" | "high";
export type Status = "open" | "done";

export interface Task {
  id: string;
  title: string;
  priority: Priority;
  status: Status;
  createdAt: string; // ISO-дата створення
  completedAt?: string; // ISO-дата закриття, тільки для status=done
}

// Окремий клас помилки: MCP-шар ловить саме її
// і перетворює на зрозумілу відповідь для моделі.
export class TaskNotFoundError extends Error {
  constructor(public readonly id: string) {
    super(`Task with id "${id}" not found`);
    this.name = "TaskNotFoundError";
  }
}

// Формат файлу data/tasks.json: лічильник id + масив задач.
interface StoreFile {
  nextId: number;
  tasks: Task[];
}

export class TaskStore {
  private tasks = new Map<string, Task>();
  private nextId = 1;

  // filePath опціональний: без нього сховище живе тільки в пам'яті.
  // Це зручно для тестів, їм не потрібен файл на диску.
  constructor(private readonly filePath?: string) {}

  // Читає data/tasks.json якщо він є. Відсутність файлу не помилка,
  // це просто перший запуск сервера.
  load(): void {
    if (!this.filePath || !fs.existsSync(this.filePath)) {
      return;
    }
    const raw = fs.readFileSync(this.filePath, "utf8");
    const data = JSON.parse(raw) as StoreFile;
    this.nextId = data.nextId;
    this.tasks = new Map(data.tasks.map((task) => [task.id, task]));
  }

  // Після кожної зміни скидаємо стан на диск.
  // Для демо це найпростіша робоча persistence-стратегія.
  private persist(): void {
    if (!this.filePath) {
      return;
    }
    fs.mkdirSync(path.dirname(this.filePath), { recursive: true });
    const data: StoreFile = {
      nextId: this.nextId,
      tasks: [...this.tasks.values()],
    };
    fs.writeFileSync(this.filePath, JSON.stringify(data, null, 2) + "\n");
  }

  addTask(title: string, priority: Priority): Task {
    const task: Task = {
      id: `task-${this.nextId++}`,
      title,
      priority,
      status: "open",
      createdAt: new Date().toISOString(),
    };
    this.tasks.set(task.id, task);
    this.persist();
    return task;
  }

  // Кидає TaskNotFoundError для неіснуючого id.
  // Рішення "що з цим робити" приймає шар вище (MCP handler).
  completeTask(id: string): Task {
    const task = this.tasks.get(id);
    if (!task) {
      throw new TaskNotFoundError(id);
    }
    const completed: Task = {
      ...task,
      status: "done",
      completedAt: new Date().toISOString(),
    };
    this.tasks.set(id, completed);
    this.persist();
    return completed;
  }

  // "all" повертає все, інакше фільтруємо за статусом.
  listTasks(status: Status | "all" = "all"): Task[] {
    const all = [...this.tasks.values()];
    if (status === "all") {
      return all;
    }
    return all.filter((task) => task.status === status);
  }

  // Дані для resource tasks://summary:
  // кількість відкритих і закритих, найстаріша відкрита задача.
  summary(): { open: number; done: number; oldestOpen?: Task } {
    const open = this.listTasks("open");
    const done = this.listTasks("done");
    const oldestOpen = open
      .slice()
      .sort((a, b) => a.createdAt.localeCompare(b.createdAt))[0];
    return { open: open.length, done: done.length, oldestOpen };
  }
}
