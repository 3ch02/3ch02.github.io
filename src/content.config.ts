import { defineCollection, reference } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

/**
 * Content collections.
 * Drop a Markdown/MDX file in the matching folder under src/content/ and the
 * site picks it up automatically (listing, detail page, tags, categories).
 * Files whose name starts with "_" are ignored.
 */

const pattern = '**/[^_]*.{md,mdx}';

export const WRITEUP_CATEGORIES = [
  'Forensics',
  'Cryptography',
  'Web',
  'Reverse Engineering',
  'Steganography',
  'OSINT',
  'Pwn',
  'Misc',
  'Boot2Root',
] as const;

export const DIFFICULTIES = ['Easy', 'Medium', 'Hard', 'Insane'] as const;

const tags = z
  .array(z.string())
  .default([])
  .transform((list) => list.map((t) => t.trim().toLowerCase().replace(/\s+/g, '-')));

const writeups = defineCollection({
  loader: glob({ pattern, base: './src/content/writeups' }),
  schema: z.object({
    title: z.string(),
    category: z.enum(WRITEUP_CATEGORIES),
    /** Leave out when the challenge has no official difficulty */
    difficulty: z.enum(DIFFICULTIES).optional(),
    ctf: z.string(),
    /** Optional link to a competition in src/content/ctf (file name without extension) */
    competition: reference('ctf').optional(),
    date: z.coerce.date(),
    tags,
    summary: z.string().optional(),
    points: z.number().optional(),
    /** Highlighted in "Featured" sections (static replacement for "popular") */
    featured: z.boolean().default(false),
    /** Language of the article body */
    lang: z.enum(['en', 'fr']).default('en'),
    /** Drafts are visible with `npm run dev` only, never in the production build */
    draft: z.boolean().default(false),
    /** Set by scripts/import-obsidian.py — imported files are regenerated on each import */
    imported: z.boolean().default(false),
  }),
});

const projects = defineCollection({
  loader: glob({ pattern, base: './src/content/projects' }),
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    status: z.enum(['in-progress', 'completed', 'planned', 'archived']),
    date: z.coerce.date(),
    tags,
    stack: z.array(z.string()).default([]),
    repo: z.url().optional(),
    demo: z.url().optional(),
    featured: z.boolean().default(false),
    /** Lower comes first */
    order: z.number().default(100),
    draft: z.boolean().default(false),
  }),
});

const stage = z.object({
  /** e.g. "Qualification stage", "Final", "Final ranking" */
  name: z.string(),
  status: z.enum(['completed', 'ongoing', 'upcoming']),
  rank: z.number().int().positive().optional(),
  /** Number of teams, if known */
  outOf: z.number().int().positive().optional(),
  score: z.number().optional(),
  date: z.coerce.date().optional(),
  note: z.string().optional(),
});

const ctf = defineCollection({
  loader: glob({ pattern, base: './src/content/ctf' }),
  schema: z.object({
    name: z.string(),
    year: z.number().int(),
    /** Optional exact date — leave it out rather than guessing */
    date: z.coerce.date().optional(),
    /** Handle used during this competition (omit if unsure) */
    handle: z.string().optional(),
    team: z.string(),
    role: z.string().optional(),
    format: z.string().optional(),
    organizer: z.string().optional(),
    url: z.url().optional(),
    categories: z.array(z.string()).default([]),
    /** Ordered stages. The last completed stage is the "current" result. */
    stages: z.array(stage).min(1),
    draft: z.boolean().default(false),
  }),
});

const achievements = defineCollection({
  loader: glob({ pattern, base: './src/content/achievements' }),
  schema: z.object({
    title: z.string(),
    year: z.number().int(),
    date: z.coerce.date().optional(),
    /**
     * If set, placement / team / stage status are read from the CTF entry,
     * so results only need to be updated in one place.
     */
    competition: reference('ctf').optional(),
    /** Used when there is no linked competition */
    headline: z.string().optional(),
    medal: z.enum(['gold', 'silver', 'bronze', 'none']).default('none'),
    draft: z.boolean().default(false),
  }),
});

const certifications = defineCollection({
  loader: glob({ pattern, base: './src/content/certifications' }),
  schema: z.object({
    title: z.string(),
    issuer: z.string(),
    /**
     * certification = exam passed and credential issued.
     * training      = course / program followed (NOT a certification).
     */
    kind: z.enum(['certification', 'training']),
    status: z.enum(['obtained', 'completed', 'in-progress', 'planned']),
    date: z.coerce.date().optional(),
    credentialUrl: z.url().optional(),
    credentialId: z.string().optional(),
    /** Expiry date for credentials that expire */
    expires: z.coerce.date().optional(),
    skills: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }).refine((c) => (c.kind === 'certification' ? c.status !== 'completed' : c.status !== 'obtained'), {
    message:
      'A certification is "obtained" (not "completed"); a training is "completed" and can never be "obtained".',
    path: ['status'],
  }),
});

export const collections = { writeups, projects, ctf, achievements, certifications };
