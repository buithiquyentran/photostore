/** @type {import('tailwindcss').Config} */
import tailwindcssAnimate from "tailwindcss-animate";
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: "#E3F6F5",
        headline: "#272343",
        paragraph: "#2D334A", 
        highlight: "#FFD803",
        card: "#FFFFFE",
        newsletter: "#BAE8E8",
      },
    },
  },
  plugins: [tailwindcssAnimate],
};
