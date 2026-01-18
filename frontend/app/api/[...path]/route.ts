import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type RssItem = {
  id: string;
  name: string;
  artistName: string;
  artworkUrl100?: string;
  url?: string;
};

export async function GET() {
  // 日本のTop Songs（most-played）
  // 例: https://rss.applemarketingtools.com/api/v2/jp/music/most-played/50/songs.json
  const rssUrl = "https://rss.applemarketingtools.com/api/v2/jp/music/most-played/50/songs.json";

  const res = await fetch(rssUrl, { cache: "no-store" });
  if (!res.ok) {
    return NextResponse.json(
      { error: "rss_fetch_failed", status: res.status },
      { status: 500 }
    );
  }

  const data = await res.json();
  const results: RssItem[] = data?.feed?.results ?? [];

  // フロントが使ってる Track 形に合わせる
  const items = results.map((r) => ({
    id: String(r.id),
    title: r.name,
    artist: r.artistName,
    artwork: r.artworkUrl100,
    preview_url: undefined, // RSSはプレビューURLが無いので一旦なし（UIは「プレビューなし」表示でOK）
    external_url: r.url,
  }));

  return NextResponse.json({ items });
}
