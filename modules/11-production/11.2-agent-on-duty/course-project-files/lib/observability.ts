import {
  Counter,
  Histogram,
  Registry,
  collectDefaultMetrics,
} from "prom-client";

type Metrics = {
  registry: Registry;
  requests: Counter<"method" | "route" | "status">;
  duration: Histogram<"method" | "route" | "status">;
};

const globalMetrics = globalThis as typeof globalThis & {
  courseProjectMetrics?: Metrics;
};

function createMetrics(): Metrics {
  const registry = new Registry();
  registry.setDefaultLabels({ service: "course-project" });
  collectDefaultMetrics({
    register: registry,
    prefix: "course_project_",
  });

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

export async function observeRequest(
  method: string,
  route: string,
  handler: () => Promise<Response>
): Promise<Response> {
  const startedAt = process.hrtime.bigint();
  let status = 500;

  try {
    const response = await handler();
    status = response.status;
    return response;
  } catch (error) {
    console.error(
      JSON.stringify({
        level: "error",
        event: "request_failed",
        method,
        route,
        status,
        release: process.env.RELEASE_SHA ?? "local",
        message: error instanceof Error ? error.message : "unknown error",
      })
    );
    throw error;
  } finally {
    const seconds = Number(process.hrtime.bigint() - startedAt) / 1e9;
    const labels = { method, route, status: String(status) };
    metrics.requests.inc(labels);
    metrics.duration.observe(labels, seconds);
    console.log(
      JSON.stringify({
        level: status >= 500 ? "error" : "info",
        event: "request_completed",
        method,
        route,
        status,
        duration_ms: Math.round(seconds * 1000),
        release: process.env.RELEASE_SHA ?? "local",
      })
    );
  }
}
