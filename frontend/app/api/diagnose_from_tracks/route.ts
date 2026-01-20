import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  const body = await req.json().catch(() => ({}));
  const username = String(body?.username ?? "").trim();
  const tracks = Array.isArray(body?.tracks) ? body.tracks : [];

  if (!username) {
    return NextResponse.json({ error: "need_username", message: "usernameが必要です" }, { status: 400 });
  }
  if (tracks.length < 5) {
    return NextResponse.json({ error: "need_5_tracks", message: "5曲以上選んでください" }, { status: 400 });
  }

  // ここは仮の診断（今のあなたのロジックに合わせて後で置換でOK）
  const type_code = "AbcD";
  const type_info = { name: "夜更かしドライブタイプ", tagline: "静かな夜に音で整う", axes: {} };
  const scores = { energy: 0.62, mood: 0.44, texture: 0.71, explore: 0.39 };
  const sample_tracks = tracks.slice(0, 3).map((t: any) => ({
    title: t.title ?? "unknown",
    artist: t.artist ?? "unknown",
    note: "サンプル",
  }));

  return NextResponse.json({
    ok: true,
    result_path: `/result/${encodeURIComponent(username)}`, // ★これが必須
    username,
    display_name: username,
    type_code,
    type_info,
    scores,
    sample_tracks,
  });
}

