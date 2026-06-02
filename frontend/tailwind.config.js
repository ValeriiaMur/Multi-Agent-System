/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      // Tokens resolve to CSS variables (see index.css) so dark/light themes
      // swap by toggling a class on the app root — no per-utility duplication.
      colors: {
        bg: "var(--bg)",
        surface: "var(--surface)",
        "surface-2": "var(--surface-2)",
        bubble: "var(--bubble-coach)",
        ink: "var(--text)",
        ink2: "var(--text-2)",
        muted: "var(--muted)",
        line: "var(--line)",
        "line-soft": "var(--line-soft)",
        chip: "var(--chip)",
        track: "var(--track)",
        blue: "var(--blue)",
        good: "var(--good)",
        amber: "var(--amber)",
        cyan: "var(--cyan)",
        accent: "var(--accent)",
        "accent-14": "var(--accent-14)",
        "accent-22": "var(--accent-22)",
        "header-bg": "var(--header-bg)",
        "tabbar-bg": "var(--tabbar-bg)",
      },
      fontFamily: {
        sans: ['-apple-system', '"SF Pro Text"', "system-ui", '"Segoe UI"', "sans-serif"],
        mono: ['"Space Mono"', "ui-monospace", "monospace"],
      },
      keyframes: {
        rise: { from: { transform: "translateY(8px)" }, to: { transform: "none" } },
        blink: { "50%": { opacity: "0" } },
        bounce2: {
          "0%,80%,100%": { transform: "translateY(0)", opacity: "0.45" },
          "40%": { transform: "translateY(-4px)", opacity: "1" },
        },
        pulse2: { "0%,100%": { opacity: "1" }, "50%": { opacity: "0.4" } },
        sparkle: {
          "0%,100%": { opacity: "0.55", transform: "scale(0.9)" },
          "50%": { opacity: "1", transform: "scale(1.12)" },
        },
        tbsweep: { "0%": { left: "-45%" }, "100%": { left: "103%" } },
        tbpulse: { "0%,100%": { opacity: "0.82" }, "50%": { opacity: "1" } },
      },
      animation: {
        rise: "rise 0.4s cubic-bezier(.2,.7,.2,1) both",
        blink: "blink 0.9s steps(1) infinite",
        bounce2: "bounce2 1.1s ease-in-out infinite",
        pulse2: "pulse2 1.2s ease-in-out infinite",
        sparkle: "sparkle 1.5s ease-in-out infinite",
        tbsweep: "tbsweep 1.25s cubic-bezier(.55,0,.45,1) infinite",
        tbpulse: "tbpulse 1.7s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
