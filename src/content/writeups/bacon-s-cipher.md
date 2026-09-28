---
# Imported from Obsidian: csplusplus CTF/Writeup ---- Bacon's Cipher.md
title: Bacon's Cipher
category: Cryptography
ctf: csplusplus
date: 2026-09-24
summary: 'Le challenge nous fournit la phrase suivante :'
tags:
- bacon-cipher
- cryptography
- csplusplus
- stegano
lang: fr
imported: true
---

## Contenu du challenge

Le challenge nous fournit la phrase suivante :

```text
the qUick brown Fox JUMps OVeR The LaZy DOg wHILe ClevEr RaVens watch every single move tonight
```

---

## Analyse & Résolution

En observant attentivement le texte, on remarque une alternance irrégulière de lettres **majuscules** et **minuscules** au sein des mots. Il s'agit d'une caractéristique typique du **Chiffre de Bacon bilatère** (*Bacon's cipher*), où les deux états (majuscule/minuscule) représentent les symboles `A` et `B` de l'alphabet de Bacon.

Pour décoder ce message, nous utilisons l'outil en ligne dédié :
 [Outil de décodage Chiffre Bacon Bilatère - dCode](https://www.dcode.fr/chiffre-bacon-bilitere)

Après avoir configuré l'outil pour traiter les majuscules et minuscules comme les deux éléments du alphabet bilatère, nous obtenons le message en clair suivant :
`BACONSWORK`

![Screenshot](./images/obsidian/bacon-s-cipher/pasted-image-20260924195237.png)

---

## 🚩 Flag

```text
cspp{BACONSWORK}
```
