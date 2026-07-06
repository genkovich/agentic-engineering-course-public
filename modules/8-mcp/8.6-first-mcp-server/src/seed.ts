// seed.ts: кладе кілька демо-задач у data/tasks.json через TaskStore.
// Для deploy-проходу (лекція 8.12): після `make seed` у задеплоєного task-store
// одразу є що показати через list_tasks і /healthz, без ручного add_task.
// Йде тим самим шляхом, що й сервер: той самий клас store, той самий файл.

import { fileURLToPath } from "node:url";
import { TaskStore } from "./store.js";

const DATA_FILE = fileURLToPath(new URL("../data/tasks.json", import.meta.url));

const store = new TaskStore(DATA_FILE);
store.load();

const existing = store.listTasks("all").length;
if (existing > 0) {
  console.log(`store вже має ${existing} задач - seed пропущено`);
} else {
  store.addTask("Підготувати демо до запису", "high");
  store.addTask("Зробити рев'ю PR команди", "medium");
  store.addTask("Оновити DEPLOY.md", "low");
  console.log("seed: додано 3 демо-задачі у data/tasks.json");
}
