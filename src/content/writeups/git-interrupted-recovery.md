---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/Writeup -Forensic - Git Interrupted Recovery.md
title: Git Interrupted Recovery
category: Forensics
ctf: picoCTF 2026
date: 2026-08-07
summary: La première étape consiste à comprendre la structure de l'image disque (disk.img) pour savoir où chercher les données.
tags:
- forensics
- picoctf-2026
lang: fr
imported: true
---

## 1. Analyse de l'image et identification des partitions

La première étape consiste à comprendre la structure de l'image disque (`disk.img`) pour savoir où chercher les données.

- **Identification du type de fichier :**
    
    ```bash
    file disk.img
    ```
    
- **Analyse de la table des partitions :**
    
    ```bash
    mmls disk.img
    ```
    
    _Observation :_ Nous avons identifié que la partition de données la plus importante commence au secteur **1140736**.
    

---

## 2. Exploration des fichiers (Inodes)

L'énoncé mentionnait une suppression interrompue d'un dépôt Git. Nous avons utilisé **The Sleuth Kit** pour scanner la partition à la recherche de traces du dossier `.git`.

- **Recherche du dossier Git :**
    
    ```bash
    fls -o 1140736 -r disk.img | grep -i ".git"
    ```
    
    _Résultat :_ Le dossier `.git` a été localisé à l'**inode 65665**.
    

---

## 3. Analyse de l'historique (Git Logs)

Dans un dépôt Git, le fichier `logs/refs/heads/master` contient l'historique de tous les changements de la branche principale, même ceux qui ont été supprimés.

- **Lecture du log master (Inode 65710) :**
    
    ```bash
    icat -o 1140736 disk.img 65710
    ```
    
    _Découverte :_ Nous avons vu une séquence de commits. Le flag semblait être présent dans le commit `e80b38b...` ("Add secret hideout chat log") avant d'être retiré dans le commit suivant.
    

---

## 4. Reconstruction de la chaîne d'objets Git

Les objets Git sont compressés avec **zlib**. Pour lire leur contenu, il faut les extraire par leur inode et les décompresser via Python.

### Étape A : Lecture du Commit

On extrait l'objet correspondant au hash `e80b38b...` (Inode **65735**).

```bash
icat -o 1140736 disk.img 65735 | python3 -c "import zlib, sys; print(zlib.decompress(sys.stdin.buffer.read()).decode(errors='ignore'))"
```

_Résultat :_ Ce commit pointe vers un objet "Tree" (arborescence) : `ead27e2bd5a0fc22868ffb629a768f82dfcda11c`.

### Étape B : Lecture du Tree (Dossier logs)

Le tree `ead27e2...` correspond à l'inode **65734**.

```bash
icat -o 1140736 disk.img 65734 | python3 -c "import zlib, sys; print(zlib.decompress(sys.stdin.buffer.read()))"
```

_Résultat :_ On y découvre un sous-dossier nommé `logs` avec le hash `22f7d0c...` (Inode **65732**).

### Étape C : Lecture du Tree final

On inspecte l'inode **65732** pour voir les fichiers à l'intérieur du dossier `logs`.

```bash
icat -o 1140736 disk.img 65732 | python3 -c "import zlib, sys; print(zlib.decompress(sys.stdin.buffer.read()))"
```

_Résultat :_ Le fichier `3.txt` apparaît avec le hash `7164443...` (Inode **65730**).

---

## 5. Extraction du Flag (Le Blob)

La dernière étape consiste à extraire et décompresser le contenu du fichier `3.txt`.

- **Extraction finale (Inode 65730) :**
    
    ```bash
    icat -o 1140736 disk.img 65730 | python3 -c "import zlib, sys; print(zlib.decompress(sys.stdin.buffer.read()).decode(errors='ignore'))"
    ```
    

**Contenu récupéré :**

> Rex: Meet at the old arcade basement for the secret hideout. Jay: Ask Rusty at the door and use password **picoCTF{g17_r35cu3_16ac6bf3}**.

---

## Conclusion

Le flag a été récupéré en exploitant la persistance des objets Git dans le système de fichiers après une suppression logique.

**Flag :** `picoCTF{g17_r35cu3_16ac6bf3}`
