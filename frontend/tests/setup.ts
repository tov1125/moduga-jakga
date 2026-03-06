import "@testing-library/jest-dom/vitest";

// Mock next/navigation
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    prefetch: vi.fn(),
  }),
  usePathname: () => "/",
  useSearchParams: () => new URLSearchParams(),
}));

// Mock next/link — return proper JSX element for testing-library
vi.mock("next/link", () => {
  const React = require("react");
  return {
    default: React.forwardRef(function MockLink(
      { href, children, ...props }: Record<string, unknown>,
      ref: unknown,
    ) {
      return React.createElement("a", { href, ref, ...props }, children);
    }),
  };
});

// Mock MediaRecorder for voice tests
class MockMediaRecorder {
  state = "inactive";
  ondataavailable: ((e: unknown) => void) | null = null;
  onstop: (() => void) | null = null;
  onerror: ((e: unknown) => void) | null = null;
  start() {
    this.state = "recording";
  }
  stop() {
    this.state = "inactive";
    this.onstop?.();
  }
  static isTypeSupported() {
    return true;
  }
}
Object.defineProperty(globalThis, "MediaRecorder", {
  value: MockMediaRecorder,
});

// Mock AudioContext
class MockAudioContext {
  state = "running";
  createBufferSource() {
    return {
      buffer: null,
      playbackRate: { value: 1 },
      connect: vi.fn(),
      start: vi.fn(),
      stop: vi.fn(),
      onended: null,
    };
  }
  createBuffer() {
    return { duration: 1, getChannelData: () => new Float32Array(44100) };
  }
  decodeAudioData() {
    return Promise.resolve(this.createBuffer());
  }
  close() {
    return Promise.resolve();
  }
  get destination() {
    return {};
  }
}
Object.defineProperty(globalThis, "AudioContext", {
  value: MockAudioContext,
});

// Mock navigator.mediaDevices
Object.defineProperty(globalThis.navigator, "mediaDevices", {
  value: {
    getUserMedia: vi.fn().mockResolvedValue({
      getTracks: () => [{ stop: vi.fn() }],
    }),
  },
});

// Mock window.matchMedia
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
class MockIntersectionObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
Object.defineProperty(globalThis, "IntersectionObserver", {
  value: MockIntersectionObserver,
});

// Mock ResizeObserver (required by Radix UI)
class MockResizeObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
Object.defineProperty(globalThis, "ResizeObserver", {
  value: MockResizeObserver,
});
