import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#0b0f1a",
          subtle: "#0f1525",
          card: "#141b2d",
          elevated: "#1a2336",
        },
        border: {
          DEFAULT: "#1f2a40",
          subtle: "#28344e",
        },
        brand: {
          DEFAULT: "#6366f1",
          hover: "#4f46e5",
          soft: "#312e81",
        },
        muted: "#8a97b3",
      },
      fontFamily: {
        sans: [
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica",
          "Arial",
          "sans-serif",
        ],
      },
      boxShadow: {
        card: "0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3)",
      },
    },
  },
  plugins: [],
};

export default config;
