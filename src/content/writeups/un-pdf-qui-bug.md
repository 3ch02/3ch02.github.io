---
# Imported from Obsidian: Cyberini/🚩 Writeup -- Un PDF qui bug.md
title: Un PDF qui bug
category: Misc
ctf: Cyberini
date: 2026-08-07
summary: 'Le fichier porte l''extension .pdf, mais les lecteurs PDF refusent de l''ouvrir. On vérifie son type réel avec la commande file :'
tags:
- cyberini
- misc
lang: fr
imported: true
---

## 📌 Aperçu du Challenge
- **Nom :** Un PDF qui bug
- **Objectif :** Résoudre l'erreur d'ouverture d'un fichier prétendant être un document PDF.
- **Flag :** `flag:{Easy_Cheesy}`

---

## Step 1 : Identification du Vrai Format (`file` & Magic Bytes)

Le fichier porte l'extension `.pdf`, mais les lecteurs PDF refusent de l'ouvrir. On vérifie son type réel avec la commande `file` :

```bash
file Mon_Document.pdf
````

**Résultat :**

`Mon_Document.pdf: PNG image data, 800 x 600, 8-bit/color RGB, non-interlaced`

Pour confirmer, on inspecte l'en-tête binaire (_magic bytes_) avec `xxd` :

```bash
xxd Mon_Document.pdf | head -n 10
```

**Extrait du dump hexadécimal :**

`00000000: 8950 4e47 0d0a 1a0a ... .PNG....IHDR`

> **Observation**
> 
> Les premiers octets `89 50 4E 47` (`.PNG`) correspondent au _Magic Byte_ officiel des images au format **PNG**. Le fichier est en réalité une image dont l'extension a été trompeusement modifiée en `.pdf`.

## Step 2 : Correction & Exploitation

1. Renommer le fichier avec la bonne extension :
      
    ```bash
    mv Mon_Document.pdf flag.png
    ```
    
2. Vérifier à nouveau la structure du fichier :

    ```bash
    file flag.png
    ```
    
3. Ouvrir l'image avec le visualiseur par défaut :
    
    ```bash
    open flag.png
    # Ou avec xdg-open / feh / display
    ```

Sortie 

![Screenshot](./images/obsidian/un-pdf-qui-bug/flag-1.png)

## Notion Clé

> **A retenir**
> 
> - **Extensions vs Magic Bytes :** Sous Linux/Unix, l'extension d'un fichier (`.pdf`, `.png`, `.exe`) est purement indicative pour l'utilisateur. Le système d'exploitation et les outils d'analyse se basent sur les **magic bytes** situés au tout début de l'en-tête du fichier (_header_).
>     
> - Toujours vérifier le type MIME réel d'un fichier suspect avec `file` ou un éditeur hexadécimal (`xxd`, `hexdump`) en cas de comportement inattendu.
