import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(_req: NextRequest, { params }: { params: { username: string } }) {
  const username = decodeURIComponent(params.username);

  return NextResponse.json({
    ok: true,
    username,
    display_name: username,
    type_code: "AbcD",
    type_info: { name: "夜更かしドライブタイプ", tagline: "静かな夜に音で整う", axes: {} },
    scores: { energy: 0.62, mood: 0.44, texture: 0.71, explore: 0.39 },
    sample_tracks: [
      { title: "unknown", artist: "unknown", note: "サンプル" },
      { title: "unknown", artist: "unknown", note: "サンプル" },
      { title: "unknown", artist: "unknown", note: "サンプル" },
    ],
  });
}

