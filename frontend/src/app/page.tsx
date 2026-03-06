import type { Metadata } from "next";
import { LandingContent } from "@/components/landing/LandingContent";

export const metadata: Metadata = {
  title: "모두가 작가 - AI 글쓰기 플랫폼",
};

export default function HomePage() {
  return <LandingContent />;
}
