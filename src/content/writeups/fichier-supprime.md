---
# Imported from Obsidian: Writeup --- Fichier supprimé.md
# Draft: unknown source
title: Fichier supprimé
category: Forensics
ctf: Unknown
date: 2026-09-22
summary: Description Tu peux regarder ce que tu veux, mais cette clé est vide... Votre cousin a trouvé une clé USB à la bibliothèque ce matin. Il n'est pas très doué avec les ordinateurs…
tags:
- deleted-files
- fat16
- forensics
- metadata
lang: fr
draft: true
imported: true
---

> **Description**
> *Tu peux regarder ce que tu veux, mais cette clé est vide...*
>
> Votre cousin a trouvé une clé USB à la bibliothèque ce matin. Il n'est pas très doué avec les ordinateurs, alors il compte sur vous pour retrouver le propriétaire de cette clé !

## Objectif

Identifier le propriétaire de la clé USB.

| Élément         | Détail                  |
| --------------- | ----------------------- |
| Fichier fourni  | `usb.image`             |
| Outils utilisés | `file`, `fls`, `icat`   |

---

## 1. Identification du type de fichier

Avant toute analyse, on détermine la nature du fichier avec `file` :

```bash
file usb.image
```

```text
usb.image: DOS/MBR boot sector, code offset 0x3c+2, OEM-ID "mkfs.fat", sectors/cluster 4, reserved sectors 4, root entries 512, sectors 63488 (volumes <=32 MB), Media descriptor 0xf8, sectors/FAT 64, sectors/track 62, heads 124, hidden sectors 2048, reserved 0x1, serial number 0xc7ecde5b, label: "USB        ", FAT (16 bit)
```

> **Analyse**
> Il s'agit d'une image disque brute contenant un système de fichiers **FAT16** (créé avec `mkfs.fat`), avec le label de volume `USB`. Ce format est directement exploitable par **The Sleuth Kit** (`fls`, `icat`).

---

## 2. Listing du contenu de l'image

On utilise `fls` pour lister les fichiers présents dans l'image **sans rien extraire** :

```bash
fls usb.image
```

```text
r/r 3:	USB         (Volume Label Entry)
r/r * 5:	anonyme.png
v/v 1013699:	$MBR
v/v 1013700:	$FAT1
v/v 1013701:	$FAT2
V/V 1013702:	$OrphanFiles
```

> **Découverte**
> Un fichier `anonyme.png` (inode **5**) apparaît. L'astérisque `*` indique qu'il a été **supprimé** : la clé semble vide, mais les données sont toujours présentes sur le disque.

---

## 3. Extraction et lecture des métadonnées

L'objectif étant d'identifier le propriétaire, on s'intéresse aux **métadonnées** du fichier. On utilise `icat` pour lire le contenu de l'inode 5 et on n'affiche que le début (l'en-tête PNG, où sont stockées les métadonnées) :

```bash
icat usb.image 5 | head -n 40
```

Extrait pertinent du résultat :

```xml
<x:xmpmeta xmlns:x='adobe:ns:meta/' x:xmptk='Image::ExifTool 11.88'>
 <rdf:Description rdf:about=''
  xmlns:dc='http://purl.org/dc/elements/1.1/'>
  <dc:creator>
   <rdf:Seq>
    <rdf:li>Javier Turcot</rdf:li>
   </rdf:Seq>
  </dc:creator>
 </rdf:Description>
</x:xmpmeta>
```

> **Résultat**
> Le bloc **XMP** (stocké dans un chunk `iTXt` du PNG) contient le champ `dc:creator` avec la valeur **Javier Turcot** : c'est le propriétaire de la clé.

> **Alternative plus propre**
> ```bash
> icat usb.image 5 > anonyme.png
> exiftool anonyme.png | grep -i creator
> ```

---

## 🚩 Flag

```text
javier_turcot
```

---

## ''''''''''''''''''''''''''📚 Ce qu'il faut retenir

- Un fichier **supprimé** sur FAT n'est pas effacé : seule l'entrée de répertoire est marquée comme supprimée, les données restent récupérables tant qu'elles ne sont pas écrasées.
- `fls` liste les fichiers (y compris supprimés, marqués `*`), `icat` extrait le contenu d'un fichier à partir de son numéro d'inode.
- Les **métadonnées** (EXIF, XMP) d'une image peuvent révéler l'auteur, le logiciel utilisé, des dates, voire une géolocalisation.
