---
# Imported from Obsidian: CTF/ForeverCTF/Writeup CTF — Strings (100 pts).md
title: Strings
category: Reverse Engineering
ctf: ForeverCTF
date: 2026-08-07
summary: L'énoncé nous indique que le flag est stocké directement en texte clair à l'intérieur du code compilé (binaire). L'objectif est d'extraire les chaînes de caractères imprimables…
tags:
- foreverctf
- reverse-engineering
lang: fr
imported: true
---

## 📝 Description du Challenge

> **Description :** I think the flag is hardcoded in the binary. If only there was a way to look at the text data in a binary file.
> 
> **Fichier :** `reversing-strings` **Auteur :** Dan

L'énoncé nous indique que le flag est stocké directement en texte clair à l'intérieur du code compilé (binaire). L'objectif est d'extraire les chaînes de caractères imprimables pour le récupérer.

## 🔍 1. Analyse du Fichier (Reconnaissance)

Avant d'exécuter un binaire inconnu ou de le passer dans un désassembleur, la règle d'or est d'analyser ses propriétés basiques avec la commande `file`.

```bash
file reversing-strings
```

**Résultat :**

```
reversing-strings: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, ... not stripped
```

Il s'agit d'un exécutable Linux standard (**ELF**) 64 bits. La mention importante ici est **`not stripped`**, ce qui signifie que la table des symboles et les noms des fonctions originales n'ont pas été nettoyés lors de la compilation, rendant le reverse encore plus accessible.

## 💥 2. Extraction des chaînes de caractères (Exploitation)

> **Rappel Théorique :** Un fichier binaire compilé contient des instructions machines (opcodes) illisibles pour un humain, mais il embarque également des sections de données (comme `.rodata` pour _Read-Only Data_) où sont stockées les phrases, les messages d'erreur et les variables textuelles définies par le développeur.

L'utilitaire de référence sous Linux pour extraire ces sections textuelles est la commande **`strings`**. Couplée à un filtre `grep`, on isole directement la structure du flag recherché.

### Commande exécutée :

```
strings reversing-strings | grep "utflag"
```

Le terminal affiche instantanément la chaîne correspondante trouvée dans le binaire.

## 🏁 3. Capture du Flag

L'extraction directe nous révèle le flag en clair sans avoir eu besoin d'ouvrir Ghidra ou IDA Pro :

**Flag récupéré :**

```
utflag{plaintext_str1ngs_aRe_b3St_Str1ngs}
```

**_3ch0 training_**
