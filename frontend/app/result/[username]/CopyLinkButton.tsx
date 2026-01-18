"use client";

import { useState } from "react";

export default function CopyLinkButton({ url }: { url: string }) {
  const [copied, setCopied] = useState(false);

  return (
    <button
      onClick={async () => {
        await navigator.clipboard.writeText(url);
        setCopied(true);
        setTimeout(() => setCopied(false), 1200);
      }}
      style={{
        padding: "10px 14px",
        borderRadius: 12,
        border: "1px solid #ddd",
        background: "white",
        fontWeight: 700,
        cursor: "pointer",
      }}
    >
      {copied ? "コピーしました" : "リンクをコピー"}
    </button>
  );
}

