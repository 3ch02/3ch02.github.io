---
# Imported from Obsidian: csplusplus CTF/File Carving.md
title: File Carving
category: Forensics
difficulty: Hard
ctf: csplusplus
date: 2026-09-30
summary: 'Énoncé : This binary blob has a complete JPEG buried inside it, padded with junk on both sides. Carve it out — a JPEG starts with the bytes FF D8 FF and ends with FF D9. Save…'
tags:
- csplusplus
- forensics
points: 95
lang: fr
imported: true
---

## Informations

- **Catégorie :** Forensics
- **Difficulté :** Hard
- **Points :** 95
- **Auteur du write-up :** 3ch0
- **Flag :** `cspp{carv3d_jpeg_from_blob}`

> **Énoncé :** This binary blob has a complete JPEG buried inside it, padded with junk on both sides. Carve it out — a JPEG starts with the bytes `FF D8 FF` and ends with `FF D9`. Save those bytes as a `.jpg`, open it, and read its metadata.

---

## 1. Analyse du fichier

On identifie le fichier fourni :

```bash
file blob.bin
```

```text
blob.bin: OpenPGP Public Key
```

`file` se fie aux magic bytes du **début** du fichier et l'identifie (à tort) comme une clé publique OpenPGP — c'est le « junk » de rembourrage qui précède le vrai contenu. L'énoncé nous prévient : un **JPEG complet** est enfoui au milieu du blob, entouré de données parasites des deux côtés.

---

## 2. Solution rapide (strings)

Le flag se trouvant dans les métadonnées du JPEG (donc en texte lisible), un simple `strings` filtré sur le préfixe du flag suffit à le sortir directement :

```bash
strings blob.bin | grep cspp
```

```text
cspp{carv3d_jpeg_from_blob}
```

> Raccourci efficace, mais qui court-circuite l'objectif pédagogique du challenge. Voici la méthode de carving réellement visée.

---

## 3. Méthode intended — File carving

L'idée : localiser la **signature de début** (`FF D8 FF`) et le **marqueur de fin** (`FF D9`) du JPEG, puis extraire précisément les octets entre ces deux bornes.

### Option A — Script Python

```python
data = open("blob.bin", "rb").read()

start = data.find(b"\xff\xd8\xff")          # SOI (Start Of Image)
end   = data.find(b"\xff\xd9", start) + 2   # EOI (End Of Image), +2 pour inclure le marqueur

jpeg = data[start:end]
open("carved.jpg", "wb").write(jpeg)
print(f"JPEG extrait : offset {start} → {end} ({len(jpeg)} octets)")
```

### Option B — Localiser les offsets puis découper avec dd

```bash
# Repérer l'offset du début (FF D8 FF)
xxd blob.bin | grep -m1 'ffd8 ff'

# Repérer l'offset de la fin (FF D9)
xxd blob.bin | grep 'ffd9'

# Extraire (remplacer <start> et <count> par les valeurs trouvées)
dd if=blob.bin of=carved.jpg bs=1 skip=<start> count=<count>
```

### Option C — Outils automatiques

```bash
foremost -t jpg -i blob.bin -o carved_out/
# ou
binwalk -e blob.bin
```

---

## 4. Lecture des métadonnées

Une fois le JPEG reconstitué, on lit ses métadonnées où se cache le flag :

```bash
exiftool carved.jpg
```

Le flag apparaît dans un champ de métadonnées (Comment / EXIF) :

```text
cspp{carv3d_jpeg_from_blob}
```

---

## Récapitulatif

1. **`file`** → identification trompeuse (OpenPGP) causée par le rembourrage de tête.
2. **Carving** → recherche des marqueurs JPEG `FF D8 FF` (SOI) et `FF D9` (EOI), extraction des octets entre les deux.
3. **`exiftool`** sur le JPEG reconstitué → le flag est dans les métadonnées.

> **Concept clé :** le file carving consiste à récupérer un fichier à partir de ses **signatures** (magic bytes de début/fin) plutôt que de sa table d'allocation ou de son extension — technique centrale en forensics et en récupération de données.

---

***— 3ch0***
