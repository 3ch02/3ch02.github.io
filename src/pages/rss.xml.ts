import type { APIRoute } from 'astro';
import { SITE } from '@/config/site';
import { getWriteups } from '@/lib/content';
import { url } from '@/lib/utils';

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/** RSS 2.0 feed of the write-ups (hand-written, no dependency). */
export const GET: APIRoute = async ({ site }) => {
  const abs = (path: string) => new URL(url(path), site).href;
  const items = (await getWriteups()).map((w) => {
    const link = abs(`/writeups/${w.id}`);
    return [
      '    <item>',
      `      <title>${esc(w.data.title)}</title>`,
      `      <link>${link}</link>`,
      `      <guid isPermaLink="true">${link}</guid>`,
      `      <pubDate>${w.data.date.toUTCString()}</pubDate>`,
      `      <category>${esc(w.data.category)}</category>`,
      ...w.data.tags.map((t) => `      <category>${esc(t)}</category>`),
      w.data.summary ? `      <description>${esc(w.data.summary)}</description>` : '',
      '    </item>',
    ]
      .filter(Boolean)
      .join('\n');
  });

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${esc(SITE.title)} — CTF Writeups</title>
    <link>${abs('/writeups')}</link>
    <atom:link href="${abs('/rss.xml')}" rel="self" type="application/rss+xml" />
    <description>CTF write-ups by ${esc(SITE.handle)}</description>
    <language>en</language>
${items.join('\n')}
  </channel>
</rss>
`;
  return new Response(xml, { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } });
};
