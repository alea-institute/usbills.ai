/** @type {import('tailwindcss').Config} */


module.exports = {
  content: [
    "./templates/**/*.{j2,html}",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Noto Sans', 'sans-serif'],
        mono: ['ui-monospace', 'monospace']
      },
      colors: {
        primary: 'var(--primary)',
        'primary-hover': 'var(--primary-hover)',
        accent: 'var(--accent)',
        'accent-hover': 'var(--accent-hover)',
      },
    },
  },
  plugins: [
      require('@tailwindcss/typography'),
  ],
}