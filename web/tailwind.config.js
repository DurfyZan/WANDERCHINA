/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts}"],
  theme: {
    extend: {
      colors: {
        brand: { DEFAULT: "#c45c26", dark: "#9e4520" },
        surface: "#ffffff",
        muted: "#6b6560",
        canvas: "#f4f1ec",
        zen: {
          white: "#F7F6F2",
          ink: "#1A1A1A",
          "ink-light": "#2C2C2C",
          "ink-muted": "#5C5C5C",
          bamboo: "#7BA05B",
          "bamboo-light": "#A3C88B",
          "bamboo-dark": "#5F7D44",
          stone: "#E8E5DF",
          "stone-dark": "#D4D0C8",
          frost: "#F0EEE8",
        },
      },
      fontFamily: {
        sans: ['"DM Sans"', "system-ui", "sans-serif"],
        serif: ['"Noto Serif SC"', "serif"],
      },
      borderRadius: {
        zen: "24px",
      },
      boxShadow: {
        zen: "0 2px 16px rgba(0,0,0,0.04), 0 4px 32px rgba(0,0,0,0.03)",
        "zen-md": "0 4px 24px rgba(0,0,0,0.05), 0 8px 48px rgba(0,0,0,0.04)",
        "zen-lg": "0 8px 40px rgba(0,0,0,0.06), 0 16px 64px rgba(0,0,0,0.04)",
      },
    },
  },
  plugins: [],
};
