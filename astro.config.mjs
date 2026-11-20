import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://equiptracker.rk8.dev',
  vite: {
    plugins: [tailwindcss()],
  },
});
