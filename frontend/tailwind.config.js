/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        border: 'hsl(214.3 31.8% 91.4%)',
        input: 'hsl(214.3 31.8% 91.4%)',
        ring: 'hsl(221.2 83.2% 53.3%)',
        background: 'hsl(0 0% 100%)',
        foreground: 'hsl(222.2 84% 4.9%)',
        primary: {
          DEFAULT: 'hsl(221.2 83.2% 53.3%)',
          foreground: 'hsl(210 40% 98%)',
        },
        secondary: {
          DEFAULT: 'hsl(210 40% 96.1%)',
          foreground: 'hsl(222.2 47.4% 11.2%)',
        },
        destructive: {
          DEFAULT: 'hsl(0 84.2% 60.2%)',
          foreground: 'hsl(210 40% 98%)',
        },
        muted: {
          DEFAULT: 'hsl(210 40% 96.1%)',
          foreground: 'hsl(215.4 16.3% 46.9%)',
        },
        accent: {
          DEFAULT: 'hsl(210 40% 96.1%)',
          foreground: 'hsl(222.2 47.4% 11.2%)',
        },
        card: {
          DEFAULT: 'hsl(0 0% 100%)',
          foreground: 'hsl(222.2 84% 4.9%)',
        },
        glass: {
          DEFAULT: 'rgba(255, 255, 255, 0.85)',
          dark: 'rgba(15, 23, 42, 0.7)',
          border: 'rgba(148, 163, 184, 0.35)',
        },
        slateglass: {
          from: '#f8fafc80',
          to: '#e2e8f080',
        },
        userbubble: {
          from: '#6366f1',
          to: '#8b5cf6',
        },
      },
      borderRadius: {
        lg: '0.5rem',
        md: 'calc(0.5rem - 2px)',
        sm: 'calc(0.5rem - 4px)',
        xl: '1.25rem',
      },
      backgroundImage: {
        'user-gradient': 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
        'bot-gradient': 'linear-gradient(135deg, rgba(15,23,42,0.85) 0%, rgba(30,41,59,0.85) 100%)',
      },
      boxShadow: {
        glass: '0 20px 45px -25px rgba(15, 23, 42, 0.45)',
        float: '0 10px 25px -10px rgba(99, 102, 241, 0.35)',
      },
      backdropBlur: {
        glass: '18px',
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        'slide-up': {
          '0%': { opacity: 0, transform: 'translateY(12px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        'bounce-dots': {
          '0%, 80%, 100%': { transform: 'scale(0.6)', opacity: 0.4 },
          '40%': { transform: 'scale(1)', opacity: 1 },
        },
      },
      animation: {
        'fade-in': 'fade-in 300ms ease-out forwards',
        'slide-up': 'slide-up 350ms ease-out forwards',
        'bounce-dots': 'bounce-dots 1.4s infinite ease-in-out both',
      },
      gridTemplateColumns: {
        sidebar: 'minmax(240px, 280px) 1fr',
      },
    },
  },
  plugins: [],
};
