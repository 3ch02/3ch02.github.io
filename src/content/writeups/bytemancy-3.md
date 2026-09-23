---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/bytemancy 3.md
title: Bytemancy 3
category: Pwn
ctf: picoCTF 2026
date: 2026-08-07
summary: Le script charge un binaire nommé spellbook et te demande les adresses de fonctions spécifiques (embersigil, glyphconflux, etc.). Contrairement au quiz précédent où tu tapais du…
tags:
- picoctf-2026
- pwn
lang: fr
imported: true
---

Source:
```
import os

import random

import select

import sys

from typing import Optional

from pwn import ELF, p32

  

BANNER = "⊹──────[ BYTEMANCY-3 ]──────⊹"

BINARY_PATH = os.path.join(os.path.dirname(__file__), "spellbook")

QUESTION_COUNT = 3

  

SPELLBOOK_FUNCTIONS = [

    "ember_sigil",

    "glyph_conflux",

    "astral_spark",

    "binding_word",

]

  
  

def read_exact_bytes(expected_len: int) -> Optional[bytes]:

    """Read a fixed number of bytes from stdin, trimming a trailing newline."""

    stdin_buffer = sys.stdin.buffer

    buf = stdin_buffer.read(expected_len)

    if not buf or len(buf) < expected_len:

        return None

  

    # Discard trailing newlines only if more bytes are immediately available

    try:

        stdin_fileno = sys.stdin.fileno()

    except (AttributeError, ValueError, OSError):

        stdin_fileno = None

  

    if stdin_fileno is not None:

        while True:

            readable, _, _ = select.select([stdin_fileno], [], [], 0)

            if not readable:

                break

  

            peek = stdin_buffer.peek(1)[:1]

            if peek in (b"\n", b"\r"):

                stdin_buffer.read(1)

                continue

            break

  

    return buf

  
  

def main():

    try:

        elf = ELF(BINARY_PATH, checksec=False)

    except FileNotFoundError:

        print("The spellbook is missing!")

        return

  

    flag = open("./flag.txt", "r").read().strip()

  

    while True:

        try:

            print(BANNER)

            print("☍⟐☉⟊☽☈⟁⧋⟡☍⟐☉⟊☽☈⟁⧋⟡☍⟐☉⟊☽☈⟁⧋⟡☍⟐")

            print()

            print("I will name four procedures hidden inside spellbook.")

            print(

                f"Each round, send me their *raw* 4-byte addresses "

                f"in little-endian form. {QUESTION_COUNT} correct answers unlock the flag."

            )

            print()

            print("☍⟐☉⟊☽☈⟁⧋⟡☍⟐☉⟊☽☈⟁⧋⟡☍⟐☉⟊☽☈⟁⧋⟡☍⟐")

            print('⊹─────────────⟡─────────────⊹')

  

            selections = random.sample(SPELLBOOK_FUNCTIONS, QUESTION_COUNT)

            success = True

  

            for idx, symbol in enumerate(selections, 1):

                target_addr = elf.symbols[symbol]

                expected_bytes = p32(target_addr)

  

                print(

                    f"[{idx}/{QUESTION_COUNT}] Send the 4-byte little-endian "

                    f"address for procedure '{symbol}'."

                )

                print("==> ", end='', flush=True)

                user_bytes = read_exact_bytes(len(expected_bytes))

  

                if user_bytes is None:

                    print("\nI needed four bytes, traveler.")

                    success = False

                    break

  

                if user_bytes != expected_bytes:

                    print("\nThose aren't the right runes.")

                    success = False

                    break

  

            if success:

                print(flag)

                break

  

            print()

            print("The aether rejects your incantation. Try again.\n")

        except EOFError:

            break

        except Exception as exc:

            print(exc)

            break

  
  

if __name__ == "__main__":

    main()
```

### Analyse du Challenge : Bytemancy-3

Le script charge un binaire nommé `spellbook` et te demande les adresses de fonctions spécifiques (`ember_sigil`, `glyph_conflux`, etc.). Contrairement au quiz précédent où tu tapais du texte (ex: `0x401176`), ici tu dois envoyer des **octets bruts** (raw bytes).

#### 1. Le format attendu : Little-Endian

Le script précise : _"raw 4-byte addresses in little-endian form"_. Cela signifie que si une adresse est `0x080491a2`, tu ne dois pas envoyer la chaîne de caractères "0x08...", mais les octets : `\xa2\x91\x04\x08`.

#### 2. Extraction des adresses

Puisque le script utilise `p32` (donc un binaire 32-bit), tu dois lister les symboles du fichier `spellbook` :

```bash
# Pour voir toutes les adresses des fonctions magiques
nm spellbook | grep -E 'ember_sigil|glyph_conflux|astral_spark|binding_word
```

Sortie:

```
080491c1 T astral_spark
080491e3 T binding_word
08049176 T ember_sigil
0804919a T glyph_conflux

```

On peut egalement utiliser un Objetdump 

Commande 

```
objetdump -d spellbook | grep -E 'ember_sigil|glyph_conflux|astral_spark|binding_word
```

### Script avec pwntools pour interagir 

```
from pwn import *

# Connexion au serveur
io = remote('green-hill.picoctf.net', 55474)

# Dictionnaire des adresses (basé sur ton nm spellbook)
spells = {
    "astral_spark":  0x080491c1,
    "binding_word":  0x080491e3,
    "ember_sigil":   0x08049176,
    "glyph_conflux": 0x0804919a
}

for i in range(3):
    # Lecture du sort demandé
    io.recvuntil(b"procedure '")
    spell_name = io.recvuntil(b"'").decode().strip("'")
    print(f"[*] Round {i+1}: Envoi de l'adresse pour {spell_name}")
    
    # Envoi de l'adresse en format raw (Little-Endian)
    io.send(p32(spells[spell_name]))

# On passe en mode interactif pour lire le flag
io.interactive()
```

### Flag :
```
picoCTF{0bjdump_m4g1c_9ee35d3a}

```
