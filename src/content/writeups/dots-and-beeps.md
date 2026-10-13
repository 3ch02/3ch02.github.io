---
# Imported from Obsidian: csplusplus CTF/Dots and Beeps.md
title: Dots and Beeps
category: Steganography
difficulty: Hard
ctf: csplusplus
date: 2026-09-30
summary: 'Énoncé : Those beeps are Morse code. Decode the tones (short = dot, long = dash) into letters and digits. The flag is what you hear, lowercased and wrapped: cspp{whatyouhear}.'
tags:
- csplusplus
- steganography
points: 100
lang: fr
imported: true
---

## Informations

- **Catégorie :** Steganography
- **Difficulté :** Hard
- **Points :** 100
- **Auteur du write-up :** 3ch0
- **Flag :** `cspp{morsecode2026}`

> **Énoncé :** Those beeps are Morse code. Decode the tones (short = dot, long = dash) into letters and digits. The flag is what you hear, lowercased and wrapped: `cspp{whatyouhear}`.

---

## 1. Analyse

En écoutant le fichier `beeps.wav`, on entend une succession de **bips courts et longs** : c'est du **code Morse** (court = point `.`, long = trait `-`).

```bash
file beeps.wav
```

Le défi consiste simplement à décoder les tonalités en lettres et chiffres.

---

## 2. Décodage du Morse

Plutôt que de transcrire les bips à l'oreille, on utilise un décodeur audio Morse en ligne qui analyse directement le fichier :

- **Outil :** [morsecode.world — Audio Decoder (adaptive)](https://morsecode.world/international/decoder/audio-decoder-adaptive.html)

On charge `beeps.wav`, le décodeur ajuste automatiquement le timing (adaptive) et restitue le message :

```text
MORSECODE2026
```

---

## 3. Construction du flag

Le message décodé est `MORSECODE2026`. **Attention à la consigne de l'énoncé** : le flag est *lowercased* (mis en minuscules) avant d'être encadré. On applique donc la mise en minuscules :

```text
MORSECODE2026  →  morsecode2026
```

Flag final :

```text
cspp{morsecode2026}
```

> ⚠️ **Piège de casse :** le Morse ne code pas la casse, donc tout décodeur renvoie des **majuscules**. Soumettre `cspp{MORSECODE2026}` échouerait — l'énoncé impose explicitement les minuscules.

---

## Méthode alternative (hors-ligne)

Pour rester en local sans outil web, on peut :

1. Ouvrir le WAV dans **Audacity** et lire visuellement les impulsions (courtes = `.`, longues = `-`) sur la forme d'onde.
2. Ou extraire l'enveloppe du signal avec un script Python (`scipy`/`numpy`), seuiller l'amplitude pour retrouver la suite de points/traits, puis mapper sur la table Morse.

---

## Récapitulatif

1. `beeps.wav` contient des bips = **code Morse**.
2. Décodage audio (morsecode.world / Audacity) → `MORSECODE2026`.
3. **Mise en minuscules** (consigne de l'énoncé) → `morsecode2026`.
4. Flag : `cspp{morsecode2026}`.

> **Concept clé :** la stéganographie audio peut cacher de l'information dans le signal lui-même (ici la temporalité des tonalités). Toujours lire la consigne de formatage du flag à la lettre — la casse compte.

---

***— 3ch0***
