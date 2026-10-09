# Як метрики лягають у `course-project` (видимий diff)

Ця сторінка показує **що саме змінюється в застосунку**, коли ти додаєш метрики.
`apply-to-course-project.sh` робить це одним `cp`, тому реальний diff не видно. Тут
він розписаний руками, щоб було зрозуміло, що робиш саме ти, і щоб ти зміг
інструментувати **свій** застосунок, а не тільки цей мем-генератор.

## Що таке `course-project` і що вже має бути

`course-project` - це **твій** застосунок із попередніх модулів, а не файл із цього
репозиторію. Теки `course-project-files/` - це оверлеї (kit-и), які **копіюються в
нього**. Ні deploy-kit, ні цей observability-kit не містять коду застосунку: обидва
припускають, що він уже є.

Перед метриками (після `11.2-vps-deploy`) у тебе має бути:

- [ ] Next.js застосунок (App Router: роути лежать у `app/api/*/route.ts`);
- [ ] шар роботи з базою `@/lib/db` (тут: `getDb`, `listMemes`, `saveMeme`, `getRandomTemplate` тощо);
- [ ] хоч один робочий роут, наприклад `app/api/memes/random/route.ts`;
- [ ] `/api/health` з `11.2-vps-deploy`;
- [ ] `Dockerfile.production` і `compose.vps.yml`, застосунок піднято на VPS.

Якщо це є - course-project готовий. Метрики нічого з цього не переписують, вони
лише **додають два файли** й **обгортають наявні роути**.

## Два шари змін (ось де була «половина»)

Метрики - це рівно дві незалежні речі:

| Шар | Що це | Копіюється як є? |
|---|---|---|
| **A. Машинерія** | `lib/observability.ts` + `app/api/metrics/route.ts` | так, дропається в будь-який Next.js |
| **B. Інструментація** | обгортка кожного твого роуту в `observeRequest` | ні, залежить від ТВОЇХ роутів |

Kit копіює обидва шари одразу. Але шар B у kit-і зроблений під конкретні мем-роути.
На своєму застосунку шар A береш як є, а шар B робиш руками по своїх роутах. Саме це
й було невидимо.

## Шар A: два нові файли (generic)

### `lib/observability.ts` - нове

Один реєстр метрик на процес плюс обгортка `observeRequest`, що заміряє кожен запит.
Кеш на `globalThis` потрібен, щоб hot-reload Next.js не створював реєстр двічі (інакше
`prom-client` кине «metric already registered»). `collectDefaultMetrics` додає process
metrics (RSS, CPU, event loop) з префіксом `course_project_`.

```ts
import { Counter, Histogram, Registry, collectDefaultMetrics } from "prom-client";

const globalMetrics = globalThis as typeof globalThis & { courseProjectMetrics?: Metrics };

function createMetrics() {
  const registry = new Registry();
  registry.setDefaultLabels({ service: "course-project" });
  collectDefaultMetrics({ register: registry, prefix: "course_project_" });

  const requests = new Counter({
    name: "course_project_http_requests_total",
    help: "Total completed HTTP requests",
    labelNames: ["method", "route", "status"],
    registers: [registry],
  });
  const duration = new Histogram({
    name: "course_project_http_request_duration_seconds",
    help: "HTTP request duration in seconds",
    labelNames: ["method", "route", "status"],
    buckets: [0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
    registers: [registry],
  });
  return { registry, requests, duration };
}

const metrics = globalMetrics.courseProjectMetrics ?? createMetrics();
globalMetrics.courseProjectMetrics = metrics;
export const metricsRegistry = metrics.registry;

export async function observeRequest(method, route, handler) {
  const startedAt = process.hrtime.bigint();
  let status = 500;
  try {
    const response = await handler();
    status = response.status;
    return response;
  } finally {
    const seconds = Number(process.hrtime.bigint() - startedAt) / 1e9;
    const labels = { method, route, status: String(status) };
    metrics.requests.inc(labels);
    metrics.duration.observe(labels, seconds);
    console.log(JSON.stringify({ level: status >= 500 ? "error" : "info", event: "request_completed", method, route, status, duration_ms: Math.round(seconds * 1000) }));
  }
}
```

Повна версія (з типами й обробкою помилок) - у
[`course-project-files/lib/observability.ts`](course-project-files/lib/observability.ts).

### `app/api/metrics/route.ts` - нове

Один маршрут, що віддає весь реєстр у форматі Prometheus. Його **не** обгортаємо в
`observeRequest`: endpoint метрик не має рахувати сам себе.

```ts
import { metricsRegistry } from "@/lib/observability";

export const dynamic = "force-dynamic";

export async function GET() {
  return new Response(await metricsRegistry.metrics(), {
    headers: { "Content-Type": metricsRegistry.contentType },
  });
}
```

Prometheus скрапить саме його: у `prometheus.yml` таргет - `app:3000` з `metrics_path: /api/metrics`.

## Шар B: інструментація роуту (ось той самий diff)

Тут єдина зміна на роут: додати import і обгорнути тіло хендлера в `observeRequest`.
Логіку всередині не чіпаємо. Приклад на `app/api/memes/random/route.ts`:

```diff
  import { NextResponse } from "next/server";
  import { getRandomCaption, getRandomTemplate } from "@/lib/db";
+ import { observeRequest } from "@/lib/observability";

  export const dynamic = "force-dynamic";

  export async function GET() {
-   const template = getRandomTemplate();
-   const top = getRandomCaption();
-   const bottom = getRandomCaption();
-
-   return NextResponse.json({
-     template: { id: template.id, name: template.name, imagePath: template.image_path },
-     topText: top.text,
-     bottomText: bottom.text,
-   });
+   return observeRequest("GET", "/api/memes/random", async () => {
+     const template = getRandomTemplate();
+     const top = getRandomCaption();
+     const bottom = getRandomCaption();
+
+     return NextResponse.json({
+       template: { id: template.id, name: template.name, imagePath: template.image_path },
+       topText: top.text,
+       bottomText: bottom.text,
+     });
+   });
  }
```

Те саме для роуту з кількома методами, `app/api/memes/route.ts`: кожен експортований
хендлер (`GET`, `POST`) обгортаємо окремо, передаючи свій метод і той самий шлях:

```diff
  export async function GET(request: Request) {
+   return observeRequest("GET", "/api/memes", async () => {
      const tag = new URL(request.url).searchParams.get("tag");
      const memes = tag ? listMemesByTag(tag) : listMemes();
      return NextResponse.json({ memes });
+   });
  }

  export async function POST(request: Request) {
+   return observeRequest("POST", "/api/memes", async () => {
      /* ...валідація тіла й saveMeme без змін... */
+   });
  }
```

## Загальний рецепт для будь-якого свого роуту

Три кроки, однакові для кожного роуту у **твоєму** застосунку:

1. Додай import: `import { observeRequest } from "@/lib/observability";`
2. Обгорни тіло хендлера: `return observeRequest("<МЕТОД>", "<ШЛЯХ>", async () => { ... });`
3. Усередині поверни свій `Response`/`NextResponse` як і раніше. Помилки не гаси:
   `observeRequest` сам зафіксує статус `500` у метриці й лозі, а потім прокине помилку далі.

> Важливо про мітку `route`. Клади туди **шаблон шляху** (`/api/memes/random`), а не
> реальний URL із параметрами (`/api/memes/random?tag=cats&id=42`). Інакше кожен
> унікальний URL породить окремий ряд у сховищі - це той самий cardinality explosion
> з лекції.

Endpoint `/api/metrics` і `/api/health` навмисно **не** інструментуємо: перший
віддає метрики й не рахує себе, другий - тривіальний liveness-пінг.

## Що робить `apply-to-course-project.sh` і на що зважати

Скрипт копіює шар A як є, а шар B копіює **вже інструментованими** мем-роутами,
затираючи твої `app/api/memes/route.ts` і `app/api/memes/random/route.ts`.

- Якщо твій course-project - **цей самий мем-генератор** із тими самими роутами й
  функціями `@/lib/db`, `cp` безпечний: файли еквівалентні до обгортки.
- Якщо твій застосунок **інший** (інші роути, інший шар БД), не покладайся на `cp`
  для шару B. Візьми `lib/observability.ts` і `app/api/metrics/route.ts` (шар A), а
  свої роути обгорни руками за рецептом вище.

## Перевірка

```bash
# збірка не має впасти на типах
npm run build

# локально або на VPS: метрики віддаються
curl -s http://localhost:3000/api/metrics | head -40
```

Після кількох запитів до `/api/memes/random` у виводі мають зʼявитися:

```text
course_project_http_requests_total{method="GET",route="/api/memes/random",status="200"} 3
course_project_http_request_duration_seconds_bucket{le="0.05",...} 3
course_project_process_resident_memory_bytes 5.1e+07
```

Перший рядок - твій Counter, другий - кошики Histogram, третій - process RSS із
`collectDefaultMetrics`. Якщо вони є, Prometheus їх забере, і далі працює вся решта
kit-а (Grafana, Loki, alerts, watcher, alert-worker).
