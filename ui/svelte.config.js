import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import("@sveltejs/vite-plugin-svelte").SvelteConfig} */
export default {
  // Voir https://svelte.dev/docs#compile-time-svelte-preprocess
  // pour plus d'informations à propos des pre-processeurs
  preprocess: vitePreprocess(),
};
