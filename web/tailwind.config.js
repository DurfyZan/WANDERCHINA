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
      },
      fontFamily: {
        sans: ['"DM Sans"', "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
