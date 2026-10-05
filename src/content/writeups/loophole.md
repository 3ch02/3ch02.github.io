---
# Imported from Obsidian: CTF/BRCTF/Loophole.md
title: Loophole
category: Forensics
difficulty: Easy
ctf: brCTF 2026
competition: brctf-2026
date: 2026-10-01
summary: 'Énoncé : Investigators recovered a history database from the suspect''s machine. Every click, every visit, every search leaves a trace. The suspect thought clearing the screen was…'
tags:
- brctf-2026
- forensics
points: 50
lang: fr
imported: true
---

> Compétition : **brCTF** — Challenge ID#3

## Informations

- **Catégorie :** Forensic
- **Difficulté :** Easy
- **Points :** 50
- **Auteur du write-up :** 3ch0
- **Flag :** `BRCTF{f0und_th3_l00ph0l3}`

> **Énoncé :** Investigators recovered a history database from the suspect's machine. Every click, every visit, every search leaves a trace. The suspect thought clearing the screen was enough — but the record persists in the database. Read their tracks. Where did they go, and what were they looking for?

---

## 1. Analyse du fichier

Le fichier fourni est une base de données d'historique de navigateur :

```bash
file History-Loophole
```

```text
History-Loophole: SQLite 3.x database, last written using SQLite version 3046001, ...
```

Une **base SQLite**. Un premier réflexe (`strings`) ne trouve pas le flag en clair :

```bash
strings History-Loophole | grep -i brctf
```

Rien. Bon indice : le flag n'est pas stocké tel quel — il est **encodé** (base64) et **fragmenté** à travers plusieurs tables, donc invisible à un `grep`.

---

## 2. Exploration de la structure

On liste les tables :

```bash
sqlite3 History-Loophole ".tables"
```

```text
downloads   downloads_url_chains   keyword_search_terms   meta   urls   visits
```

Tables typiques d'un historique **Chrome / Chromium**. On va inspecter celles qui racontent l'activité du suspect : `urls` (sites visités), `keyword_search_terms` (recherches) et `downloads` (fichiers téléchargés).

---

## 3. Collecte des fragments

### Fragment 1 — table `urls`, paramètre `note=` (base64)

```bash
sqlite3 History-Loophole "SELECT url, title FROM urls;"
```

Parmi les entrées anodines, une URL de recherche porte un paramètre `note=` suspect :

```text
https://www.google.com/search?q=best+cloud+storage+for+backup&note=QlJDVEZ7ZjB1bmRf
```

On décode le base64 :

```bash
echo "QlJDVEZ7ZjB1bmRf" | base64 -d
```

```text
BRCTF{f0und_
```

### Fragment 2 — table `downloads`, dossier caché

```bash
sqlite3 History-Loophole "SELECT * FROM downloads;"
```

Un téléchargement sort du lot : un PDF enregistré dans un **répertoire temporaire caché** dont le nom porte un fragment :

```text
/home/jdoe/Downloads/.tmp_th3_/invoice_march.pdf
                     └───────┘
                      .tmp_th3_   →   th3_
```

### Fragment 3 — table `urls`, URL interne

Toujours dans `urls`, une URL vers un hôte interne se termine par la fin manifeste d'un flag :

```text
https://internal-notes.example.com/staging/l00ph0l3}
                                           └────────┘
                                            l00ph0l3}
```

---

## 4. Reconstruction du flag

Les trois fragments, dispersés dans trois emplacements distincts de la base :

| Ordre | Fragment | Source | Table |
|-------|----------|--------|-------|
| 1 | `BRCTF{f0und_` | `note=QlJDVEZ7ZjB1bmRf` (base64) | `urls` |
| 2 | `th3_` | dossier `.tmp_th3_` | `downloads` |
| 3 | `l00ph0l3}` | URL `/staging/l00ph0l3}` | `urls` |

Assemblage :

```
BRCTF{f0und_  +  th3_  +  l00ph0l3}
```

**Flag :** `BRCTF{f0und_th3_l00ph0l3}`

> Soit *« found the loophole »* — le flag décrit lui-même le challenge.

---

## Récapitulatif de la chaîne d'exploitation

1. **`file`** → base **SQLite** (historique Chrome).
2. **`strings`** → rien : flag encodé et fragmenté (indice fort).
3. **`.tables`** → inspection de `urls` et `downloads`.
4. **3 fragments** : base64 dans un `note=` (`urls`), dossier `.tmp_th3_` (`downloads`), fin d'URL interne (`urls`).
5. **Décodage base64 + assemblage** → flag.

> **Concept clé :** l'historique d'un navigateur (`History`, base SQLite) conserve chaque URL visitée, chaque recherche et **chaque téléchargement** (chemin de destination inclus), même après « effacement de l'écran ». Il faut ratisser **toutes** les tables (`urls`, `visits`, `keyword_search_terms`, `downloads`) : un indice peut se cacher dans un paramètre d'URL, un chemin de fichier, ou être encodé. Un `grep` qui ne trouve rien doit faire penser à de l'encodage (base64) plutôt qu'à une absence de données.

---

***— 3ch0***
