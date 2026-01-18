import { ImageResponse } from "next/og";
import fs from "node:fs/promises";

export const runtime = "nodejs";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

async function loadJPFont(): Promise<Buffer> {
  // TTFのみ（TTCはttcfで落ちる）
  return await fs.readFile("/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf");
}

export default async function Image({
  params,
}: {
  params: Promise<{ username: string }>;
}) {
  const { username } = await params;

  const res = await fetch(`http://127.0.0.1:8000/api/result/${username}`, { cache: "no-store" });
  const data = await res.json();

  const title = data?.type_info?.name ?? data?.type_code ?? "Music Type";
  const tagline = data?.type_info?.tagline ?? "";
  const chips: string[] = data?.type_info?.axes ? Object.values(data.type_info.axes) : [];
  const display = data?.display_name ?? username;
  const code = data?.type_code ?? "";

  const sampleTracks: any[] = Array.isArray(data?.sample_tracks) ? data.sample_tracks.slice(0, 3) : [];

  const fontData = await loadJPFont();

  return new ImageResponse(
    (
      <div
        style={{
          width: "1200px",
          height: "630px",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #FFE3F1 0%, #E7F3FF 45%, #E9FFE9 100%)",
          padding: "56px",
          fontFamily: "JP",
        }}
      >
        <div
          style={{
            width: "100%",
            height: "100%",
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            borderRadius: 40,
            background: "rgba(255,255,255,0.78)",
            border: "2px solid rgba(255,255,255,0.9)",
            boxShadow: "0 30px 90px rgba(0,0,0,0.12)",
            padding: "50px",
          }}
        >
          {/* header */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <div style={{ display: "flex", fontSize: 26, opacity: 0.7 }}>Tuneee（仮）</div>
              <div style={{ display: "flex", fontSize: 18, opacity: 0.55 }}>music taste card</div>
            </div>

            <div style={{ display: "flex", gap: 10 }}>
              <div
                style={{
                  display: "flex",
                  width: 18,
                  height: 18,
                  borderRadius: 999,
                  background: "rgba(255,105,180,0.65)",
                }}
              />
              <div
                style={{
                  display: "flex",
                  width: 18,
                  height: 18,
                  borderRadius: 999,
                  background: "rgba(120,170,255,0.65)",
                }}
              />
              <div
                style={{
                  display: "flex",
                  width: 18,
                  height: 18,
                  borderRadius: 999,
                  background: "rgba(130,220,160,0.65)",
                }}
              />
            </div>
          </div>

          {/* main */}
          <div style={{ display: "flex", flexDirection: "column", marginTop: 8 }}>
            <div style={{ display: "flex", fontSize: 66, fontWeight: 900, lineHeight: 1.05 }}>
              {title}
            </div>

            <div style={{ display: "flex", fontSize: 30, marginTop: 14, opacity: 0.85 }}>
              {tagline}
            </div>

            <div style={{ display: "flex", gap: 12, marginTop: 18, flexWrap: "wrap" }}>
              {chips.map((c, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    fontSize: 24,
                    padding: "8px 14px",
                    borderRadius: 999,
                    background: "rgba(255,255,255,0.9)",
                    border: "1px solid rgba(0,0,0,0.08)",
                    boxShadow: "0 10px 22px rgba(0,0,0,0.08)",
                  }}
                >
                  {c}
                </div>
              ))}
            </div>

            {/* sample tracks */}
            <div style={{ display: "flex", flexDirection: "column", marginTop: 22, gap: 10 }}>
              <div style={{ display: "flex", fontSize: 20, opacity: 0.6 }}>代表曲（仮）</div>

              {sampleTracks.length > 0 ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {sampleTracks.map((t, i) => (
                    <div
                      key={i}
                      style={{
                        display: "flex",
                        flexDirection: "column",
                        padding: "10px 14px",
                        borderRadius: 18,
                        background: "rgba(255,255,255,0.9)",
                        border: "1px solid rgba(0,0,0,0.08)",
                      }}
                    >
                      <div style={{ display: "flex", fontSize: 24, fontWeight: 900 }}>
                        {t.title ?? "Unknown Title"}
                      </div>
                      <div style={{ display: "flex", fontSize: 18, opacity: 0.75 }}>
                        {t.artist ?? ""}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ display: "flex", fontSize: 22, opacity: 0.7 }}>（データなし）</div>
              )}
            </div>
          </div>

          {/* footer */}
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
            <div style={{ display: "flex", gap: 8, fontSize: 26, opacity: 0.75 }}>
              <span style={{ fontWeight: 800 }}>{display}</span>
              <span style={{ opacity: 0.6 }}>/ {code}</span>
            </div>

            <div style={{ display: "flex", fontSize: 18, opacity: 0.55 }}>
              {new Date().toISOString().slice(0, 10)}
            </div>
          </div>
        </div>
      </div>
    ),
    {
      ...size,
      fonts: [{ name: "JP", data: fontData, style: "normal" }],
    }
  );
}

