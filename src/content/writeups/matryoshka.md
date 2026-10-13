---
# Imported from Obsidian: csplusplus CTF/Matryoshka.md
title: Matryoshka
category: Forensics
difficulty: Medium
ctf: csplusplus
date: 2026-09-30
summary: 'Énoncé : A zip inside a zip inside a zip... like nesting dolls. Keep extracting until there''s nothing left to unzip — the innermost file holds the flag.'
tags:
- csplusplus
- forensics
points: 60
lang: fr
imported: true
---

## Informations

- **Catégorie :** Forensics
- **Difficulté :** Medium
- **Points :** 60
- **Auteur du write-up :** 3ch0
- **Flag :** `cspp{m4tryoshka_z1p_dolls}`

> **Énoncé :** A zip inside a zip inside a zip... like nesting dolls. Keep extracting until there's nothing left to unzip — the innermost file holds the flag.

---

## 1. Analyse

Comme son nom l'indique, le challenge est une série d'archives ZIP imbriquées les unes dans les autres (à la manière de poupées russes). Chaque archive en contient une autre, jusqu'au fichier final `flag.dat`.

---

## 2. Extraction manuelle, couche par couche

On déballe chaque couche successivement avec `unzip` :

```bash
unzip nested.zip     # → layer3.zip
unzip layer3.zip     # → layer2.zip
unzip layer2.zip     # → layer1.zip
unzip layer1.zip     # → layer0.zip
unzip layer0.zip     # → flag.dat
```

À la dernière couche, on obtient enfin `flag.dat`.

---

## 3. Récupération du flag

```bash
cat flag.dat
```

```text
cspp{m4tryoshka_z1p_dolls}
```

---

## Méthode alternative — extraction automatisée

Pour éviter de retaper `unzip` à chaque couche, une petite boucle déballe tout automatiquement tant qu'il reste un ZIP à extraire :

```bash
while ls *.zip >/dev/null 2>&1; do
  unzip -o *.zip && rm *.zip
done
cat flag.dat
```

> Pratique quand l'imbrication compte des dizaines (voire des centaines) de couches, où le déballage manuel deviendrait vite ingérable.

---

## Récapitulatif

1. Archives ZIP **imbriquées** en poupées russes.
2. `unzip` répété couche par couche (`nested → layer3 → ... → layer0 → flag.dat`).
3. Lecture du fichier final → flag.

---

***— 3ch0***
