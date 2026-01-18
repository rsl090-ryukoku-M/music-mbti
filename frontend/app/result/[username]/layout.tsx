import type { Metadata } from "next";

export const dynamic = "force-dynamic";

type Props = {
  children: React.ReactNode;
  params: Promise<{ username: string }>;
};

export async function generateMetadata({ params }: { params: Promise<{ username: string }> }): Promise<Metadata> {
  const { username } = await params;

  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";
  const metadataBase = new URL(siteUrl);

  // 結果JSON（NextのAPI経由で取る）
  const res = await fetch(`${siteUrl}/api/result/${username}`, { cache: "no-store" });
  const data = await res.json().catch(() => ({}));

  const typeName = data?.type_info?.name ?? data?.type_code ?? "Music Type";
  const tagline = data?.type_info?.tagline ?? "音楽の好みからタイプ診断";
  const title = `${typeName} | Tuneee（仮）`;

  const ogImagePath = `/result/${username}/opengraph-image`;

  return {
    metadataBase,
    title,
    description: tagline,
    openGraph: {
      title,
      description: tagline,
      url: `/result/${username}`,
      siteName: "Tuneee（仮）",
      type: "website",
      images: [
        {
          url: ogImagePath,
          width: 1200,
          height: 630,
          alt: `${typeName} の結果`,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description: tagline,
      images: [ogImagePath],
    },
  };
}

export default function Layout({ children }: Props) {
  return <>{children}</>;
}

