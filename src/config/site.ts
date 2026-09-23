/**
 * Personal information and site-wide settings.
 *
 * This is the ONLY file you need to edit to change your identity, links
 * or contact details. Anything left as `null` is simply not rendered,
 * so the site never shows a broken or invented link.
 */

export const SITE = {
  name: 'KERIM Loukouman',
  handle: '3ch0',
  title: 'KERIM Loukouman — 3ch0',
  tagline: 'Cybersecurity Student | Systems & Networks | CTF',
  description:
    'Portfolio and technical journal of KERIM Loukouman (3ch0), cybersecurity student at IPNET Institute of Technology. CTF write-ups, projects and hands-on notes on systems, networks and security.',
  role: 'Cybersecurity Student',
  focus: ['Systems & Networks', 'CTF', 'Security'],
  school: 'IPNET Institute of Technology',
  locale: 'en',
  ogImage: '/og-default.png',
} as const;

export type SocialLink = {
  label: string;
  href: string;
  /** Icon key, see src/components/Icon.astro */
  icon: 'github' | 'linkedin' | 'mail' | 'x' | 'award' | 'htb' | 'thm' | 'rootme' | 'ctftime' | 'link';
  /** Short text shown on the Contact page, e.g. the username */
  display?: string;
};

/**
 * Contact & social links.
 * Set a value to `null` to hide it everywhere.
 */
const links: Record<string, SocialLink | null> = {
  github: {
    label: 'GitHub',
    href: 'https://github.com/3ch02',
    icon: 'github',
    display: '3ch02',
  },
  linkedin: {
    label: 'LinkedIn',
    href: 'https://www.linkedin.com/in/loukouman-kerim-38565338b/',
    icon: 'linkedin',
    display: 'Loukouman KERIM',
  },
  credly: {
    label: 'Credly',
    href: 'https://www.credly.com/users/loukouman-kerim',
    icon: 'award',
    display: 'Verified badges',
  },
  // Public contact address, e.g. 'mailto:you@example.com' (null = hidden)
  email: null,
  // Optional platforms — fill in if you want them displayed.
  ctftime: null,
  tryhackme: null,
  hackthebox: null,
  rootme: null,
};

export const SOCIALS: SocialLink[] = Object.values(links).filter(
  (l): l is SocialLink => l !== null,
);

/**
 * CV download. Put the PDF in /public/cv/ and set `available: true`.
 * While `available` is false the hero shows a "Request CV" link to the
 * contact page instead of a dead download link.
 */
export const CV = {
  available: false,
  href: '/cv/KERIM_Loukouman_CV.pdf',
};

export const NAV = [
  { label: 'Home', href: '/' },
  { label: 'About', href: '/about' },
  { label: 'Projects', href: '/projects' },
  { label: 'CTF', href: '/ctf' },
  { label: 'Writeups', href: '/writeups' },
  { label: 'Achievements', href: '/achievements' },
  { label: 'Certifications', href: '/certifications' },
  { label: 'Contact', href: '/contact' },
] as const;

/** Skills, grouped. Only list what you can actually talk about in an interview. */
export const SKILLS: { group: string; items: string[] }[] = [
  {
    group: 'Cybersecurity',
    items: [
      'Digital Forensics',
      'Web Security',
      'Cryptography',
      'CTF',
      'OSINT',
      'Steganography',
      'Reverse Engineering',
    ],
  },
  {
    group: 'Systems',
    items: ['Linux', 'Windows', 'Windows Server', 'Active Directory'],
  },
  {
    group: 'Networking',
    items: ['TCP/IP', 'VLAN', 'VPN', 'SD-WAN', 'Network Security'],
  },
  {
    group: 'Tools & Technologies',
    items: ['FortiGate', 'pfSense', 'Wazuh', 'Burp Suite', 'Wireshark', 'Ghidra'],
  },
];

export const INTERESTS = [
  'Cybersecurity',
  'Systems & Networks',
  'Digital Forensics',
  'CTF',
  'Security Engineering',
];

export const CREDLY_URL = 'https://www.credly.com/users/loukouman-kerim';
