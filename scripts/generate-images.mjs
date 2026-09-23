// Regenerates PNG icons and the default Open Graph image from SVG.
// Usage: node scripts/generate-images.mjs
import sharp from 'sharp';
import { readFile } from 'node:fs/promises';

const favicon = await readFile(new URL('../public/favicon.svg', import.meta.url));
await sharp(favicon, { density: 300 }).resize(32, 32).png().toFile('public/favicon-32.png');
await sharp(favicon, { density: 300 }).resize(180, 180).png().toFile('public/apple-touch-icon.png');

const og = `
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <pattern id="grid" width="44" height="44" patternUnits="userSpaceOnUse">
      <path d="M44 0H0V44" fill="none" stroke="#1f2732" stroke-width="1"/>
    </pattern>
    <radialGradient id="fade" cx="0.3" cy="0.2" r="0.9">
      <stop offset="0" stop-color="#0a0c10" stop-opacity="0"/>
      <stop offset="1" stop-color="#0a0c10" stop-opacity="1"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="630" fill="#0a0c10"/>
  <rect width="1200" height="630" fill="url(#grid)" opacity="0.6"/>
  <rect width="1200" height="630" fill="url(#fade)"/>
  <g font-family="DejaVu Sans Mono, monospace">
    <text x="90" y="250" font-size="132" font-weight="700" fill="#e3e7ec">3ch<tspan fill="#5fd4c4">0</tspan></text>
    <g fill="none" stroke="#5fd4c4" stroke-width="7" stroke-linecap="round" transform="translate(425 150)">
      <path d="M10 40a28 28 0 0 1 0 44"/>
      <path d="M34 22a54 54 0 0 1 0 80" opacity=".55"/>
      <path d="M58 6a80 80 0 0 1 0 112" opacity=".25"/>
    </g>
    <text x="94" y="330" font-size="44" fill="#939daa">KERIM Loukouman</text>
    <text x="94" y="440" font-size="34" fill="#e3e7ec">Cybersecurity Student</text>
    <text x="94" y="492" font-size="28" fill="#5fd4c4">Systems &amp; Networks • CTF • Security</text>
  </g>
  <rect x="0" y="622" width="1200" height="8" fill="#5fd4c4" opacity="0.8"/>
</svg>`;
await sharp(Buffer.from(og)).png({ compressionLevel: 9 }).toFile('public/og-default.png');
console.log('images generated');
