"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

type Track = {
  id: string;
  title: string;
  artist: string;
  artwork?: string;
  preview_url?: string;
  external_url?: string;
};

type Selected = Track & {
  tempo: number;
  bright: number;
  electro: number;
  explore: number;
};

function Slider({
  label,
  value,
  onChange,
  left,
  right,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  left: string;
  right: string;
}) {
  return (
    <div style={{ marginTop: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, opacity: 0.8 }}>
        <span>{label}</span>
        <span>
          {left} ←→ {right}
        </span>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        value={Math.round(value * 100)}
        onChange={(e) => onChange(Number(e.target.value) / 100)}
        style={{ width: "100%" }}
      />
    </div>
  );
}

export default function DiagnosisPage() {
  const router = useRouter();

  const [q, setQ] = useState("");
  const [results, setResults] = useState<Track[]>([]);
  const [selected, setSelected] = useState<Selected[]>([]);
  const [msg, setMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const didInit = useRef(false); // StrictMode / Turbopack対策
  const canDiagnose = selected.length >= 5;

  // ✅ APIに送るpayloadをここで確定させる（これが「完全版」の肝）
  const payload = {
    username: "test", // 本番は入力欄を作って変えられるようにしてもOK
    tracks: selected.map((t) => ({
      id: t.id,
      title: t.title,
      artist: t.artist,
      artwork: t.artwork,
      preview_url: t.preview_url,
      external_url: t.external_url,
      tempo: t.tempo,
      bright: t.bright,
      electro: t.electro,
      explore: t.explore,
    })),
  };

  async function fetchTracks(query: string) {
    setIsLoading(true);
    setMsg("");
    try {
      const res = await fetch(`/api/tracks/search?q=${encodeURIComponent(query)}`, {
        cache: "no-store",
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setMsg(`search failed: ${JSON.stringify(data, null, 2)}`);
        setResults([]);
        return;
      }
      setResults(Array.isArray(data.items) ? data.items : []);
    } catch (e: any) {
      setMsg(`search error: ${e?.message ?? String(e)}`);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    if (didInit.current) return;
    didInit.current = true;

    (async () => {
      try {
        // devログイン（cookie確保） ※今はダミーでもOK
        const loginRes = await fetch("/api/dev/login", { credentials: "include" });
        if (!loginRes.ok) {
          setMsg(`login failed: ${await loginRes.text()}`);
          return;
        }

        // 初期おすすめ（空検索）
        await fetchTracks("");
      } catch (e: any) {
        setMsg(`init error: ${e?.message ?? String(e)}`);
      }
    })();
  }, []);

  function addTrack(t: Track) {
    if (selected.some((x) => x.id === t.id)) return;
    setSelected((prev) => [
      ...prev,
      { ...t, tempo: 0.5, bright: 0.5, electro: 0.5, explore: 0.5 },
    ]);
  }

  function removeTrack(id: string) {
    setSelected((prev) => prev.filter((t) => t.id !== id));
  }

  function updateTrack(id: string, patch: Partial<Selected>) {
    setSelected((prev) => prev.map((t) => (t.id === id ? { ...t, ...patch } : t)));
  }

  async function diagnose() {
    if (!canDiagnose) {
      setMsg("5曲以上選んでください");
      return;
    }

    setMsg("診断中...");
    try {
      const res = await fetch("/api/diagnose_from_tracks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        credentials: "include",
      });

      const data = await res.json().catch(() => ({}));

      // ✅ 失敗レスポンスはここで止める
      if (!res.ok || !data?.result_path) {
        setMsg(data?.message ?? data?.error ?? "diagnose failed");
        return;
      }

      router.replace(data.result_path);
    } catch (e: any) {
      setMsg(`diagnose error: ${e?.message ?? String(e)}`);
    }
  }

  return (
    <main style={{ padding: 24, maxWidth: 900, margin: "0 auto" }}>
      <h1>診断する（好きな曲を選ぶ）</h1>
      <p style={{ opacity: 0.8 }}>
        曲を追加して診断できます（初期はおすすめ表示）。最低5曲がおすすめ。
      </p>

      <section style={{ marginTop: 18 }}>
        <h2>曲を検索</h2>

        <div style={{ display: "flex", gap: 10 }}>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") fetchTracks(q.trim());
            }}
            placeholder="曲名 / アーティスト（例：YOASOBI）"
            style={{ flex: 1, padding: 10, borderRadius: 10, border: "1px solid #ddd" }}
          />
          <button
            onClick={() => fetchTracks(q.trim())}
            style={{
              padding: "10px 14px",
              borderRadius: 10,
              border: "1px solid #ddd",
              background: "white",
              fontWeight: 800,
              cursor: "pointer",
            }}
          >
            検索
          </button>
        </div>

        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.7 }}>
          {isLoading ? "読み込み中..." : "（初期表示はおすすめです）"}
        </div>

        {msg ? (
          <pre
            style={{
              marginTop: 10,
              padding: 12,
              borderRadius: 12,
              background: "#fafafa",
              border: "1px solid #eee",
              whiteSpace: "pre-wrap",
            }}
          >
            {msg}
          </pre>
        ) : null}

        <div style={{ marginTop: 12, display: "flex", flexDirection: "column", gap: 10 }}>
          {results.map((t) => (
            <div
              key={t.id}
              style={{
                border: "1px solid #eee",
                borderRadius: 14,
                padding: 12,
                background: "white",
                display: "flex",
                gap: 12,
                alignItems: "center",
              }}
            >
              {t.artwork ? (
                <img
                  src={t.artwork}
                  width={56}
                  height={56}
                  style={{ borderRadius: 12, objectFit: "cover" }}
                  alt=""
                />
              ) : null}

              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 900 }}>{t.title}</div>
                <div style={{ opacity: 0.7 }}>{t.artist}</div>
              </div>

              <button
                onClick={() => addTrack(t)}
                style={{
                  padding: "10px 12px",
                  borderRadius: 12,
                  border: "1px solid #ddd",
                  background: selected.some((x) => x.id === t.id) ? "#f3f3f3" : "white",
                  fontWeight: 900,
                  cursor: "pointer",
                  whiteSpace: "nowrap",
                }}
              >
                {selected.some((x) => x.id === t.id) ? "追加済み" : "追加"}
              </button>
            </div>
          ))}
        </div>
      </section>

      <section style={{ marginTop: 22 }}>
        <h2>選んだ曲（{selected.length}）</h2>

        <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 12 }}>
          {selected.map((t) => (
            <div
              key={t.id}
              style={{
                border: "1px solid #ddd",
                borderRadius: 16,
                padding: 14,
                background: "white",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                <div>
                  <div style={{ fontWeight: 900 }}>{t.title}</div>
                  <div style={{ opacity: 0.75 }}>{t.artist}</div>
                </div>
                <button
                  onClick={() => removeTrack(t.id)}
                  style={{
                    padding: "6px 10px",
                    borderRadius: 10,
                    border: "1px solid #ddd",
                    background: "white",
                    cursor: "pointer",
                  }}
                >
                  削除
                </button>
              </div>

              <Slider label="テンポ" value={t.tempo} onChange={(v) => updateTrack(t.id, { tempo: v })} left="ゆったり" right="速い" />
              <Slider label="明るさ" value={t.bright} onChange={(v) => updateTrack(t.id, { bright: v })} left="暗い" right="明るい" />
              <Slider label="質感" value={t.electro} onChange={(v) => updateTrack(t.id, { electro: v })} left="生音" right="電子" />
              <Slider label="好み傾向" value={t.explore} onChange={(v) => updateTrack(t.id, { explore: v })} left="定番" right="新規開拓" />
            </div>
          ))}
        </div>

        <div style={{ marginTop: 18, display: "flex", gap: 12, alignItems: "center" }}>
          <button
            disabled={!canDiagnose}
            onClick={diagnose}
            style={{
              padding: "12px 16px",
              borderRadius: 12,
              border: "1px solid #ddd",
              background: canDiagnose ? "black" : "#999",
              color: "white",
              fontWeight: 900,
              cursor: canDiagnose ? "pointer" : "not-allowed",
            }}
          >
            診断する
          </button>
          <span style={{ opacity: 0.75 }}>{msg}</span>
        </div>
      </section>
    </main>
  );
}

