import ShareXButton from "./ShareXButton";
import CopyLinkButton from "./CopyLinkButton";
import DonateButtons from "./DonateButtons";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ username: string }> };

function Bar({ label, value }: { label: string; value: number }) {
  const safe = Number.isFinite(value) ? value : 0;
  const pct = Math.round(safe * 100);

  return (
    <div style={{ margin: "10px 0" }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <span>{label}</span>
        <span>{pct}%</span>
      </div>
      <div style={{ height: 10, background: "#eee", borderRadius: 999 }}>
        <div
          style={{
            width: `${pct}%`,
            height: 10,
            background: "#333",
            borderRadius: 999,
          }}
        />
      </div>
    </div>
  );
}

export default async function ResultPage({ params }: Props) {
  const { username } = await params;

  const res = await fetch(`http://localhost:3000/api/result/${username}`, {
    cache: "no-store",
    credentials: "include",
  });
  const data = await res.json();

  if (!res.ok) {
    return (
      <main style={{ padding: 24, maxWidth: 760, margin: "0 auto" }}>
        <h1 style={{ fontSize: 28, margin: 0 }}>結果がありません</h1>
        <p style={{ opacity: 0.8 }}>先に診断を実行してください。</p>
        <pre
          style={{
            marginTop: 12,
            padding: 12,
            borderRadius: 12,
            border: "1px solid #eee",
            background: "#fafafa",
            whiteSpace: "pre-wrap",
          }}
        >
          {JSON.stringify(data, null, 2)}
        </pre>
        <div style={{ marginTop: 14 }}>
          <a href="/diagnosis">診断しにいく</a>
        </div>
      </main>
    );
  }

  // scores の形がどっちでも動くように吸収
  const scores = data.scores ?? {};
  const energy = scores.energy ?? scores.energy_score ?? 0;
  const mood = scores.mood ?? scores.mood_score ?? 0;
  const texture = scores.texture ?? scores.texture_score ?? 0;
  const explore = scores.explore ?? scores.explore_score ?? 0;

  const typeName = data.type_info?.name ?? data.type_code;
  const tagline = data.type_info?.tagline ?? "";

  // シェア用（本番は .env.local で差し替え）
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";
  const shareUrl = `${siteUrl}/result/${username}`;
  const shareText = `【${typeName}】\n${tagline}\n#Tuneee #MusicType`;

  const sampleTracks = Array.isArray(data.sample_tracks) ? data.sample_tracks : [];

  return (
    <main style={{ padding: 24, maxWidth: 760, margin: "0 auto" }}>
      {/* ヘッダー */}
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: 16,
          flexWrap: "wrap",
        }}
      >
        <div>
          <h1 style={{ fontSize: 30, margin: 0 }}>結果</h1>
          <div style={{ marginTop: 6, opacity: 0.8 }}>
            <b>{data.display_name}</b>
          </div>
        </div>

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
          <ShareXButton url={shareUrl} text={shareText} />
          <CopyLinkButton url={shareUrl} />
        </div>
      </header>

      {/* タイプ表示 */}
      <section
        style={{
          marginTop: 18,
          border: "1px solid #eee",
          borderRadius: 18,
          padding: 16,
          background: "white",
        }}
      >
        <div style={{ fontSize: 20, fontWeight: 900 }}>{typeName}</div>
        <div style={{ marginTop: 6, opacity: 0.8 }}>{tagline}</div>

        {/* 軸チップ */}
        {data.type_info?.axes ? (
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 12 }}>
            {Object.entries(data.type_info.axes).map(([k, v]) => (
              <span
                key={k}
                style={{
                  padding: "4px 10px",
                  border: "1px solid #ddd",
                  borderRadius: 999,
                  background: "#fafafa",
                  fontSize: 13,
                }}
              >
                {String(v)}
              </span>
            ))}
          </div>
        ) : null}
      </section>

      {/* スコア */}
      <section
        style={{
          marginTop: 16,
          border: "1px solid #eee",
          borderRadius: 18,
          padding: 16,
          background: "white",
        }}
      >
        <h2 style={{ margin: 0, fontSize: 18 }}>スコア</h2>
        <Bar label="Energy" value={energy} />
        <Bar label="Mood" value={mood} />
        <Bar label="Texture" value={texture} />
        <Bar label="Explore" value={explore} />
      </section>

      {/* 代表曲 */}
      <section
        style={{
          marginTop: 16,
          border: "1px solid #eee",
          borderRadius: 18,
          padding: 16,
          background: "white",
        }}
      >
        <h2 style={{ margin: 0, fontSize: 18 }}>代表曲（仮）</h2>

        {sampleTracks.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 12 }}>
            {sampleTracks.map((t: any, i: number) => (
              <div
                key={i}
                style={{
                  border: "1px solid #eee",
                  borderRadius: 14,
                  padding: 12,
                  background: "#fafafa",
                }}
              >
                <div style={{ fontWeight: 900 }}>{t.title}</div>
                <div style={{ opacity: 0.8 }}>{t.artist}</div>
                {t.note ? <div style={{ opacity: 0.7, marginTop: 6 }}>{t.note}</div> : null}
              </div>
            ))}
          </div>
        ) : (
          <pre
            style={{
              marginTop: 12,
              padding: 12,
              borderRadius: 12,
              border: "1px solid #eee",
              background: "#fafafa",
              whiteSpace: "pre-wrap",
            }}
          >
            {JSON.stringify(data.sample_track_ids, null, 2)}
          </pre>
        )}
      </section>

      {/* 投げ銭 */}
      <section style={{ marginTop: 16 }}>
        <DonateButtons />
      </section>

      {/* フッター導線 */}
      <footer style={{ marginTop: 18, display: "flex", gap: 12, flexWrap: "wrap" }}>
        <a href="/">トップへ</a>
        <a href="/diagnosis">もう一回診断する</a>
      </footer>
    </main>
  );
}

<div style={{ marginTop: 24, display: "grid", gap: 12 }}>
  <h3 style={{ fontSize: 16, fontWeight: 700 }}>応援（投げ銭）</h3>

  <a
    href="https://buy.stripe.com/XXXXXXXXXXXXXX"  // 300円リンク
    target="_blank"
    rel="noopener noreferrer"
    style={{
      padding: "12px 16px",
      borderRadius: 12,
      border: "1px solid #ddd",
      textAlign: "center",
      fontWeight: 700,
      textDecoration: "none",
      display: "block",
    }}
  >
    ¥300で応援する
  </a>

  <a
    href="https://buy.stripe.com/YYYYYYYYYYYYYY"  // 500円リンク
    target="_blank"
    rel="noopener noreferrer"
    style={{
      padding: "12px 16px",
      borderRadius: 12,
      border: "1px solid #ddd",
      textAlign: "center",
      fontWeight: 700,
      textDecoration: "none",
      display: "block",
    }}
  >
    ¥500で応援する
  </a>

  <p style={{ fontSize: 12, opacity: 0.8 }}>
    支払いはStripeの安全な決済画面で行われます。
  </p>
</div>

