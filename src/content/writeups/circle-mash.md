---
# Imported from Obsidian: CTF/BRCTF/Circle Mash.md
title: Circle Mash
category: Forensics
difficulty: Easy
ctf: brCTF 2026
competition: brctf-2026
date: 2026-10-01
summary: 'Énoncé : A backup repository was found on a shared server, containing config and backup scripts. The current files look innocent enough — but version control never forgets. Every…'
tags:
- brctf-2026
- forensics
points: 50
lang: fr
imported: true
---

> Compétition : **brCTF** — Challenge ID#1

## Informations

- **Catégorie :** Forensic
- **Difficulté :** Easy
- **Points :** 50
- **Auteur du write-up :** 3ch0
- **Flag :** `BRCTF{n07h1ng_1s_3v3r_d3l3t3d}`

> **Énoncé :** A backup repository was found on a shared server, containing config and backup scripts. The current files look innocent enough — but version control never forgets. Every commit is a snapshot in time, and someone was careless about what they committed. Walk the history. What did they try to bury?

---

## 1. Mise en place

L'archive fournie est doublement compressée (`.tar.gz`). On décompresse :

```bash
gunzip circle-mash.tar.gz
tar -xvf circle-mash.tar
cd repo
```

Le dépôt contient des fichiers d'apparence anodine — `backup.py`, `config.py`, `README.md`, `.gitignore` — **et un dossier `.git/`**. C'est ce dernier qui compte : l'indice de l'énoncé (« version control never forgets ») pointe droit sur l'historique Git.

```bash
ls -la
```

```text
backup.py  config.py  README.md  .gitignore  .git/
```

---

## 2. Exploration de l'historique visible

```bash
git log -p
```

L'historique de `main` ne compte que 4 commits, tous parfaitement propres :

| Commit | Message | Contenu |
|--------|---------|---------|
| `16e0d6f` | polish README | ajout section Usage |
| `458652d` | add backup feature | fonction retry |
| `54278e2` | add config loader | `BACKUP_DIR`, `RETRY_COUNT` |
| `e0ee967` | Initial commit | README, .gitignore |

Rien de sensible. Mais la présence d'un fichier `.git/ORIG_HEAD` trahit une **réécriture d'historique** (reset/rebase/merge) : des commits ont probablement été détachés de la branche pour les faire disparaître.

---

## 3. Récupération des commits orphelins

On cherche les objets Git **non rattachés** (unreachable) avec `git fsck` :

```bash
git fsck --full --unreachable --lost-found
```

```text
unreachable commit 8162581...
unreachable commit 04b3e61...
unreachable commit 47ac5bc...
unreachable commit 9862371...
unreachable commit f17c406...
unreachable commit bd0bd64...
...
```

Plusieurs commits orphelins apparaissent. On les inspecte tous d'un coup avec leur diff :

```bash
for c in 8162581 04b3e61 47ac5bc 9862371 f17c406 bd0bd64; do
  echo "===== commit $c ====="
  git show $c
done
```

Trois de ces commits contiennent chacun un **fragment de flag** dans des fichiers que le contractant a cru effacer :

### Fragment 1 — `bd0bd64` (« debug: dump staging token »)

```python
# .debug_token
# left in by mistake during testing
staging_token=BRCTF{n07h1ng_
```

### Fragment 2 — `47ac5bc` (« wip: check token leak before release »)

```
# leak_check.txt
TODO: rotate the staging token before this goes near prod.
fragment: 1s_3v3r_
```

### Fragment 3 — `8162581` (« index on main: polish README »)

```
# .staging_backup.txt
just in case, temp copy before I clean the workspace up
fragment: d3l3t3d}
```

---

## 4. Reconstruction du flag

On réassemble les trois fragments dans l'ordre qui forme une phrase cohérente :

| Ordre | Fragment | Source |
|-------|----------|--------|
| 1 | `BRCTF{n07h1ng_` | `.debug_token` |
| 2 | `1s_3v3r_` | `leak_check.txt` |
| 3 | `d3l3t3d}` | `.staging_backup.txt` |

**Flag :** `BRCTF{n07h1ng_1s_3v3r_d3l3t3d}`

> Soit *« nothing is ever deleted »* — le flag résume lui-même la leçon du challenge.

---

## Récapitulatif de la chaîne d'exploitation

1. **Extraction** → dépôt Git avec `.git/` présent.
2. **`git log -p`** → historique `main` propre (4 commits), mais `.git/ORIG_HEAD` signale une réécriture.
3. **`git fsck --unreachable`** → découverte de commits orphelins détachés de la branche.
4. **`git show`** sur chaque orphelin → 3 fragments de flag dans des fichiers « effacés ».
5. **Réassemblage** → flag.

> **Concept clé :** `git` est un système à base de snapshots. Supprimer un fichier ou réécrire l'historique ne détruit pas les objets correspondants : ils subsistent dans `.git/objects` jusqu'au prochain *garbage collection*, et restent récupérables via `git fsck`, `git reflog` ou `git cat-file`.
>
> **Remédiation :** ne jamais commiter de secret, même temporairement. Un secret commité puis « retiré » doit être considéré comme **compromis et révoqué** (rotation de la clé/token). Pour purger réellement l'historique : `git filter-repo` (ou BFG), suivi d'un `git gc --prune=now`.

---

***— 3ch0***
