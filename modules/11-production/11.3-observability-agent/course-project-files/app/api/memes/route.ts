import { NextResponse } from "next/server";
import { listMemes, listMemesByTag, saveMeme } from "@/lib/db";
import { observeRequest } from "@/lib/observability";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  return observeRequest("GET", "/api/memes", async () => {
    const tag = new URL(request.url).searchParams.get("tag");
    const memes = tag ? listMemesByTag(tag) : listMemes();
    return NextResponse.json({ memes });
  });
}

type SaveBody = {
  templateId?: unknown;
  topText?: unknown;
  bottomText?: unknown;
  tags?: unknown;
};

export async function POST(request: Request) {
  return observeRequest("POST", "/api/memes", async () => {
    let body: SaveBody;
    try {
      body = (await request.json()) as SaveBody;
    } catch {
      return NextResponse.json(
        { ok: false, error: "Invalid JSON body" },
        { status: 400 }
      );
    }

    const templateId = Number(body.templateId);
    if (!Number.isInteger(templateId) || templateId <= 0) {
      return NextResponse.json(
        { ok: false, error: "templateId must be a positive integer" },
        { status: 400 }
      );
    }

    const topText =
      typeof body.topText === "string" && body.topText.length > 0
        ? body.topText
        : null;
    const bottomText =
      typeof body.bottomText === "string" && body.bottomText.length > 0
        ? body.bottomText
        : null;
    const tags = Array.isArray(body.tags)
      ? body.tags.filter((tag): tag is string => typeof tag === "string")
      : [];

    const { id } = saveMeme({ templateId, topText, bottomText, tags });
    return NextResponse.json({ ok: true, id });
  });
}
