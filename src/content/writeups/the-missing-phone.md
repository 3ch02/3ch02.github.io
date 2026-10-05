---
# Imported from Obsidian: CTF/BRCTF/The-Missing-Phone.md
title: The Missing Phone
category: Mobile
difficulty: Hard
ctf: brCTF 2026
competition: brctf-2026
date: 2026-10-02
summary: 'Énoncé : Chale, one phone has been causing serious yawa in the neighbourhood. The owner swears everything is normal, but somehow there''s something about that phone that doesn''t…'
tags:
- brctf-2026
- mobile
points: 150
lang: fr
imported: true
---

> Compétition : **brCTF** — Challenge ID#12

## Informations

- **Catégorie :** Mobile
- **Difficulté :** Hard
- **Points :** 150
- **Auteur du write-up :** 3ch0
- **Flag :** `brctf{hidd3n_in_th3_p4ck4ge}`

> **Énoncé :** Chale, one phone has been causing serious yawa in the neighbourhood. The owner swears everything is normal, but somehow there's something about that phone that doesn't add up. Something dey there. Find am.

---

## 1. Contenu de l'APK

```bash
unzip -o app-release.apk -d apk && ls apk
```

```text
AndroidManifest.xml   (67 o)
classes.dex           (68 o)
assets/build_info.txt
assets/file_manifest.txt
res/values/strings.xml
META-INF/MANIFEST.MF
```

Tout est anormalement petit. `classes.dex` ne fait que 68 octets et commence par `fa ce fa ce` (magie bidon, pas un vrai DEX). Le manifest est une ligne de texte, pas du binaire XML. **L'APK est un leurre** — "everything looks normal" mais rien ne tourne vraiment.

---

## 2. Les deux indices textuels

```bash
cat apk/assets/file_manifest.txt
```

```text
classes.dex
classes2.dex
resources.arsc
lib/armeabi-v7a/libnative.so
```

Ce manifeste liste des fichiers **absents** de l'APK (`classes2.dex`, `resources.arsc`, `libnative.so`) : c'est le "something doesn't add up". Il oriente vers une anomalie structurelle, pas vers du code.

```bash
cat apk/assets/build_info.txt
```

```text
build_stamp=buildstamp-2026.03.14-r7
built_by=ci-runner-04
```

À retenir : le `build_stamp`.

---

## 3. L'anomalie : un champ "extra" ZIP

Un APK est un ZIP. En inspectant les en-têtes des entrées (ce qu'`unzip` n'affiche pas), l'entrée `classes.dex` porte un **champ extra** custom :

```python
import zipfile
z = zipfile.ZipFile("app-release.apk")
for zi in z.infolist():
    if zi.extra:
        print(zi.filename, zi.extra.hex())
```

```text
classes.dex  feca1c0000070a1802081c0809141e5c6f5b5871445b1d6e4419115c56120c11
```

Structure d'un champ extra ZIP : `[header_id (2o)][taille (2o)][données]`.

```text
feca      -> header_id = 0xCAFE  (marqueur custom)
1c00      -> taille = 0x001c = 28 octets
données   -> 00070a1802081c0809141e5c6f5b5871445b1d6e4419115c56120c11
```

28 octets planqués dans les métadonnées ZIP. Invisible à `unzip`, invisible à `strings`.

---

## 4. Déchiffrement

Le payload fait 28 octets, taille d'un flag. Test XOR à clé répétée avec le `build_stamp` relevé plus tôt :

```python
hid = bytes.fromhex("00070a1802081c0809141e5c6f5b5871445b1d6e4419115c56120c11")
key = b"buildstamp-2026.03.14-r7"
print(bytes(hid[i] ^ key[i % len(key)] for i in range(len(hid))))
```

```text
b'brctf{hidd3n_in_th3_p4ck4ge}'
```

**Flag :** `brctf{hidd3n_in_th3_p4ck4ge}`

---

## Récapitulatif de la chaîne d'exploitation

1. **`unzip`** → APK entièrement bidon (dex/manifest tronqués).
2. **`file_manifest.txt`** → fichiers manquants = l'anomalie est structurelle.
3. **`zipfile.infolist()`** → champ extra `0xCAFE` de 28 o sur l'entrée `classes.dex`.
4. **`build_info.txt`** → `build_stamp` = clé XOR.
5. **XOR répété** → flag.

> **Concept clé :** le format ZIP (donc APK, JAR, DOCX…) réserve à chaque entrée un **champ extra** optionnel, prévu pour des métadonnées (timestamps Unix, alignement Zip64…). Rien n'empêche d'y cacher des données arbitraires : `unzip` les ignore et `strings` sur l'archive ne les met pas en évidence parmi le reste. Pour les voir, il faut parser les en-têtes locaux/centraux (`zipfile.infolist()`, `zipdetails`, un hexdump ciblé). La clé de déchiffrement était fournie en clair dans un autre asset — ici le `build_stamp` — ce qui est fréquent : l'astuce n'est pas la crypto (simple XOR) mais l'**emplacement** de la donnée.

---

***— 3ch0***
