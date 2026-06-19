import {defineConfig} from 'vite';
import {svelte} from '@sveltejs/vite-plugin-svelte';
import {resolve} from 'path';

const pages = {
  "tableau-de-bord": 'tableau-de-bord.html'
};

const input = Object.fromEntries(
  Object.entries(pages).map(([name, path]) => [
    name,
    resolve(`${__dirname}/pages`, path),
  ])
);

export default defineConfig({
  plugins: [svelte()],
  build: {
    rollupOptions: {
      input: {
        ...input,
        main: resolve(__dirname, 'index.html'),
      },
    },
  },
});
