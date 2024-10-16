/** @type {import('tailwindcss').Config} */
import daisyui from 'daisyui'
import colors from 'tailwindcss'
export default {
  mode: 'jit',
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {...colors}
    },
  },
  plugins: [daisyui],
  daisyui: {
    themes: [
      {
        cardboard: {
          "primary": "#14648C",
          "secondary": "#f6d860",
          "accent": "#37cdbe",
          "neutral": "#3d4451",
          "base-100": "#fefefe",
        },
      },
      "dark",
      "cupcake",
    ],
  },
}
