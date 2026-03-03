/**
 * axe-core 자동 접근성 테스트
 * WCAG 2.1 AA 수준의 자동화된 접근성 검증을 수행합니다.
 * 핵심 컴포넌트들의 접근성 위반 사항을 자동으로 감지합니다.
 */
import { describe, it, expect, vi } from "vitest";
import { render } from "@testing-library/react";
import { axe } from "vitest-axe";
import { Button } from "@/components/ui/Button";
import { StreamingText } from "@/components/writing/StreamingText";

// Mock useAnnouncer
vi.mock("@/hooks/useAnnouncer", () => ({
  useAnnouncer: () => ({
    announcePolite: vi.fn(),
    announceAssertive: vi.fn(),
  }),
}));

describe("axe-core 자동 접근성 검증", () => {
  it("Button 컴포넌트에 접근성 위반이 없다", async () => {
    const { container } = render(
      <Button variant="primary" size="md" onClick={() => {}}>
        테스트 버튼
      </Button>
    );

    const results = await axe(container);
    expect(results.violations).toHaveLength(0);
  });

  it("Button 비활성 상태에 접근성 위반이 없다", async () => {
    const { container } = render(
      <Button variant="primary" size="md" disabled>
        비활성 버튼
      </Button>
    );

    const results = await axe(container);
    expect(results.violations).toHaveLength(0);
  });

  it("StreamingText 컴포넌트에 접근성 위반이 없다", async () => {
    const { container } = render(
      <StreamingText text="AI가 생성한 텍스트입니다." isStreaming={false} />
    );

    const results = await axe(container);
    expect(results.violations).toHaveLength(0);
  });

  it("StreamingText 스트리밍 중 접근성 위반이 없다", async () => {
    const { container } = render(
      <StreamingText text="생성 중..." isStreaming={true} />
    );

    const results = await axe(container);
    expect(results.violations).toHaveLength(0);
  });

  it("여러 Button variant에 접근성 위반이 없다", async () => {
    const { container } = render(
      <div>
        <Button variant="primary" size="md" onClick={() => {}}>
          Primary
        </Button>
        <Button variant="secondary" size="md" onClick={() => {}}>
          Secondary
        </Button>
        <Button variant="ghost" size="md" onClick={() => {}}>
          Ghost
        </Button>
      </div>
    );

    const results = await axe(container);
    expect(results.violations).toHaveLength(0);
  });
});
