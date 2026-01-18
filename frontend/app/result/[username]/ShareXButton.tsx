"use client";

export default function ShareXButton({
  url,
  text,
}: {
  url: string;
  text: string;
}) {
  const href =
    "https://twitter.com/intent/tweet?text=" +
    encodeURIComponent(text) +
    "&url=" +
    encodeURIComponent(url);

  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      style={{
        display: "inline-block",
        padding: "10px 14px",
        borderRadius: 12,
        border: "1px solid #ddd",
        textDecoration: "none",
        fontWeight: 700,
      }}
    >
      Xでシェア
    </a>
  );
}

