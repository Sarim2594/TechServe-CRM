/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          800: "#172554",
          900: "#0f1d3d",
        },
      },
    },
  },
  plugins: [],
};
