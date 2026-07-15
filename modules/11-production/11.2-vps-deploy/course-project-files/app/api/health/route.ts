import { NextResponse } from "next/server";
import { getDb } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    getDb().prepare("SELECT 1").get();
    return NextResponse.json({
      status: "ok",
      database: "ok",
      release: process.env.RELEASE_SHA ?? "local",
    });
  } catch (error) {
    console.error(
      JSON.stringify({
        level: "error",
        event: "healthcheck_failed",
        message: error instanceof Error ? error.message : "unknown error",
      })
    );
    return NextResponse.json(
      { status: "error", database: "error" },
      { status: 503 }
    );
  }
}
