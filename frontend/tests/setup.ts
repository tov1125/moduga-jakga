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

// Mock next/link
vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
    [key: string]: unknown;
  }) => {
    return `<a href="${href}" ${Object.entries(props)
      .map(([k, v]) => `${k}="${v}"`)
      .join(" ")}>${children}</a>`;
  },
}));

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

// Mock IntersectionObserver
class MockIntersectionObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
Object.defineProperty(globalThis, "IntersectionObserver", {
  value: MockIntersectionObserver,
});
