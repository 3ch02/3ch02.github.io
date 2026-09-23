---
# Imported from Obsidian: CTF/picoCTF/Writeup - DISKO 1.md
title: DISKO 1
category: Forensics
ctf: picoCTF
date: 2026-08-07
summary: Can you find the flag in this disk image?
tags:
- disk-analysis
- file
- forensics
- grep
- picoctf
- strings
lang: fr
imported: true
---

## Métadonnées

- **Catégorie :** Forensics Disk-Analysis
    
- **Outils :** file strings grep
    
- **Flag :** `picoCTF{1t5_ju5t_4_5tr1n9_e3408eef}`
    

##  Description du challenge

> _Can you find the flag in this disk image?_

##  Étape 1 : Analyse de l'image disque

Comme pour toute investigation forensics, on commence par analyser la nature exacte du fichier fourni à l'aide de la commande `file`.

```bash
file disko-1.dd
```

### Résultat :

```
disko-1.dd: DOS/MBR boot sector, code offset 0x58+2, OEM-ID "mkfs.fat", Media descriptor 0xf8, sectors/track 32, heads 8, sectors 102400 (volumes > 32 MB), FAT (32 bit), sectors/FAT 788, serial number 0x241a4420, unlabeled
```

> 📌 **Constat :** Le fichier `.dd` est une copie conforme (dump brut) d'une partition ou d'un périphérique de stockage formaté en **FAT32** (`FAT (32 bit)`).

## 🔓 Étape 2 : Extraction directe des chaînes de caractères

Avant de déployer des outils lourds d'analyse de système de fichiers ou de carving (comme `autopsy`, `fls` ou `foremost`), on applique la méthode de l'analyse statique rapide : extraire toutes les chaînes de texte imprimables du disque et filtrer directement le motif du flag (`picoCTF`).

```bash
strings disko-1.dd | grep "picoCTF"
```

### Résultat :

```
picoCTF{1t5_ju5t_4_5tr1n9_e3408eef}
```

Le flag était stocké en clair dans l'un des secteurs du système de fichiers (probablement à l'intérieur d'un fichier texte non fragmenté ou résiduel).

## 🏁 Étape 3 : Capture du Flag

**Flag :** `picoCTF{1t5_ju5t_4_5tr1n9_e3408eef}`

## Mémo de Forensics : Analyse d'images disques

L'approche adoptée ici est parfaite pour un triage rapide (_Quick Win_). Voici la méthodologie standard à suivre si le flag avait été effacé ou masqué :

1. **`strings <image>`** : À tenter systématiquement en premier. Si le flag est stocké dans un fichier standard, il apparaîtra ici.
    
2. **`binwalk -e <image>`** : Permet de scanner l'image pour extraire automatiquement les fichiers connus (images, archives, documents) compressés ou cachés dans les secteurs.
    
3. **`sleuthkit` (`fls` / `icat`)** : Permet de lister l'arborescence des fichiers du disque directement depuis le terminal Kali, même pour les fichiers récemment supprimés (qui apparaissent avec une astérisque `*`).
    
4. **Montage manuel** : Si nécessaire, on peut monter l'image dans le système Linux pour l'explorer comme une clé USB classique :
    
    ```bash
    sudo mkdir /mnt/disk
    sudo mount -o loop disko-1.dd /mnt/disk
    ```
