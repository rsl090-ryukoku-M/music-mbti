"use client";

type Props = {
  amount300Url?: string;
  amount500Url?: string;
};

export default function DonateButtons({
  amount300Url = process.env.NEXT_PUBLIC_STRIPE_300_URL || "",
  amount500Url = process.env.NEXT_PUBLIC_STRIPE_500_URL || "",
}: Props) {
  // URLが未設定ならUI上で分かるようにする
  const missing = !amount300Url || !amount500Url;

  return (
    <div
      style={{
        marginTop: 24,
        border: "1px solid #eee",
        borderRadius: 18,
        padding: 16,
        background: "white",
      }}
    >
      <h3 style={{ fontSize: 16, fontWeight: 900, margin: 0 }}>応援（開発支援）</h3>
      <p style={{ marginTop: 8, marginBottom: 0, opacity: 0.75, lineHeight: 1.6 }}>
        このアプリが良かったら、コーヒー1杯分の応援で開発を続けられます。
        <br />
        決済はStripeの安全な画面で行われます。
      </p>

      {missing ? (
        <div
          style={{
            marginTop: 12,
            padding: 12,
            borderRadius: 12,
            border: "1px solid #f3d6d6",
            background: "#fff5f5",
            color: "#b42318",
            fontWeight: 700,
          }}
        >
          Stripeリンクが未設定です。
          <div style={{ marginTop: 6, fontWeight: 400, color: "#7a271a" }}>
            .env.local に
            <code style={{ marginLeft: 6 }}>NEXT_PUBLIC_STRIPE_300_URL</code> と
            <code style={{ marginLeft: 6 }}>NEXT_PUBLIC_STRIPE_500_URL</code>
            を設定してください。
          </div>
        </div>
      ) : (
        <div style={{ marginTop: 14, display: "grid", gap: 10 }}>
          <a
            href={amount300Url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              padding: "12px 16px",
              borderRadius: 12,
              border: "1px solid #ddd",
              textAlign: "center",
              fontWeight: 900,
              textDecoration: "none",
              display: "block",
              background: "#fafafa",
            }}
          >
            ☕ ¥300で応援する
          </a>

          <a
            href={amount500Url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              padding: "12px 16px",
              borderRadius: 12,
              border: "1px solid #ddd",
              textAlign: "center",
              fontWeight: 900,
              textDecoration: "none",
              display: "block",
              background: "#fafafa",
            }}
          >
            🚀 ¥500で応援する
          </a>

          <div style={{ fontSize: 12, opacity: 0.7, textAlign: "center" }}>
            ※ 応援は任意です（機能制限はありません）
          </div>
        </div>
      )}
    </div>
  );
}

