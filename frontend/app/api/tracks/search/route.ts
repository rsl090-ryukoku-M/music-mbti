import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const q = req.nextUrl.searchParams.get("q") ?? "";
  if (!q.trim()) return NextResponse.json({ items: [] });

  const url = new URL("https://itunes.apple.com/search");
  url.searchParams.set("term", q);
  url.searchParams.set("country", "JP");
  url.searchParams.set("media", "music");
  url.searchParams.set("entity", "song");
  url.searchParams.set("limit", "25");

  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) {
    return NextResponse.json(
      { error: "itunes_fetch_failed", status: res.status },
      { status: 500 }
    );
  }

  const data = await res.json();
  const items = (data?.results ?? []).map((r: any) => ({
    id: String(r.trackId),
    title: r.trackName,
    artist: r.artistName,
    artwork: r.artworkUrl100,
    preview_url: r.previewUrl,
    external_url: r.trackViewUrl,
  }));

  return NextResponse.json({ items });
}
