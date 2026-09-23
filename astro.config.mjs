// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import tailwindcss from '@tailwindcss/vite';
import { shikiThemeCss, styleToClass } from './src/lib/shiki-csp.mjs';

// SITE_URL and BASE_PATH are injected by the GitHub Pages workflow.
// Defaults target a user site (https://<user>.github.io/). For a project site
// (https://<user>.github.io/<repo>/) the workflow sets BASE_PATH=/<repo>.
const site = process.env.SITE_URL || 'https://3ch02.github.io';
const base = process.env.BASE_PATH || '/';

const codeTheme = 'github-dark-dimmed';

export default defineConfig({
  site,
  base,
  trailingSlash: 'ignore',
  integrations: [mdx(), sitemap()],
  // Content-Security-Policy <meta> with hashes of every script and style Astro emits.
  security: {
    csp: true,
  },
  markdown: {
    shikiConfig: {
      theme: codeTheme,
      wrap: false,
      // Token colours as classes instead of inline styles (blocked by the CSP).
      transformers: [styleToClass],
    },
  },
  vite: {
    plugins: [tailwindcss(), shikiThemeCss(codeTheme)],
  },
});
