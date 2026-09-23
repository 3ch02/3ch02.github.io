---
# Imported from Obsidian: Cyberini/🌅 Writeup -- Coucher de soleil.md
title: Coucher de soleil
category: Steganography
ctf: Cyberini
date: 2026-08-17
summary: Décidément, la section Stéganographie est estivale 😎. Après Bali, ma tante m'a envoyé cette image d'un coucher de soleil qui me semble plutôt "fabriquée" que réelle, si vous voyez…
tags:
- cyberini
- lsb
- steganography
- zsteg
lang: fr
imported: true
---

## 📝 Description du Challenge
> Décidément, la section Stéganographie est estivale 😎. Après Bali, ma tante m'a envoyé cette image d'un coucher de soleil qui me semble plutôt "fabriquée" que réelle, si vous voyez ce que je veux dire.

---

##  Phase d'Analyse

### 1. Extraction de l'Archive
On commence par décompresser le fichier ZIP fourni pour récupérer l'image du challenge.
```bash
\$ unzip coucher_soleil.zip 
Archive:  coucher_soleil.zip
  inflating: coucher_soleil.png      
```

### 2. Vérification du Fichier
On vérifie le type de fichier pour s'assurer qu'il s'agit bien d'une image PNG standard et non d'un faux format ou d'un fichier corrompu.
```bash
\$ file coucher_soleil.png 
coucher_soleil.png: PNG image data, 640 x 480, 8-bit/color RGB, non-interlaced
```

---

## 🛠️Résolution & Exploitation

### Analyse LSB avec `zsteg`
Puisque la description indique que l'image semble *"fabriquée"*, on suspecte une modification des bits de poids faible (**LSB - Least Significant Bit**), technique classique en stéganographie sur le format PNG.

On passe l'outil `zsteg` sur l'image extraite :
```bash
\$ zsteg coucher_soleil.png 
chunk:0:IHDR        .. file: Adobe Photoshop Color swatch, version 0, 640 colors...
b1,r,lsb,xy         .. text: ":/Qr!gcsI3k"
b1,g,lsb,xy         .. file: OpenPGP Public Key
b1,b,lsb,xy         .. file: OpenPGP Secret Key
b1,rgb,lsb,xy       .. text: "flag=l5b_st3g0_r3v34l3d<<<END>>>\$"
b2,r,msb,xy         .. text: ["U" repeated 96 times]
b2,rgb,lsb,xy       .. file: OpenPGP Secret Key
b2,bgr,msb,xy       .. file: OpenPGP Public Key
b4,g,msb,xy         .. text: ";3333333333333333333333333333..."
```

L'outil détecte immédiatement une chaîne textuelle dissimulée dans les canaux combinés **RGB (Bit 1, LSB, coordonnées XY)**.

---

## 🚩 Flag

Le flag extrait de la charge utile LSB est :
`flag=l5b_st3g0_r3v34l3d<<<END>>>$`

> **Note de l'analyse :** Le format exact dépend de la plateforme de CTF (ex: `FLAG{l5b_st3g0_r3v34l3d}`).
