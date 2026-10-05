---
# Imported from Obsidian: CTF/BRCTF/Ashaiman.md
title: Ashaiman
category: Mobile
difficulty: Easy
ctf: brCTF 2026
competition: brctf-2026
date: 2026-10-01
summary: 'Énoncé : The first app off the studio''s assembly line. It runs, it looks ordinary, but something is tucked away inside the package. Your first job: learn to take an Android app…'
tags:
- brctf-2026
- mobile
points: 50
lang: fr
imported: true
---

> Compétition : **brCTF** — Challenge ID#5

## Informations

- **Catégorie :** Mobile (Android)
- **Difficulté :** Easy
- **Points :** 50
- **Auteur du write-up :** 3ch0
- **Flag :** `BRCTF{ash4iman_ins1d3r_pr1c3_unlocked}`

> **Énoncé :** The first app off the studio's assembly line. It runs, it looks ordinary, but something is tucked away inside the package. Your first job: learn to take an Android app apart and see what the developer left behind. Where do apps keep the things they'd rather you didn't find?

---

## 1. Décompilation de l'APK

Un APK est une archive ZIP contenant le bytecode Dalvik (`.dex`), les ressources et le manifeste. On le décompile en **smali** (assembleur Dalvik lisible) avec **apktool** :

```bash
apktool d Ashaiman.apk
cd Ashaiman
```

```text
I: Baksmaling classes.dex...
I: Baksmaling classes2.dex...
I: Baksmaling classes3.dex...
I: Copying assets and libs...
```

---

## 2. Recherche du flag dans le code

Premier réflexe : grep sur le préfixe du flag dans tout le code décompilé.

```bash
grep -ri BRCTF .
```

Le flag n'apparaît pas en clair, mais le package `com.brctf.ashaiman` ressort, avec une classe très parlante : **`MarketLore`**. Elle contient trois tableaux d'octets et une méthode `xor` :

```
MarketLore;->KEY:[B
MarketLore;->AUTH_TOKEN:[B
MarketLore;->FLAG_ENC:[B
MarketLore;->xor([B[B)[B
```

> Le flag n'est pas stocké en clair : il est **chiffré par XOR** et déchiffré à l'exécution.

---

## 3. Analyse de `MarketLore.smali`

```bash
cat smali_classes3/com/brctf/ashaiman/MarketLore.smali
```

### La clé (`KEY`)

Dans le constructeur statique `<clinit>`, la clé est une simple chaîne UTF-8 :

```text
const-string v0, "ASHAIMAN_MARKET_SECRET_CODE"
...
sput-object v0, Lcom/brctf/ashaiman/MarketLore;->KEY:[B
```

→ `KEY = "ASHAIMAN_MARKET_SECRET_CODE"`

### Le flag chiffré (`FLAG_ENC`)

Tableau de 38 octets (`0x26`) rempli via `fill-array-data :array_1` :

```text
:array_1
.array-data 1
    0x3t 0x1t 0xbt 0x15t 0xft 0x36t 0x20t 0x3dt 0x37t 0x79t
    0x28t 0x3ft 0x2at 0x2bt 0xbt 0x36t 0x3dt 0x36t 0x72t 0x36t
    0x76t 0x26t 0x0t 0x33t 0x3dt 0x75t 0x26t 0x72t 0xct 0x3dt
    0x2ft 0x25t 0x22t 0x22t 0x25t 0x3at 0x29t 0x3ct
.end array-data
```

### La logique (`getInsiderPrice`)

La méthode `getInsiderPrice(guess)` vérifie que `xor(guess, KEY) == AUTH_TOKEN`, et seulement alors renvoie `xor(FLAG_ENC, KEY)`. Autrement dit, l'app exige un mot de passe avant d'afficher le flag — une barrière **inutile en reverse statique** : rien ne nous empêche de déchiffrer `FLAG_ENC` directement.

La fonction `xor` est un XOR classique avec clé répétée (`key[i % len(key)]`).

---

## 4. Déchiffrement du flag

On reproduit le XOR en Python, hors de l'app :

```python
key = b"ASHAIMAN_MARKET_SECRET_CODE"
flag_enc = [0x3,0x1,0xb,0x15,0xf,0x36,0x20,0x3d,0x37,0x79,0x28,0x3f,
            0x2a,0x2b,0xb,0x36,0x3d,0x36,0x72,0x36,0x76,0x26,0x0,0x33,
            0x3d,0x75,0x26,0x72,0xc,0x3d,0x2f,0x25,0x22,0x22,0x25,0x3a,
            0x29,0x3c]

flag = bytes(flag_enc[i] ^ key[i % len(key)] for i in range(len(flag_enc)))
print(flag.decode())
```

```text
BRCTF{ash4iman_ins1d3r_pr1c3_unlocked}
```

**Flag :** `BRCTF{ash4iman_ins1d3r_pr1c3_unlocked}`

---

## Bonus — le mot de passe caché (`AUTH_TOKEN`)

Par curiosité, on déchiffre aussi `AUTH_TOKEN` pour retrouver le `guess` attendu par l'app. Puisque la vérification est `xor(guess, KEY) == AUTH_TOKEN`, on a `guess = xor(AUTH_TOKEN, KEY)` :

```python
auth = [0x22,0x3b,0x29,0x28,0x3b,0x20,0x20,0x20]
print(bytes(auth[i] ^ key[i % len(key)] for i in range(len(auth))).decode())
# -> chairman
```

Le mot magique était **`chairman`** : saisi dans le WebView, il aurait débloqué le flag à l'exécution. Le reverse statique permet de l'ignorer complètement.

---

## Récapitulatif de la chaîne d'exploitation

1. **apktool** → décompilation de l'APK en smali.
2. **`grep BRCTF`** → repérage de la classe `MarketLore` (KEY / AUTH_TOKEN / FLAG_ENC + xor).
3. **Analyse smali** → extraction de `KEY` (chaîne) et `FLAG_ENC` (tableau d'octets).
4. **XOR en Python** → flag, sans exécuter l'app ni connaître le mot de passe.

> **Concept clé :** du « security through obscurity ». Chiffrer un secret par XOR avec une clé **embarquée dans le même binaire** n'offre aucune protection : quiconque décompile l'APK (apktool / jadx) récupère la clé et le texte chiffré, et refait l'opération. Les secrets (clés d'API, tokens, flags) ne doivent jamais être stockés côté client, encodés ou « chiffrés » soient-ils.

---

***— 3ch0***
