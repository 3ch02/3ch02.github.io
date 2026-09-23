---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/shift registers.md
# Draft: very short note
title: Shift registers
category: Cryptography
ctf: picoCTF 2026
date: 2026-08-07
tags:
- cryptography
- lfsr
- picoctf-2026
lang: fr
draft: true
imported: true
---

```text
from Crypto.Util.number import bytes_to_long, long_to_bytes

from Crypto.Random import get_random_bytes

key = bytes_to_long(get_random_bytes(126))

  

def steplfsr(lfsr):

    b7 = (lfsr >> 7) & 1

    b5 = (lfsr >> 5) & 1

    b4 = (lfsr >> 4) & 1

    b3 = (lfsr >> 3) & 1

  

    feedback = b7 ^ b5 ^ b4 ^ b3

    lfsr = (feedback << 7) | (lfsr >> 1)

    return lfsr

  

def encrypt_lfsr(pt_bytes):

    output = bytearray()

    lfsr = key & 0xFF

    for p in pt_bytes:

        lfsr = steplfsr(lfsr)

        ks = lfsr

        output.append(p ^ ks)

    return bytes_to_long(bytes(output))

  

pt = b"[redacted]"

ct = encrypt_lfsr(pt)

  

print(long_to_bytes(ct).hex())
```

Output ; 

```
21c1b705764e4bfdafd01e0bfdbc38d5eadf92991cdd347064e37444e517d661cea9

```

Flag : 
```
picoCTF{l1n3ar_f33dback_sh1ft_r3g}
```
