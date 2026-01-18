"use client";

export default function DonateButtons() {
  const url300 = process.env.NEXT_PUBLIC_DONATE_URL_300;
  const url500 = process.env.NEXT_PUBLIC_DONATE_URL_500;

  if (!url300 && !url500) return null;

  return (
    <section style={{ marginTop: 18 }}>
      <h2>応援（投げ銭）</h2>
      <p style={{ opacity: 0.75, marginTop: -6 }}>
        気に入ったらコーヒー1杯分だけでも嬉しいです。
      </p>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 10 }}>
        {url300 ? (
          <a
            href={url300}
            target="_blank"
            rel="noreferrer"
            style={{
              padding: "10px 14px",
              borderRadius: 12,
              border: "1px solid #ddd",
              background: "white",
              fontWeight: 900,
              textDecoration: "none",
            }}
          >
            300円で応援
          </a>
        ) : null}

        {url500 ? (
          <a
            href={url500}
            target="_blank"
            rel="noreferrer"
            style={{
              padding: "10px 14px",
              borderRadius: 12,
              border: "1px solid #ddd",
              background: "black",
              color: "white",
              fontWeight: 900,
              textDecoration: "none",
            }}
          >
            500円で応援
          </a>
        ) : null}
      </div>

      <div style={{ fontSize: 12, opacity: 0.6, marginTop: 8 }}>
        決済はStripeで安全に処理されます。
      </div>
    </section>
  );
}
