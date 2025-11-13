import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./templates/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Match frontend design system
        background: 'hsl(0 0% 100%)',
        foreground: 'hsl(240 10% 3.9%)',

        primary: {
          DEFAULT: 'hsl(240 5.9% 10%)',
          foreground: 'hsl(0 0% 98%)',
        },

        muted: {
          DEFAULT: 'hsl(240 4.8% 95.9%)',
          foreground: 'hsl(240 3.8% 46.1%)',
        },

        border: 'hsl(240 5.9% 90%)',

        // Success/accent colors
        success: 'hsl(142.1 76.2% 36.3%)',

        // Neutral grays (for email compatibility)
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Helvetica Neue', 'Arial', 'sans-serif'],
        mono: ['Menlo', 'Monaco', 'Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
};

export default config;
