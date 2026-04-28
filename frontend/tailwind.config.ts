import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          primary: '#c17f3a',
          accent: '#e8875a',
          bg: '#fffaf4',
          sidebar: '#fdf3e8',
          border: '#f0dfc8',
          tint: '#fde8d0',
        },
      },
      borderRadius: {
        'bubble-ai': '4px 16px 16px 16px',
        'bubble-user': '16px 4px 16px 16px',
      },
      boxShadow: {
        card: '0 2px 8px rgba(0,0,0,0.06)',
        send: '0 2px 8px rgba(232,135,90,0.4)',
      },
    },
  },
  plugins: [],
} satisfies Config;
