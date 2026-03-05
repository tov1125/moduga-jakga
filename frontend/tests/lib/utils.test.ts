/**
 * lib/utils.ts 테스트
 * cn, formatDate, formatRelativeDate, formatWordCount, genreLabel, statusLabel,
 * chapterStatusLabel, generateId, clamp 함수를 검증합니다.
 */
import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  cn,
  formatDate,
  formatRelativeDate,
  formatWordCount,
  genreLabel,
  statusLabel,
  chapterStatusLabel,
  generateId,
  clamp,
} from "@/lib/utils";

describe("cn (className merger)", () => {
  it("단일 클래스를 반환한다", () => {
    expect(cn("px-4")).toBe("px-4");
  });

  it("여러 클래스를 병합한다", () => {
    expect(cn("px-4", "py-2")).toBe("px-4 py-2");
  });

  it("Tailwind 충돌을 해결한다", () => {
    const result = cn("px-4", "px-8");
    expect(result).toBe("px-8");
  });

  it("조건부 클래스를 처리한다", () => {
    expect(cn("base", false && "hidden", "end")).toBe("base end");
  });
});

describe("formatDate", () => {
  it("날짜를 한국어 형식으로 변환한다", () => {
    const result = formatDate("2026-03-05");
    expect(result).toContain("2026");
    expect(result).toContain("3");
    expect(result).toContain("5");
  });
});

describe("formatRelativeDate", () => {
  it("방금 전을 반환한다", () => {
    const now = new Date().toISOString();
    expect(formatRelativeDate(now)).toBe("방금 전");
  });

  it("N분 전을 반환한다", () => {
    const date = new Date(Date.now() - 5 * 60 * 1000).toISOString();
    expect(formatRelativeDate(date)).toMatch(/\d+분 전/);
  });

  it("N시간 전을 반환한다", () => {
    const date = new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString();
    expect(formatRelativeDate(date)).toMatch(/\d+시간 전/);
  });

  it("N일 전을 반환한다", () => {
    const date = new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString();
    expect(formatRelativeDate(date)).toMatch(/\d+일 전/);
  });

  it("30일 이상이면 포맷된 날짜를 반환한다", () => {
    const date = new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString();
    const result = formatRelativeDate(date);
    expect(result).not.toMatch(/일 전/);
  });
});

describe("formatWordCount", () => {
  it("1000 미만: N자", () => {
    expect(formatWordCount(500)).toBe("500자");
  });

  it("1000~9999: N.N천 자", () => {
    expect(formatWordCount(3500)).toBe("3.5천 자");
  });

  it("10000 이상: N.N만 자", () => {
    expect(formatWordCount(15000)).toBe("1.5만 자");
  });
});

describe("genreLabel", () => {
  it("모든 장르에 대해 한국어 라벨을 반환한다", () => {
    expect(genreLabel("essay")).toBe("에세이");
    expect(genreLabel("novel")).toBe("소설");
    expect(genreLabel("poem")).toBe("시");
    expect(genreLabel("autobiography")).toBe("자서전");
    expect(genreLabel("children")).toBe("동화");
    expect(genreLabel("non_fiction")).toBe("논픽션");
    expect(genreLabel("other")).toBe("기타");
  });
});

describe("statusLabel", () => {
  it("모든 상태에 대해 한국어 라벨을 반환한다", () => {
    expect(statusLabel("draft")).toBe("초안");
    expect(statusLabel("writing")).toBe("집필 중");
    expect(statusLabel("editing")).toBe("편집 중");
    expect(statusLabel("designing")).toBe("디자인 중");
    expect(statusLabel("completed")).toBe("완성됨");
    expect(statusLabel("published")).toBe("출판 완료");
  });
});

describe("chapterStatusLabel", () => {
  it("모든 챕터 상태에 대해 한국어 라벨을 반환한다", () => {
    expect(chapterStatusLabel("draft")).toBe("초안");
    expect(chapterStatusLabel("writing")).toBe("작성 중");
    expect(chapterStatusLabel("completed")).toBe("완료");
    expect(chapterStatusLabel("editing")).toBe("편집 중");
    expect(chapterStatusLabel("finalized")).toBe("최종 확인");
  });
});

describe("generateId", () => {
  it("문자열을 반환한다", () => {
    const id = generateId();
    expect(typeof id).toBe("string");
    expect(id.length).toBeGreaterThan(0);
  });

  it("매번 다른 ID를 생성한다", () => {
    const id1 = generateId();
    const id2 = generateId();
    expect(id1).not.toBe(id2);
  });
});

describe("clamp", () => {
  it("범위 내 값을 그대로 반환한다", () => {
    expect(clamp(5, 0, 10)).toBe(5);
  });

  it("최솟값 이하를 최솟값으로 클램핑한다", () => {
    expect(clamp(-5, 0, 10)).toBe(0);
  });

  it("최댓값 이상을 최댓값으로 클램핑한다", () => {
    expect(clamp(15, 0, 10)).toBe(10);
  });

  it("경계값을 그대로 반환한다", () => {
    expect(clamp(0, 0, 10)).toBe(0);
    expect(clamp(10, 0, 10)).toBe(10);
  });
});
