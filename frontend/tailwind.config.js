/** @type {import('tailwindcss').Config} */
import tailwindcssAnimate from "tailwindcss-animate";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: ["class"],
  theme: {
    extend: {
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      colors: {
        bg: "#E3F6F5",
        paragraph: "#2D334A",
        highlight: "#FFD803",
        newsletter: "#BAE8E8",
        tertiary: "#bae8e8",
        popover: "var(--popover)",
        background: "var(--background)",
        foreground: "var(--foreground)",
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        primary: {
          DEFAULT: "var(--primary)",
          foreground: "hsl(var(--primary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },

        border: "var(--border)",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        sidebar: {
          accent: "var(--sidebar-accent)",
        },
      },
    },
  },
  plugins: [tailwindcssAnimate],
};
