/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './inventory/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        // Paleta de colores de cafetería
        coffee: {
          50: '#fdf8f6',
          100: '#f2e8e5',
          200: '#eaddd7',
          300: '#e0cfc5',
          400: '#d2bab0',
          500: '#bfa094',
          600: '#a18072',
          700: '#977669',
          800: '#846358',
          900: '#43302b',
          950: '#3c2415'
        },
        cream: {
          50: '#fefdfb',
          100: '#fef7ed',
          200: '#feebc8',
          300: '#fbd38d',
          400: '#f6ad55',
          500: '#ed8936',
          600: '#dd6b20',
          700: '#c05621',
          800: '#9c4221',
          900: '#7c2d12'
        },
        espresso: {
          50: '#f7f3f0',
          100: '#ede4db',
          200: '#dcc7b8',
          300: '#c4a28c',
          400: '#b08968',
          500: '#8b4513',
          600: '#7c3f12',
          700: '#6b3410',
          800: '#5a2c0e',
          900: '#4a240c'
        }
      },
      fontFamily: {
        'display': ['Playfair Display', 'serif'],
        'body': ['Inter', 'system-ui', 'sans-serif'],
        'mono': ['JetBrains Mono', 'monospace']
      },
      boxShadow: {
        'warm': '0 4px 14px 0 rgba(139, 69, 19, 0.15)',
        'coffee': '0 8px 25px 0 rgba(60, 36, 21, 0.2)',
        'cream': '0 4px 14px 0 rgba(237, 137, 54, 0.1)'
      },
      backgroundImage: {
        'coffee-gradient': 'linear-gradient(135deg, #8b4513 0%, #3c2415 100%)',
        'cream-gradient': 'linear-gradient(135deg, #fef7ed 0%, #feebc8 100%)',
        'warm-gradient': 'linear-gradient(135deg, #f7f3f0 0%, #ede4db 100%)'
      }
    },
  },
  plugins: [],
}