/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        instagram: {
          start: '#f09433',
          mid1: '#e6683c',
          mid2: '#dc2743',
          mid3: '#cc2366',
          end: '#bc1888'
        },
        dark: {
          bg: '#121212',
          card: '#1e1e1e',
          border: '#333333',
          text: '#ffffff',
          muted: '#a3a3a3'
        }
      }
    },
  },
  plugins: [],
}
