---
# Imported from Obsidian: CTF/BRCTF/Ratrace.md
title: Ratrace
category: Forensics
difficulty: Easy
ctf: brCTF 2026
competition: brctf-2026
date: 2026-10-01
summary: 'Énoncé : The compromised workstation''s drive was imaged before the machine was wiped. Somewhere on this disk is the story of how the attacker moved in and what they left behind…'
tags:
- brctf-2026
- forensics
points: 50
lang: fr
imported: true
---

> Compétition : **brCTF** — Challenge ID#4

## Informations

- **Catégorie :** Forensic
- **Difficulté :** Easy
- **Points :** 50
- **Auteur du write-up :** 3ch0
- **Flag :** `BRCTF{y0u_w0n_th3_r4t_r4c3}`

> **Énoncé :** The compromised workstation's drive was imaged before the machine was wiped. Somewhere on this disk is the story of how the attacker moved in and what they left behind. Files get deleted, but disks have long memories. Mount it. Dig. What were they hiding?

---

## 1. Analyse de l'image disque

Le fichier fourni est une image de disque brute :

```bash
file retrace-disk.img
```

```text
retrace-disk.img: Linux rev 1.0 ext4 filesystem data, UUID=..., volume name "RATRACE" ...
```

Un système de fichiers **ext4** (pas de table de partitions — `mmls` ne renvoie rien, l'image est le volume lui-même). On travaille directement avec **The Sleuth Kit** (`fls`, `icat`) sans montage.

---

## 2. Reconnaissance de l'arborescence

```bash
fls -r retrace-disk.img
```

```text
d/d 16: home
+ d/d 17: analyst
++ r/r 18:  .bash_history
++ d/d 19:  .config
+++ d/d 20:   .rat_cache
++++ r/r 21:    .stage1_token
++ r/r 23:  incident_notes.txt
d/d 26: opt
+ d/d 27:  rat
++ r/r 28:  readme.txt
d/d 29: var
+ d/d 30:  log
++ r/r 31:  auth.log
++ r/r 32:  cron_backup.log
+ d/d 33:  tmp
++ r/r * 34:  .exfil_notes.txt      ← supprimé (*)
```

Les notes de l'enquêteur (`incident_notes.txt`, inode 23) donnent deux pistes : des **fichiers supprimés** dont les blocs traînent encore, et une **entrée cron suspecte** non décodée. Le flag est fragmenté en trois, chacun exfiltré par une méthode différente.

---

## 3. Collecte des fragments

### Fragment 1 — fichier caché `.stage1_token` (inode 21)

Un token de configuration du loader (beacon C2) :

```bash
icat retrace-disk.img 21
```

```json
{
  "beacon_id": "a83f19cd7e2b",
  "c2_host": "185.220.101.7",
  "c2_port": 4444,
  "auth_token": "BRCTF{y0u_"
}
```

→ `BRCTF{y0u_`

### Fragment 2 — fichier supprimé `.exfil_notes.txt` (inode 34)

On liste **uniquement les entrées supprimées** sur tout le disque :

```bash
fls -rd retrace-disk.img
```

```text
r/r * 34: var/tmp/.exfil_notes.txt
```

L'inode est toujours récupérable car ses blocs n'ont pas été réécrits — on lit directement son contenu :

```bash
icat retrace-disk.img 34
```

```text
cleanup log - run before wipe
staged creds.zip -> uploaded ok
removing stage1 loader from /tmp
removing this file next
fragment: w0n_th3_
```

→ `w0n_th3_`

### Fragment 3 — cron suspect `cron_backup.log` (inode 32)

```bash
icat retrace-disk.img 32
```

```text
CRON[988]: (root) CMD (/usr/bin/backup.sh)
CRON[989]: (www-data) CMD (/usr/bin/php /var/www/cron/session_gc.php)
CRON[990]: (root) CMD (/usr/sbin/logrotate /etc/logrotate.conf)
CRON[991]: (root) CMD (echo cjR0X3I0YzN9 | base64 -d >> /var/log/.sync)
CRON[992]: (root) CMD (/usr/sbin/anacron -s)
```

La ligne 991 est la fausse note : une commande qui écrit du base64 décodé dans un fichier caché `.sync`. On décode :

```bash
echo 'cjR0X3I0YzN9' | base64 -d
```

```text
r4t_r4c3}
```

→ `r4t_r4c3}`

---

## 4. Reconstruction du flag

| Ordre | Fragment | Source | Technique |
|-------|----------|--------|-----------|
| 1 | `BRCTF{y0u_` | `.stage1_token` | fichier caché |
| 2 | `w0n_th3_` | `.exfil_notes.txt` | **récupération de fichier supprimé** |
| 3 | `r4t_r4c3}` | `cron_backup.log` | **décodage base64** |

Assemblage :

```
BRCTF{y0u_  +  w0n_th3_  +  r4t_r4c3}
```

**Flag :** `BRCTF{y0u_w0n_th3_r4t_r4c3}`

> Soit *« you won the rat race »* — clin d'œil au nom du challenge (Ratrace / RAT).

---

## Récapitulatif de la chaîne d'exploitation

1. **`file`** → image **ext4** sans partition → analyse directe avec The Sleuth Kit.
2. **`fls -r`** → arborescence ; `incident_notes.txt` oriente vers fichiers supprimés + cron suspect.
3. **`icat 21`** → fragment 1 dans un fichier caché (config C2).
4. **`fls -rd` + `icat 34`** → fragment 2 dans un fichier **supprimé** mais récupérable.
5. **`icat 32` + base64 -d** → fragment 3 caché dans une entrée cron encodée.
6. **Assemblage** → flag.

> **Concept clé :** sur une image disque, « supprimé » ne veut pas dire « effacé ». Tant que les blocs ne sont pas réécrits, `fls -rd` liste les inodes supprimés et `icat` en relit le contenu. The Sleuth Kit permet cette analyse **sans monter** l'image (donc sans risque de modification). Un attaquant qui « nettoie » laisse des traces : fichiers cachés, inodes orphelins, et commandes planquées dans des logs/cron — souvent encodées (base64) pour échapper à un simple `grep`.

---

***— 3ch0***
