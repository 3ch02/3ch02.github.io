/**
 * Build an internal URL: prefixes the configured base (GitHub project pages)
 * and adds the trailing slash GitHub Pages expects for directory-style pages,
 * which saves a 301 redirect on every navigation.
 */
export function url(path: string): string {
  if (/^(https?:|mailto:|#)/.test(path)) return path;
  const base = import.meta.env.BASE_URL.replace(/\/$/, '');
  const [, pathname = '', suffix = ''] = path.match(/^([^?#]*)(.*)$/) ?? [];
  let clean = pathname.startsWith('/') ? pathname : `/${pathname}`;
  if (!clean.endsWith('/') && !/\.[a-z0-9]+$/i.test(clean)) clean += '/';
  return `${base}${clean}${suffix}`;
}

/** Compare the current pathname with a nav link (already built with `href()`); `exact` for the home link. */
export function isActive(pathname: string, target: string, exact = false): boolean {
  const t = target.replace(/\/$/, '');
  const current = pathname.replace(/\/$/, '');
  return current === t || (!exact && current.startsWith(`${t}/`));
}

export function slugify(value: string): string {
  return value
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

type Lang = 'en' | 'fr';
const intl = { en: 'en-GB', fr: 'fr-FR' } as const;
const fmt = (lang: Lang, day: boolean) =>
  new Intl.DateTimeFormat(intl[lang], { ...(day && { day: '2-digit' }), month: 'short', year: 'numeric', timeZone: 'UTC' });
const dateFmt = { en: fmt('en', true), fr: fmt('fr', true) };
const monthFmt = { en: fmt('en', false), fr: fmt('fr', false) };

export const formatDate = (d: Date, lang: Lang = 'en') => dateFmt[lang].format(d);
export const formatMonth = (d: Date, lang: Lang = 'en') => monthFmt[lang].format(d);
export const formatNumber = (n: number, lang: Lang = 'en') => n.toLocaleString(intl[lang]);
export const isoDate = (d: Date) => d.toISOString().slice(0, 10);

/** Rough reading time from raw markdown. */
export function readingTime(body: string | undefined): number {
  if (!body) return 1;
  const words = body
    .replace(/```[\s\S]*?```/g, ' code ')
    .split(/\s+/)
    .filter(Boolean).length;
  return Math.max(1, Math.round(words / 200));
}
