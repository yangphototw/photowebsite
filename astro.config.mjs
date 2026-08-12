// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://yangphoto.vercel.app',
  vite: {
    plugins: [tailwindcss()]
  },
  output: 'static',
	integrations: [sitemap({
		filter: (page) => new URL(page).pathname !== '/travel/',
	})]
});
