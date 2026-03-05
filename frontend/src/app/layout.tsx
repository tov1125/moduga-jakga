import type { Metadata } from "next";
import "./globals.css";
import { ClientLayout } from "./ClientLayout";

export const metadata: Metadata = {
  title: {
    default: "모두가 작가 - AI 글쓰기 플랫폼",
    template: "%s | 모두가 작가",
  },
  description:
    "시각 장애인을 위한 AI 기반 글쓰기 플랫폼. 음성 인식과 AI의 도움으로 누구나 작가가 될 수 있습니다.",
  keywords: ["글쓰기", "AI", "시각 장애인", "접근성", "음성 인식", "TTS", "STT"],
  authors: [{ name: "모두가 작가 팀" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" dir="ltr" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#2563eb" />
      </head>
      <body className="min-h-screen flex flex-col antialiased">
        <ClientLayout>{children}</ClientLayout>
      </body>
    </html>
  );
}
