/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        poppins: ["Poppins", "Inter", "sans-serif"],
        serifBali: ["Georgia", "serif"]
      },
      colors: {
        baliBg: "#FAF7F2",
        baliBrown: "#5A321D",
        baliDark: "#2A160E",
        baliCream: "#EFE1CE",
        baliSoft: "#F7EFE6",
        baliBorder: "#E8DED2"
      },
      boxShadow: {
        soft: "0 10px 30px rgba(90, 50, 29, 0.08)"
      }
    }
  },
  plugins: []
};
