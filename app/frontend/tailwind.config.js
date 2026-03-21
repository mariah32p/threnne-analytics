/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        threnne: {
          bg: '#0A0A0A',      // The deep dark background
          card: '#161616',    // Slightly lighter for data cards
          accent: '#E5E5E5',  // Off-white text
          brand: '#FF3366'    // Optional: A pop of color for the charts
        }
      },
      fontFamily: {
        bebas: ['"Bebas Neue"', 'sans-serif'],
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
