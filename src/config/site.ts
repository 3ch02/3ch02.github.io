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
  // Tagline, description, role and interests are translated: see src/i18n/ui.ts (`site`).
  school: 'IPNET Institute of Technology',
  level: 'Licence 3',
  location: 'Lomé, Togo',
  ogImage: '/og-default.png',
} as const;

export type SocialLink = {
  label: string;
  href: string;
  /** Icon key, see src/components/Icon.astro */
  icon: 'github' | 'linkedin' | 'mail' | 'whatsapp' | 'x' | 'award' | 'htb' | 'thm' | 'rootme' | 'ctftime' | 'link';
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
    href: 'https://www.linkedin.com/in/loukouman-kerim/',
    icon: 'linkedin',
    display: 'Loukouman KERIM',
  },
  credly: {
    label: 'Credly',
    href: 'https://www.credly.com/users/loukouman-kerim',
    icon: 'award',
    display: 'Verified badges',
  },
  // No public email or phone number, on purpose: people write through the contact form (CONTACT_FORM below).
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

/**
 * Contact form endpoint (Formspree). Messages are delivered to the mailbox linked to
 * the form, so no email address is ever printed on the site. `null` hides the form.
 */
export const CONTACT_FORM: string | null = 'https://formspree.io/f/xaqpabqg';

/** `key` is the label in src/i18n/ui.ts (`nav`). */
export const NAV = [
  { key: 'home', href: '/' },
  { key: 'about', href: '/about' },
  { key: 'projects', href: '/projects' },
  { key: 'ctf', href: '/ctf' },
  { key: 'writeups', href: '/writeups' },
  { key: 'certifications', href: '/certifications' },
  { key: 'contact', href: '/contact' },
] as const;

/** Skills, grouped. Only list what you can actually talk about in an interview. Group names are translated in src/i18n/ui.ts (`skills`). */
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
    items: ['TCP/IP', 'VLAN', 'Network Security'],
  },
  {
    group: 'Tools & Technologies',
    items: ['FortiGate', 'pfSense', 'Wazuh', 'Burp Suite', 'Wireshark', 'Ghidra'],
  },
];

export const CREDLY_URL = 'https://www.credly.com/users/loukouman-kerim';
