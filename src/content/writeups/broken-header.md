---
# Imported from Obsidian: csplusplus CTF/Broken Header.md
title: Broken Header
category: Forensics
difficulty: Medium
ctf: csplusplus
date: 2026-09-30
summary: 'Énoncé : This file won''t open as an image — its PNG signature (the magic bytes at the very start) was corrupted. A valid PNG begins with 89 50 4E 47 0D 0A 1A 0A. Patch the header…'
tags:
- csplusplus
- forensics
points: 75
lang: fr
imported: true
---

## Informations

- **Catégorie :** Forensics
- **Difficulté :** Medium
- **Points :** 75
- **Auteur du write-up :** 3ch0
- **Flag :** `cspp{f1x_the_png_header}`

> **Énoncé :** This file won't open as an image — its PNG signature (the magic bytes at the very start) was corrupted. A valid PNG begins with `89 50 4E 47 0D 0A 1A 0A`. Patch the header in a hex editor, then inspect the repaired file's metadata for the flag.

---

## 1. Analyse

Le fichier refuse de s'ouvrir comme une image. `file` ne l'identifie pas :

```bash
file broken.png
```

```text
broken.png: data
```

On inspecte les premiers octets en hexadécimal :

```bash
xxd broken.png | head -n 20
```

```text
00000000: dead beef 0d0a 1a0a 0000 000d 4948 4452  ............IHDR
00000010: 0000 008c 0000 0046 0802 0000 0091 d1eb  .......F........
00000020: bb00 0000 1d74 4558 7466 6c61 6700 6373  .....tEXtflag.cs
00000030: 7070 7b66 3178 5f74 6865 5f70 6e67 5f68  pp{f1x_the_png_h
00000040: 6561 6465 727d 5e83 af3e 0000 4313 4944  eader}^..>..C.ID
```

Deux constats :

1. **Signature corrompue** : le fichier commence par `DE AD BE EF` au lieu des magic bytes PNG attendus `89 50 4E 47`. Les 4 octets suivants (`0D 0A 1A 0A`) sont, eux, intacts.
2. **Flag déjà visible** : un chunk `tEXt` avec le mot-clé `flag` contient la chaîne `cspp{f1x_the_png_header}` — lisible à l'œil dès le dump hexa.

---

## 2. Réparation du header (hex editor)

On corrige les 4 premiers octets pour restaurer la signature PNG. Header cassé → header valide :

```
AVANT :  DE AD BE EF 0D 0A 1A 0A
APRÈS :  89 50 4E 47 0D 0A 1A 0A
         └──────────┘
         octets à patcher
```

On édite avec `hexeditor` (ou `hexedit`, `ghex`, `xxd`...) :

```bash
hexeditor broken.png
```

On remplace `DE AD BE EF` par `89 50 4E 47`, on sauvegarde. Vérification :

```bash
file broken.png
```

```text
broken.png: PNG image data, 140 x 70, 8-bit/color RGB, non-interlaced
```

Le fichier est de nouveau reconnu comme un PNG valide et s'ouvre :

```bash
open broken.png
```

---

## 3. Lecture du flag (métadonnées)

Le flag est stocké dans le chunk `tEXt` (métadonnée textuelle du PNG). Une fois le header réparé, on le lit proprement :

```bash
exiftool broken.png
```

Le champ correspondant contient :

```text
cspp{f1x_the_png_header}
```

> **Note :** ici le flag était récupérable **sans même réparer le fichier**, puisque les chunks `tEXt` stockent leur contenu en clair — un simple `strings broken.png | grep cspp` l'aurait sorti. Mais la réparation du header reste l'objectif du challenge.

---

## Patch en ligne de commande (bonus)

Pour patcher sans éditeur interactif, on peut réécrire les 4 octets avec `dd` :

```bash
printf '\x89\x50\x4e\x47' | dd of=broken.png bs=1 seek=0 count=4 conv=notrunc
```

---

## Récapitulatif

1. **`file`** → « data » : signature non reconnue.
2. **`xxd`** → header corrompu (`DE AD BE EF` au lieu de `89 50 4E 47`) + flag visible dans un chunk `tEXt`.
3. **Hex editor** (ou `dd`) → restauration des magic bytes PNG.
4. **`exiftool`** → lecture du flag dans les métadonnées.

> **Concept clé :** les **magic bytes** en tête de fichier déterminent comment les outils interprètent son format. Corrompre cette signature « casse » le fichier sans en altérer le contenu — le réparer suffit à le rendre de nouveau exploitable.

---

***— 3ch0***
