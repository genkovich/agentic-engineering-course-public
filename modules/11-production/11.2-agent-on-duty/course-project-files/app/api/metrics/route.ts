import { metricsRegistry } from "@/lib/observability";

export const dynamic = "force-dynamic";

export async function GET() {
  return new Response(await metricsRegistry.metrics(), {
    headers: { "Content-Type": metricsRegistry.contentType },
  });
}
