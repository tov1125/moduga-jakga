import type { Config } from "tailwindcss";
import tailwindcssAnimate from "tailwindcss-animate";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/providers/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        /* Gold 기반 primary 스케일 (Gemini 3.1 Pro 리디자인) */
        primary: {
          50: "#FAF6ED",
          100: "#F4ECDA",
          200: "#E8D7B0",
          300: "#DDC286",
          400: "#D4A843",
          500: "#C39632",
          600: "#A87B1E",
          700: "#876319",
          800: "#6B4E15",
          900: "#523C13",
          950: "#33240A",
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        accent: {
          50: "#FAF6ED",
          100: "#F4ECDA",
          200: "#E8D7B0",
          300: "#DDC286",
          400: "#D4A843",
          500: "#C39632",
          600: "#A87B1E",
          700: "#876319",
          800: "#6B4E15",
          900: "#523C13",
          950: "#33240A",
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        /* Charcoal 기반 gray 스케일 — gray-900=#2D3436, gray-200=#DFE6E9 */
        gray: {
          50: "#F4F6F7",
          100: "#EAEFF1",
          200: "#DFE6E9",
          300: "#C8D3D8",
          400: "#A1B3B9",
          500: "#7A8F97",
          600: "#5C7078",
          700: "#46555B",
          800: "#354045",
          900: "#2D3436",
          950: "#1E2324",
        },
        /* shadcn/ui CSS 변수 기반 색상 */
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
      },
      fontSize: {
        base: ["1.125rem", { lineHeight: "1.75rem" }],
        lg: ["1.25rem", { lineHeight: "1.875rem" }],
        xl: ["1.375rem", { lineHeight: "2rem" }],
        "2xl": ["1.625rem", { lineHeight: "2.25rem" }],
        "3xl": ["2rem", { lineHeight: "2.5rem" }],
        "4xl": ["2.5rem", { lineHeight: "3rem" }],
      },
      spacing: {
        touch: "2.75rem",
      },
      minHeight: {
        touch: "2.75rem",
      },
      minWidth: {
        touch: "2.75rem",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [tailwindcssAnimate],
};

export default config;
