/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        space: {
          900: "#0b0f19",
          800: "#111827",
          700: "#1f2937",
          600: "#374151",
          border: "#1f293d"
        },
        gold: "#fbbf24",
        cyan: "#06b6d4"
      }
    },
  },
  plugins: [],
};
