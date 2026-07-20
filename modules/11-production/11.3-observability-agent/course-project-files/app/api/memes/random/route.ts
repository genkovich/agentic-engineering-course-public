import { NextResponse } from "next/server";
import { getRandomCaption, getRandomTemplate } from "@/lib/db";
import { observeRequest } from "@/lib/observability";

export const dynamic = "force-dynamic";

export async function GET() {
  return observeRequest("GET", "/api/memes/random", async () => {
    const template = getRandomTemplate();
    const top = getRandomCaption();
    const bottom = getRandomCaption();

    return NextResponse.json({
      template: {
        id: template.id,
        name: template.name,
        imagePath: template.image_path,
      },
      topText: top.text,
      bottomText: bottom.text,
    });
  });
}
