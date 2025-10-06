/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#0B0F17',
        card: '#0F1623',
        accent: '#6EE7F9',
        accent2: '#A78BFA',
      },
      boxShadow: {
        glass: '0 4px 30px rgba(0,0,0,0.1)'
      },
      backdropBlur: {
        xs: '2px'
      }
    },
  },
  plugins: [],
}
