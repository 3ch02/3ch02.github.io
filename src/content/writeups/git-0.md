---
# Imported from Obsidian: CTF/picoCTF/Writeup Forensics Git 0.md
title: Git 0
category: Forensics
ctf: picoCTF
date: 2026-05-20
summary: Analyse d'une image disque brute nommée disk.img afin de localiser des artefacts Git cachés ou supprimés dans l'environnement d'un utilisateur et d'en extraire le flag.
tags:
- disk-analysis
- forensics
- git-forensics
- picoctf
- python
- sleuthkit
lang: fr
imported: true
---

## Métadonnées

- **Catégorie :** Forensics Disk-Analysis Git-Forensics
    
- **Outils :** SleuthKit (`mmls`, `fls`, `icat`), Python (`zlib`)
    
- **Flag :** `picoCTF{g17_1n_7h3_d15k_041217d8}`
    

## Description du challenge

Analyse d'une image disque brute nommée `disk.img` afin de localiser des artefacts Git cachés ou supprimés dans l'environnement d'un utilisateur et d'en extraire le flag.

## Étape 1 : Identification du type de fichier

On commence l'investigation en vérifiant la nature de la cible avec la commande `file` :

```
file disk.img
```

### Résultat :

```
disk.img: DOS/MBR boot sector; partition 1 : ID=0x83, active, start-CHS (0x2,0,33), end-CHS (0x263,8,56), startsector 2048, 614400 sectors; partition 2 : ID=0x82, start-CHS (0x263,8,57), end-CHS (0x3ff,15,63), startsector 616448, 524288 sectors; partition 3 : ID=0x83, start-CHS (0x3ff,15,63), end-CHS (0x3ff,15,63), startsector 1140736, 956416 sectors
```

L'image contient une table de partitions de type Master Boot Record (MBR) découpée en plusieurs volumes Linux.

## Étape 2 : Analyse de la table de partitions (`mmls`)

Pour obtenir la disposition exacte des secteurs et identifier la partition de données principale, on utilise `mmls` :

```
mmls disk.img
```

### Résultat :

```
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors

      Slot      Start        End         Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000002047   0000002048   Unallocated
002:  000:000   0000002048   0000616447   0000614400   Linux (0x83)
003:  000:001   0000616448   0001140735   0000524288   Linux Swap / Solaris x86 (0x82)
004:  000:002   0001140736   0002097151   0000956416   Linux (0x83)
```

La partition Linux principale se situe au niveau du **Slot 004** avec un décalage de début (offset) de **`1140736`** secteurs.

## Étape 3 : Exploration du système de fichiers (`fls`)

On liste la structure racine de la partition cible à l'aide de l'outil `fls` :

```bash
fls -o 1140736 disk.img
```

### Résultat :

![Screenshot](./images/obsidian/git-0/pasted-image-20260520231800.png)

Le répertoire `/home` est repéré à l'**inode 64770**. On lance une inspection récursive de ce dossier (après correction de la position de l'argument `-r` dans la syntaxe de la commande) :

```bash
fls -r -o 1140736 disk.img 64770
```

### Résultat de l'arborescence :

```
d/d 64771:      ctf-player
+ d/d 65663:    Code
++ d/d 65664:   secrets
+++ d/d 65665:  .git
[...]
++++ d/d 65689: objects
+++++ d/d 65694:        46
++++++ r/r 65695:       064ac3ab7afd9a95bc1224aa8b4cef23741fcc
+++++ d/d 65697:        18
++++++ r/r 65698:       6ca660f488a4e4cdd92e7678fcfa3da478aee7
+++++ d/d 65699:        32
++++++ r/r 65700:       7681bb38cf467cec328eec9707b240e3e74ced
+++ r/r 65692:  note.txt
```

### Lecture directe de la note

L'extraction directe du fichier classique `note.txt` (**inode 65692**) nous donne une indication cruciale sur le format attendu :

```bash
icat -o 1140736 disk.img 65692
```

> `The picoCTF flag format is 'picoCTF{}' where there is some leetspeak phrase in between the curly braces`

## Étape 4 : Extraction et décompression de la base d'objets Git

Le dossier `.git/objects` contient des fichiers compressés au format brut `zlib`. Pour inspecter le contenu des fichiers d'objets (blobs, commits, trees), on automatise l'extraction via `icat` combinée à un interpréteur Python chargé de décompresser le flux :

```bash
for inode in 65695 65698 65700 65708 65709; do 
    echo "--- Inode $inode ---"
    icat -o 1140736 disk.img $inode > /tmp/obj.zlib 2>/dev/null && \
    python3 -c "import zlib; print(zlib.decompress(open('/tmp/obj.zlib', 'rb').read()).decode('utf-8', errors='ignore'))" 2>/dev/null
done
```

### Sortie du script :

```text
--- Inode 65695 ---
blob 104The picoCTF flag format is 'picoCTF{}' where there is some leetspeak phrase in between the curly braces

--- Inode 65698 ---
tree 36100644 note.txtFJëz$L#t

--- Inode 65700 ---
commit 232tree 186ca660f488a4e4cdd92e7678fcfa3da478aee7
author ctf-player <ctf-player@example.com> 1763542167 +0000
committer ctf-player <ctf-player@example.com> 1763542167 +0000

Wrap this phrase in the flag format: g17_1n_7h3_d15k_041217d8

--- Inode 65708 ---
--- Inode 65709 ---
```

## 🏁 Étape 5 : Reconstitution du Flag

L'**inode 65700** correspond à un objet de type `commit`. Dans son message de validation, le développeur a laissé la chaîne secrète en clair : `g17_1n_7h3_d15k_041217d8`.

En appliquant les consignes de formatage de la note de l'inode 65695, on assemble le flag final.

**Flag :** `picoCTF{g17_1n_7h3_d15k_041217d8}`
