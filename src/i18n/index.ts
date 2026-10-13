import { url } from '@/lib/utils';
import { ui } from './ui';

/**
 * Two languages: English (default, no URL prefix) and French (/fr/...).
 * Every page lives in src/pages/[...locale]/ and is built once per language;
 * the interface strings are in ./ui.ts.
 */
export const LOCALES = ['en', 'fr'] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = 'en';

const base = import.meta.env.BASE_URL.replace(/\/$/, '');

/** Pathname without the configured base and without the language prefix. */
function split(pathname: string): { locale: Locale; rest: string } {
  const path = pathname.startsWith(base) ? pathname.slice(base.length) : pathname;
  const match = path.match(/^\/fr(\/.*)?$/);
  return match ? { locale: 'fr', rest: match[1] ?? '/' } : { locale: DEFAULT_LOCALE, rest: path || '/' };
}

export const getLocale = (u: URL): Locale => split(u.pathname).locale;

/** "/about" → "/fr/about" for French; external links and anchors are left alone. */
export function localePath(locale: Locale, path: string): string {
  if (/^(https?:|mailto:|#)/.test(path) || locale === DEFAULT_LOCALE) return path;
  return path === '/' ? '/fr' : `/fr${path.startsWith('/') ? path : `/${path}`}`;
}

/** The same page in another language (used by the switcher and hreflang tags). */
export function switchLocale(u: URL, to: Locale): string {
  const { rest } = split(u.pathname);
  // The 404 page exists once, at the root: send the visitor to the home page instead.
  return url(localePath(to, /^\/404/.test(rest) ? '/' : rest));
}

/** `const { locale, t, href } = useI18n(Astro.url)` — strings and links for the current language. */
export function useI18n(u: URL) {
  const locale = getLocale(u);
  return { locale, t: ui[locale], href: (path: string) => url(localePath(locale, path)) };
}

type Path = { params?: Record<string, string | undefined>; props?: Record<string, unknown> };

/** getStaticPaths helper: one copy of each path per language. */
export function withLocales<T extends Path>(paths: T[] = [{} as T]) {
  return paths.flatMap((p) =>
    LOCALES.map((l) => ({ ...p, params: { ...p.params, locale: l === DEFAULT_LOCALE ? undefined : l } })),
  );
}
