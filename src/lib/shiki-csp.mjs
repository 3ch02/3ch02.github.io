// @ts-check
/**
 * Makes Shiki syntax highlighting compatible with the Content-Security-Policy.
 *
 * Shiki colours tokens with inline `style="color:#…"` attributes, which a
 * hash-based `style-src` (what Astro's `security.csp` generates) blocks.
 * The transformer below swaps those attributes for classes, and the Vite
 * plugin serves the matching stylesheet, generated from the theme itself so
 * it always stays in sync with `shikiConfig.theme`.
 */
import { bundledThemes } from 'shiki';

/** @param {string} color */
const colorClass = (color) => `sh-${color.replace('#', '').toLowerCase()}`;

/** @type {import('shiki').ShikiTransformer} */
export const styleToClass = {
  name: 'csp-style-to-class',
  pre(node) {
    delete node.properties.style;
  },
  span(node) {
    const style = node.properties.style;
    if (typeof style !== 'string') return;
    for (const declaration of style.split(';')) {
      const [prop, value] = declaration.split(':').map((s) => s.trim().toLowerCase());
      if (prop === 'color' && value) this.addClassToHast(node, colorClass(value));
      else if (prop === 'font-style' && value === 'italic') this.addClassToHast(node, 'sh-i');
      else if (prop === 'font-weight' && value === 'bold') this.addClassToHast(node, 'sh-b');
      else if (prop === 'text-decoration' && value === 'underline') this.addClassToHast(node, 'sh-u');
    }
    delete node.properties.style;
  },
};

const VIRTUAL_ID = 'virtual:shiki-theme.css';
const RESOLVED_ID = `\0${VIRTUAL_ID}`;

/**
 * Serves `virtual:shiki-theme.css`: one class per colour used by the theme.
 * @param {keyof typeof bundledThemes} themeName
 * @returns {import('vite').Plugin}
 */
export function shikiThemeCss(themeName) {
  return {
    name: 'shiki-theme-css',
    resolveId(id) {
      return id === VIRTUAL_ID ? RESOLVED_ID : undefined;
    },
    async load(id) {
      if (id !== RESOLVED_ID) return;
      const { default: theme } = await bundledThemes[themeName]();
      const fg = theme.colors?.['editor.foreground'] ?? theme.fg ?? '#adbac7';
      const bg = theme.colors?.['editor.background'] ?? theme.bg ?? '#22272e';

      const colors = new Set([fg.toLowerCase()]);
      for (const rule of theme.tokenColors ?? []) {
        const color = rule.settings?.foreground;
        if (color) colors.add(color.toLowerCase());
      }

      return [
        `.astro-code{background-color:${bg};color:${fg}}`,
        ...[...colors].map((c) => `.${colorClass(c)}{color:${c}}`),
        '.sh-i{font-style:italic}.sh-b{font-weight:700}.sh-u{text-decoration:underline}',
      ].join('\n');
    },
  };
}
