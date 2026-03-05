import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import PrivacyPage from "@/app/privacy/page";

describe("PrivacyPage", () => {
  it("페이지 제목이 렌더링된다", () => {
    render(<PrivacyPage />);
    expect(screen.getByRole("heading", { level: 1, name: "개인정보처리방침" })).toBeInTheDocument();
  });

  it("6개 조항 heading이 모두 표시된다", () => {
    render(<PrivacyPage />);
    expect(screen.getByText("제1조 (수집하는 개인정보)")).toBeInTheDocument();
    expect(screen.getByText("제2조 (음성 데이터 처리)")).toBeInTheDocument();
    expect(screen.getByText("제3조 (장애 정보의 처리)")).toBeInTheDocument();
    expect(screen.getByText("제4조 (개인정보의 보유 및 이용 기간)")).toBeInTheDocument();
    expect(screen.getByText("제5조 (이용자의 권리)")).toBeInTheDocument();
    expect(screen.getByText("제6조 (개인정보의 안전성 확보 조치)")).toBeInTheDocument();
  });

  it("article 요소로 감싸져 있다", () => {
    render(<PrivacyPage />);
    expect(screen.getByRole("article")).toBeInTheDocument();
  });

  it("시행일이 표시된다", () => {
    render(<PrivacyPage />);
    expect(screen.getByText(/시행일: 2026년 3월 1일/)).toBeInTheDocument();
  });
});
