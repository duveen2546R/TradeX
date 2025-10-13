/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class", // ✅ important line
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: "#0d1117",
        darkCard: "#161b22",
        accent: "#00c896",
      },
    },
  },
  plugins: [],
};