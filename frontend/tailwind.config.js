/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        saju: {
          bg:      '#06030f',
          bg2:     '#0e0820',
          gold:    '#c9922a',
          goldL:   '#e8bc60',
          goldD:   '#7a560f',
          crimson: '#8b1535',
          purple:  '#4a2070',
          text:    '#ede4ce',
          textDim: '#8a7a60',
        },
      },
      fontFamily: {
        myeongjo: ['Nanum Myeongjo', 'serif'],
        cinzel:   ['Cinzel', 'serif'],
      },
    },
  },
  plugins: [],
}
