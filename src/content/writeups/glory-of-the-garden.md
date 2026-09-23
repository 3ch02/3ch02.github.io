---
# Imported from Obsidian: CTF/picoCTF/Writeup - Glory of the Garden.md
title: Glory of the Garden
category: Forensics
ctf: picoCTF
date: 2026-08-07
summary: On s'assure du format du fichier avec la commande standard file.
tags:
- file
- forensics
- grep
- picoctf
- static-analysis
- strings
lang: fr
imported: true
---

## Métadonnées

- **Catégorie :** Forensics Static-Analysis
    
- **Outils :** file strings grep
    
- **Flag :** `picoCTF{more_than_m33ts_the_3y395e12915}`
    

## Description du challenge

> _This file contains more than it seems._

## Étape 1 : Vérification de la nature du fichier

On s'assure du format du fichier avec la commande standard `file`.

```bash
file garden.jpg
```

### Résultat :

```text
garden.jpg: JPEG image data, JFIF standard 1.01, resolution (DPI), density 72x72, segment length 16, baseline, precision 8, 2999x2249, components 3
```

## 🕵️ Étape 2 : Extraction des chaînes de caractères (Quick Win)

Avant de lancer des outils d'extraction ou de stéganographie lourds, on applique le réflexe de l'analyse statique pour extraire les chaînes de texte imprimables et filtrer le format du flag.

```bash
strings garden.jpg | grep "picoCTF"
```

### Résultat :

```text
Here is a flag: picoCTF{more_than_m33ts_the_3y395e12915}
```

Le flag était simplement injecté en texte brut à l'intérieur du fichier binaire de l'image.

## 🏁 Étape 3 : Capture du Flag

**Flag :** `picoCTF{more_than_m33ts_the_3y395e12915}`

## Mémo Forensics : Concaténation de données en fin de fichier

Pourquoi le flag apparaît-il avec `strings` alors que l'image s'ouvre normalement ?

- Les fichiers JPEG possèdent des marqueurs structurels stricts. Ils commencent par `FF D8` (Start of Image) et se terminent impérativement par **`FF D9`** (End of Image).
    
- Les visionneuses d'images lisent le fichier jusqu'au marqueur `FF D9` puis s'arrêtent, ignorant tout ce qui se trouve après.
    
- Les attaquants ou les créateurs de CTF peuvent donc utiliser une simple commande de concaténation (comme `cat flag.txt >> image.jpg`) pour "coller" des données, une archive zip ou un script à la fin de l'image sans altérer son affichage visuel.
