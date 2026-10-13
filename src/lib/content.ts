import { getCollection, type CollectionEntry } from 'astro:content';
import { slugify } from './utils';

type Lang = 'en' | 'fr';
type Translatable = 'projects' | 'ctf' | 'achievements';

// ---------------------------------------------------------------------------
// Translations (see the `translations` collection in src/content.config.ts)
// ---------------------------------------------------------------------------

let translationIndex: Promise<Map<string, CollectionEntry<'translations'>>> | undefined;
const translations = () =>
  (translationIndex ??= getCollection('translations').then((all) => new Map(all.map((t) => [t.id, t]))));

const translationOf = async (entry: { collection: string; id: string }, lang: Lang) =>
  lang === 'en' ? undefined : (await translations()).get(`${lang}/${entry.collection}/${entry.id}`);

type Entry = { collection: string; id: string; data: Record<string, unknown> };

/** Entry with its text fields in the requested language; facts stay those of the original. */
async function localize<E extends Entry>(entry: E, lang: Lang): Promise<E> {
  const tr = await translationOf(entry, lang);
  if (!tr) return entry;
  const { stages, ...text } = tr.data;
  const data: Record<string, unknown> = { ...entry.data };
  for (const [k, v] of Object.entries(text)) if (v !== undefined && k in data) data[k] = v;
  if (stages && Array.isArray(data.stages)) {
    data.stages = data.stages.map((s: object, i: number) => ({
      ...s,
      ...Object.fromEntries(Object.entries(stages[i] ?? {}).filter(([, v]) => v)),
    }));
  }
  return { ...entry, data };
}

/** What to pass to `render()`: the translated body when there is one, the original otherwise. */
export const bodyOf = async (entry: CollectionEntry<Translatable>, lang: Lang) =>
  (await translationOf(entry, lang)) ?? entry;

const localizeAll = <E extends Entry>(entries: E[], lang: Lang) => Promise.all(entries.map((e) => localize(e, lang)));

/** Drafts are shown in `astro dev` only. */
const published = ({ data }: { data: { draft: boolean } }) => import.meta.env.DEV || !data.draft;

const byDateDesc = <T extends { data: { date: Date } }>(a: T, b: T) =>
  b.data.date.valueOf() - a.data.date.valueOf();

export async function getWriteups() {
  return (await getCollection('writeups', published)).sort(byDateDesc);
}

export async function getProjects(lang: Lang = 'en') {
  const all = (await getCollection('projects', published)).sort((a, b) => a.data.order - b.data.order || byDateDesc(a, b));
  return localizeAll(all, lang);
}

/** Sort key for entries that may only have a year. */
const when = (d: { year: number; date?: Date }) => d.date?.valueOf() ?? Date.UTC(d.year, 0, 1);
const byYearDesc = <T extends { data: { year: number; date?: Date } }>(a: T, b: T) => when(b.data) - when(a.data);

export async function getCompetitions(lang: Lang = 'en') {
  return localizeAll((await getCollection('ctf', published)).sort(byYearDesc), lang);
}

export async function getAchievements(lang: Lang = 'en') {
  return localizeAll((await getCollection('achievements', published)).sort(byYearDesc), lang);
}

export async function getCertifications() {
  return (await getCollection('certifications', published)).sort(
    (a, b) => (b.data.date?.valueOf() ?? 0) - (a.data.date?.valueOf() ?? 0),
  );
}

/** Tag -> count, sorted by count then name. */
export function countTags(entries: { data: { tags: string[] } }[]) {
  const counts = new Map<string, number>();
  for (const e of entries) for (const t of e.data.tags) counts.set(t, (counts.get(t) ?? 0) + 1);
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

export const categorySlug = (category: string) => slugify(category);

/** Write-ups belonging to a competition: explicit `competition` reference, or same `ctf` name. */
export function writeupsFor(competition: CollectionEntry<'ctf'>, writeups: CollectionEntry<'writeups'>[]) {
  return writeups.filter(
    (w) => w.data.competition?.id === competition.id || w.data.ctf === competition.data.name,
  );
}

// ---------------------------------------------------------------------------
// Competition results
// ---------------------------------------------------------------------------

export type Medal = 'gold' | 'silver' | 'bronze' | 'none';
type Stage = CollectionEntry<'ctf'>['data']['stages'][number];

export const medalFor = (rank?: number): Medal =>
  rank === 1 ? 'gold' : rank === 2 ? 'silver' : rank === 3 ? 'bronze' : 'none';

/**
 * The latest completed stage carrying a rank — this is what the site
 * presents as "the result". Upcoming stages are shown separately so a
 * qualification result can never be mistaken for a final result.
 */
export function currentResult(c: CollectionEntry<'ctf'>) {
  const completed = c.data.stages.filter((s) => s.status === 'completed' && s.rank);
  const best = completed.at(-1);
  const pending = c.data.stages.filter((s) => s.status !== 'completed');
  const isFinalResult = pending.length === 0;
  return { stage: best, pending, isFinalResult, medal: medalFor(best?.rank) };
}

export type { Stage };

// ---------------------------------------------------------------------------
// Write-up sources (the `ctf` field): competitions vs training platforms
// ---------------------------------------------------------------------------

/** Events that are competitions even without a page in src/content/ctf/ */
const COMPETITION_EVENTS = new Set(['EcowsCTF', 'boroCTF']);

/** "picoCTF 2026" → "picoCTF", "Hackropole (FCSC)" → "Hackropole", "Kali Team CTF 26" → "Kali Team CTF" */
export const sourceFamily = (ctf: string) =>
  ctf.replace(/\s*\([^)]*\)\s*$/, '').replace(/\s+'?\d{2,4}$/, '').trim();

export type Source = { name: string; slug: string; count: number; kind: 'competition' | 'platform' };

export function getSources(writeups: CollectionEntry<'writeups'>[]): Source[] {
  const map = new Map<string, Source>();
  for (const w of writeups) {
    const name = sourceFamily(w.data.ctf);
    const s: Source = map.get(name) ?? { name, slug: slugify(name), count: 0, kind: 'platform' };
    s.count++;
    if (w.data.competition || COMPETITION_EVENTS.has(name)) s.kind = 'competition';
    map.set(name, s);
  }
  return [...map.values()].sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
}
