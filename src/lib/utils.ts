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

/** Compare the current pathname with a nav href, base-aware. */
export function isActive(pathname: string, href: string): boolean {
  const target = url(href).replace(/\/$/, '');
  const current = pathname.replace(/\/$/, '');
  if (href === '/') return current === target;
  return current === target || current.startsWith(`${target}/`);
}

export function slugify(value: string): string {
  return value
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

const dateFmt = new Intl.DateTimeFormat('en-GB', {
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  timeZone: 'UTC',
});
const monthFmt = new Intl.DateTimeFormat('en-GB', {
  month: 'short',
  year: 'numeric',
  timeZone: 'UTC',
});

export const formatDate = (d: Date) => dateFmt.format(d);
export const formatMonth = (d: Date) => monthFmt.format(d);
export const isoDate = (d: Date) => d.toISOString().slice(0, 10);

export function ordinal(n: number): string {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return `${n}${s[(v - 20) % 10] ?? s[v] ?? s[0]}`;
}

/** Rough reading time from raw markdown. */
export function readingTime(body: string | undefined): number {
  if (!body) return 1;
  const words = body
    .replace(/```[\s\S]*?```/g, ' code ')
    .split(/\s+/)
    .filter(Boolean).length;
  return Math.max(1, Math.round(words / 200));
}
