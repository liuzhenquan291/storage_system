/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#0052D9',
          light: '#366EF4',
          lighter: '#618DFF',
        },
        background: {
          DEFAULT: '#F3F5F8',
          white: '#FFFFFF',
          light: '#F9FAFB',
        },
        text: {
          DEFAULT: '#1C2435',
          secondary: '#5E6D82',
          muted: '#8F9BB3',
        }
      },
      fontFamily: {
        sans: ['PingFang SC', 'Microsoft YaHei', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
  ],
}
