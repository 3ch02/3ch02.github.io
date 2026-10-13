---
# Imported from Obsidian: csplusplus CTF/Heavier Than It Looks.md
title: Heavier Than It Looks
category: Forensics
difficulty: Medium
ctf: csplusplus
date: 2026-09-30
summary: 'Un PNG tout ce qu''il y a de classique en apparence. Mais l''énoncé insiste : l''image est « plus lourde que ses pixels ne le justifient » (17 kB pour une image de 120×80). On creuse…'
tags:
- csplusplus
- forensics
points: 55
lang: fr
imported: true
---

## Informations

- **Catégorie :** Forensics
- **Difficulté :** Medium
- **Points :** 55
- **Auteur du write-up :** 3ch0
- **Flag :** `cspp{z1p_appended_after_iend}`

> **Énoncé :** This PNG is larger than its pixels justify. Something is appended after the image data.
> **Indice :** le répertoire central d'une archive ZIP se trouve à la **fin** du fichier, donc des outils comme `unzip` ouvrent sans broncher un PNG auquel un ZIP a été collé à la suite.

---

## 1. Analyse du fichier

On vérifie d'abord le type du fichier :

```bash
file polyglot.png
```

```text
polyglot.png: PNG image data, 120 x 80, 8-bit/color RGB, non-interlaced
```

Un PNG tout ce qu'il y a de classique en apparence. Mais l'énoncé insiste : l'image est « plus lourde que ses pixels ne le justifient » (17 kB pour une image de 120×80). On creuse avec `exiftool` :

```bash
exiftool polyglot.png
```

L'indice décisif apparaît dans la sortie :

```text
Warning : [minor] Trailer data after PNG IEND chunk
```

> **`IEND` est le dernier chunk d'un PNG valide** : tout ce qui vient après n'appartient pas à l'image. Il y a donc des données cachées collées à la fin du fichier.

---

## 2. Identification des données cachées (binwalk)

On analyse la structure interne du fichier avec `binwalk` :

```bash
binwalk polyglot.png
```

```text
DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             PNG image, 120 x 80, 8-bit/color RGB, non-interlaced
41            0x29            Zlib compressed data, default compression
16838         0x41C6          Zip archive data, ... name: flag.dat
16959         0x423F          End of Zip archive, footer length: 22
```

Le fichier est un **polyglotte PNG + ZIP** : une archive ZIP contenant `flag.dat` est concaténée après les données de l'image, à l'offset `0x41C6`.

---

## 3. Extraction et récupération du flag

On extrait le contenu embarqué :

```bash
binwalk -e polyglot.png
```

```bash
ls -al _polyglot.png.extracted
```

```text
-rw------- 1 echo echo    29 Jun  5 15:50 flag.dat
```

Il ne reste qu'à lire le fichier extrait :

```bash
cat _polyglot.png.extracted/flag.dat
```

```text
cspp{z1p_appended_after_iend}
```

---

## Méthode alternative

Puisque le répertoire central du ZIP est en fin de fichier, `unzip` lit le PNG directement comme une archive — sans même passer par binwalk :

```bash
unzip polyglot.png
cat flag.dat
```

---

## Récapitulatif

1. **`exiftool`** → warning « Trailer data after PNG IEND chunk » : des données existent après la fin légitime du PNG.
2. **`binwalk`** → identification d'un ZIP (`flag.dat`) concaténé à l'offset `0x41C6`.
3. **`binwalk -e`** (ou `unzip`) → extraction de l'archive et lecture du flag.

> **Concept clé :** un fichier polyglotte exploite le fait que le PNG se lit depuis le **début** (signature + chunks jusqu'à `IEND`) tandis que le ZIP se lit depuis la **fin** (End of Central Directory). Les deux formats cohabitent donc dans un même fichier sans se gêner.

---

***— 3ch0***
