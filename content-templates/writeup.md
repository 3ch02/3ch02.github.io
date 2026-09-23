---
# Copy to src/content/writeups/<slug>.md — the file name becomes the URL: /writeups/<slug>/
title: "Challenge name"
category: "Forensics"      # Forensics | Cryptography | Web | Reverse Engineering | Steganography | OSINT | Misc | Boot2Root
difficulty: "Medium"       # Easy | Medium | Hard | Insane
ctf: "IPNET CyberBattle 2026"
competition: ipnet-cyberbattle-2026   # optional: file name in src/content/ctf/ (links the write-up to the competition page)
date: 2026-09-22
summary: "One sentence shown on cards and in search results."
tags:
  - forensics
  - pcap
# points: 300              # optional
# featured: true           # optional: shown in the "Featured" block of /writeups
draft: true                # visible with `npm run dev` only — remove when ready to publish
---

## Challenge

Statement, files provided, flag format.

## Recon

What you looked at first, and why.

```console
$ file challenge.bin
challenge.bin: ELF 64-bit LSB executable, x86-64
```

## Solution

Steps, reasoning, dead ends worth mentioning.

<!--
Images: put them next to the write-up, e.g. src/content/writeups/images/, and use a
relative path. Astro optimises them (WebP, width/height, lazy loading) at build time.
The file must exist, otherwise the build fails:

![Wireshark — suspicious DNS traffic](./images/my-writeup-dns.png)
-->

```python
# solve.py
print("flag")
```

## Flag

```text
FLAG{...}
```

## Takeaways

- What you learned
- What you would do differently
