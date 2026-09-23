import { getCollection, type CollectionEntry } from 'astro:content';
import { slugify } from './utils';

/** Drafts are shown in `astro dev` only. */
const published = ({ data }: { data: { draft: boolean } }) => import.meta.env.DEV || !data.draft;

const byDateDesc = <T extends { data: { date: Date } }>(a: T, b: T) =>
  b.data.date.valueOf() - a.data.date.valueOf();

export async function getWriteups() {
  return (await getCollection('writeups', published)).sort(byDateDesc);
}

export async function getProjects() {
  return (await getCollection('projects', published)).sort(
    (a, b) => a.data.order - b.data.order || byDateDesc(a, b),
  );
}

/** Sort key for entries that may only have a year. */
const when = (d: { year: number; date?: Date }) => d.date?.valueOf() ?? Date.UTC(d.year, 0, 1);
const byYearDesc = <T extends { data: { year: number; date?: Date } }>(a: T, b: T) => when(b.data) - when(a.data);

export async function getCompetitions() {
  return (await getCollection('ctf', published)).sort(byYearDesc);
}

export async function getAchievements() {
  return (await getCollection('achievements', published)).sort(byYearDesc);
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
const COMPETITION_EVENTS = new Set(['EcowsCTF']);

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
