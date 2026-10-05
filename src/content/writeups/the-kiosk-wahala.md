---
# Imported from Obsidian: CTF/BRCTF/The-Kiosk-Wahala.md
title: The Kiosk Wahala
category: Cryptography
difficulty: Hard
ctf: brCTF 2026
competition: brctf-2026
date: 2026-10-02
summary: 'Énoncé : Kofi opened his kiosk one morning and everything looked normal. But after one customer came and left, Kofi started shouting that somebody had entered his business without…'
tags:
- brctf-2026
- cryptography
points: 150
lang: fr
imported: true
---

> Compétition : **brCTF** — Challenge ID#11

## Informations

- **Catégorie :** Mobile
- **Difficulté :** Hard
- **Points :** 150
- **Auteur du write-up :** 3ch0
- **Flag :** `brctf{n4t1v3_l1b_g1v3s_1t_up}`

> **Énoncé :** Kofi opened his kiosk one morning and everything looked normal. But after one customer came and left, Kofi started shouting that somebody had entered his business without permission. Now everyone is blaming everyone. Find out what really happened.

---

## 1. Contenu de l'archive

```bash
tar -xvf app_data.tar
```

```text
lib/libnative.so
shared_prefs/app_config.xml
```

Deux artefacts d'une application Android : une **bibliothèque native** (`.so`) et un fichier de **préférences partagées** (`shared_prefs`), là où une app stocke sa configuration.

---

## 2. Le blob chiffré

```bash
cat shared_prefs/app_config.xml
```

```text
<?xml version="1.0" encoding="utf-8"?>
<map>
    <string name="cfg_blob">WE+aimLbGTGgL6gOMxCsXtdl+hyyCrvn64IEV63/7cbhSAlgMVL61lTRqPSHf/o1</string>
</map>
```

`cfg_blob` est du base64. Décodé, il fait **48 octets**, soit exactement **3 blocs de 16** → chiffrement par blocs de type **AES** (ECB ou CBC).

---

## 3. La clé dans la bibliothèque native

```bash
file lib/libnative.so
```

```text
libnative.so: ELF 64-bit LSB shared object, x86-64, ... not stripped
```

`not stripped` = les symboles sont présents. Un simple `strings` suffit :

```bash
strings libnative.so
```

```text
get_key_marker
sk_live_9f2a7c41
SECRET_KEY
_native.c
```

Trois éléments parlants : une fonction `get_key_marker`, un symbole `SECRET_KEY`, et surtout **`sk_live_9f2a7c41`** — une chaîne de **16 caractères exactement**, soit la taille d'une clé **AES-128**.

---

## 4. Déchiffrement

AES-128 avec `sk_live_9f2a7c41` comme clé. Test ECB puis CBC (IV nul) :

```python
import base64
from Crypto.Cipher import AES

blob = base64.b64decode("WE+aimLbGTGgL6gOMxCsXtdl+hyyCrvn64IEV63/7cbhSAlgMVL61lTRqPSHf/o1")
key  = b"sk_live_9f2a7c41"

print(AES.new(key, AES.MODE_CBC, iv=b"\x00"*16).decrypt(blob))
```

```text
b'last_sync_token:brctf{n4t1v3_l1b_g1v3s_1t_up}\x03\x03\x03'
```

Mode **CBC, IV = 16 octets nuls**, padding PKCS7 (`03 03 03`). Le plaintext :

```text
last_sync_token:brctf{n4t1v3_l1b_g1v3s_1t_up}
```

**Flag :** `brctf{n4t1v3_l1b_g1v3s_1t_up}`

---

## Récapitulatif de la chaîne d'exploitation

1. **`tar -xvf`** → une lib native + un fichier de prefs.
2. **`cfg_blob`** (base64) → 48 octets = 3 blocs AES.
3. **`strings libnative.so`** (non strippée) → clé `sk_live_9f2a7c41` (16 o = AES-128).
4. **AES-128-CBC, IV = 0** → `last_sync_token:` + flag.

> **Concept clé :** un secret embarqué dans une bibliothèque native (`.so`) n'est **pas** protégé. Beaucoup de devs mobiles déplacent une clé du code Java/Kotlin vers du C/JNI en croyant la cacher, mais elle reste en clair dans le binaire : `strings` (si non strippée) ou un désassembleur la sortent en quelques secondes. Ici la clé AES servait à chiffrer les prefs ; la connaître casse tout. Le titre le résume : *native lib gives it up*.

---

***— 3ch0***
