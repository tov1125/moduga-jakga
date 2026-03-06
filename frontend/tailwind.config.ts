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
        /* Electric Blue 기반 primary 스케일 (#0984E3) */
        primary: {
          50: "#EBF5FF",
          100: "#D6EAFF",
          200: "#ADD6FF",
          300: "#7ABCF5",
          400: "#3D9EEB",
          500: "#0984E3",
          600: "#076EBE",
          700: "#05579A",
          800: "#044278",
          900: "#032E57",
          950: "#011C36",
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        /* Cyan Neon 기반 accent 스케일 (#00CEC9) */
        accent: {
          50: "#ECFFFE",
          100: "#CFFCFB",
          200: "#A0F7F5",
          300: "#63F0EC",
          400: "#00CEC9",
          500: "#00B5B1",
          600: "#009995",
          700: "#007C79",
          800: "#006160",
          900: "#004544",
          950: "#002928",
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        /* Night Black 기반 gray 스케일 — gray-900=#1E272E, gray-50=#F5F6FA */
        gray: {
          50: "#F5F6FA",
          100: "#E8EBF0",
          200: "#D0D5DE",
          300: "#AAB2C0",
          400: "#7D879A",
          500: "#5A6474",
          600: "#404958",
          700: "#303844",
          800: "#262D37",
          900: "#1E272E",
          950: "#151B22",
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
        blink: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        blink: "blink 1s step-end infinite",
      },
    },
  },
  plugins: [tailwindcssAnimate],
};

export default config;
