---
# Imported from Obsidian: CTF/picoCTF/Writeup - Piece by Piece.md
title: Piece by Piece
category: Forensics
difficulty: Easy
ctf: picoCTF
date: 2026-08-07
summary: L'énoncé indique que le flag est stocké dans une archive ZIP découpée en plusieurs morceaux dans le répertoire personnel (home) de la machine distante, et qu'il faut les…
tags:
- forensics
- picoctf
lang: fr
imported: true
---

- **Catégorie :** General Skills / Forensic
    
- **Difficulté :** Easy
    
- **Plateforme :** PicoCTF
    

##  Analyse du Problème

L'énoncé indique que le flag est stocké dans une archive ZIP découpée en plusieurs morceaux dans le répertoire personnel (`home`) de la machine distante, et qu'il faut les réassembler avant extraction.

##  Résolution & Commandes clés

### 1. Connexion SSH (Spécification du port)

La commande `ssh` requiert l'option `-p` pour spécifier un port non standard :

```
ssh ctf-player@dolphin-cove.picoctf.net -p 59851
```

### 2. Inspection et Assemblage des morceaux

Le répertoire contient les fichiers `part_aa`, `part_ab`, `part_ac`, `part_ad`, `part_ae`. La commande `cat` avec un joker (`*`) permet de concaténer les fichiers dans le bon ordre alphabétique vers un fichier unique `flag.zip` :

```
cat part_* > flag.zip
```

Le fichier `instructions.txt` nous fournit le mot de passe requis : **`supersecret`**.

### 3. Extraction de l'archive

```
unzip flag.zip
# Saisir le mot de passe : supersecret
cat flag.txt
```

> ****Flag capturé** `picoCTF{z1p_and_spl1t_f1l3s_4r3_fun_5b6e506b}`**
## 💡

- **`cat part_* > fichier`** : Parfait pour reconstruire des fichiers découpés par la commande Linux `split`. L'ordre alphabétique automatique des extensions (`aa`, `ab`, `ac`...) garantit l'intégrité du fichier final.
    
- **`file <nom_fichier>`** : Toujours vérifier la signature (Magic Bytes) d'un fichier combiné pour confirmer son format réel (ici, _Zip archive data_).
