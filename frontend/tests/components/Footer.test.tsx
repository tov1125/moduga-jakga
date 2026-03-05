/**
 * Footer 컴포넌트 테스트
 */
import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { Footer } from "@/components/layout/Footer";

describe("Footer", () => {
  it("footer가 렌더링된다", () => {
    render(<Footer />);
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
  });

  it("저작권 텍스트가 포함된다", () => {
    render(<Footer />);
    expect(screen.getByText(/모두가 작가|©/)).toBeInTheDocument();
  });
});
