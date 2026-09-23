---
# Imported from Obsidian: CTF/picoCTF/Writeup - So Many Layers.md
title: So Many Layers
category: Cryptography
difficulty: Easy
ctf: boroCTF 2026
competition: boroctf-2026
date: 2026-08-07
summary: So Many Layers Makes me cry. 00110101 00111001 ... 01000100 L'énoncé présente une longue suite de blocs de 8 bits (binaire). Le titre et la description évoquent des couches…
tags:
- boroctf-2026
- cryptography
lang: fr
imported: true
---

- **Catégorie :** Cryptography / Web / General Skills
    
- **Difficulté :** Easy
    
- **Plateforme :** boroCTF
    

## Description du Challenge

> **So Many Layers** _Makes me cry._ `00110101 00111001 ... 01000100`

L'énoncé présente une longue suite de blocs de 8 bits (binaire). Le titre et la description évoquent des couches successives à analyser (comme un oignon) pour extraire l'information.

## Analyse & Résolution (Peler l'Oignon)

Le challenge repose sur un enchaînement de plusieurs encodages classiques (multi-layer decoding).

### Couche 1 : Du Binaire à l'ASCII

En convertissant chaque octet binaire en caractère ASCII (ex: `00110101` = `5`, `00111001` = `9`), on obtient une chaîne de caractères qui ressemble à de l'**Hexadécimal**.

### Couche 2 : De l'Hexadécimal au Texte / Base64

En traduisant la chaîne hexadécimale obtenue, on tombe sur une nouvelle couche d'encodage (probablement du **Base64** reconnaissable à ses caractères alphanumériques et son éventuel padding `=`).

### Couche 3 : Le Flag Final

Après avoir décodé la dernière couche, le texte clair révèle le flag au format attendu.

## 🏁 Flag

> ****Flag capturé** `boroCTF{L!k3_aN_0n1on^}`**

## 💡 Leçons à retenir pour Obsidian

- **Indices thématiques :** Les termes "Layers" (couches) et "Onion" (oignon) dans les CTF pointent presque toujours vers des encodages imbriqués (ex: Binaire ➡️ Hexa ➡️ Base64 ➡️ Base32 ➡️ Flag) ou vers le protocole de routage Tor.
    
- **Automatisation :** Ce genre de défi se résout en 2 secondes sur **CyberChef** en empilant les blocs _From Binary_, _From Hex_, et _From Base64_ dans la recette (Recipe).
