---
# Imported from Obsidian: CTF/BRCTF/HideAndSeek.md
title: HideAndSeek
category: Mobile
difficulty: Easy
ctf: brCTF 2026
competition: brctf-2026
date: 2026-10-01
summary: 'Énoncé : Exactly what it sounds like — the developers hid something and dared anyone to seek it. The app plays innocent, but the name is a challenge. Somewhere in here, something…'
tags:
- brctf-2026
- mobile
points: 50
lang: fr
imported: true
---

> Compétition : **brCTF** — Challenge ID#7

## Informations

- **Catégorie :** Mobile (Android)
- **Difficulté :** Easy
- **Points :** 50
- **Auteur du write-up :** 3ch0
- **Flag :** `BRCTF{man1f3st_1s_th3_h1d1ng_sp0t}`

> **Énoncé :** Exactly what it sounds like — the developers hid something and dared anyone to seek it. The app plays innocent, but the name is a challenge. Somewhere in here, something is waiting to be found.

---

## 1. Décompilation de l'APK

```bash
apktool d HideAndSeek.apk
cd HideAndSeek
```

---

## 2. Recherche du flag

On grep le préfixe `BRCTF` sur tout le code décompilé :

```bash
grep -ri BRCTF .
```

Rien dans le smali (hormis le nom de package `com.brctf.hideandseek`). En revanche, le `AndroidManifest.xml` contient des balises `meta-data` suspectes :

```xml
<meta-data android:name="com.brctf.hideandseek.build_channel" android:value="production"/>
<meta-data android:name="com.brctf.hideandseek.analytics_id" android:value="a3f9c2e1"/>
<meta-data android:name="com.brctf.hideandseek.sync_token"
           android:value="UWxKRFZFWjdiV0Z1TVdZemMzUmZNWE5mZEdnelgyZ3haREZ1WjE5emNEQjBmUT09"/>
```

Les deux premières sont du leurre crédible (canal de build, ID analytics). La troisième, `sync_token`, est une longue chaîne manifestement **base64** — c'est la cachette, et le nom du challenge (« hide and seek ») plus l'énoncé (« the name is a challenge ») pointaient vers ça.

> Le `AndroidManifest.xml` est souvent négligé en reverse Android alors qu'il peut contenir des secrets planqués dans des `meta-data`.

---

## 3. Décodage (double base64)

On décode une première fois :

```bash
echo "UWxKRFZFWjdiV0Z1TVdZemMzUmZNWE5mZEdnelgyZ3haREZ1WjE5emNEQjBmUT09" | base64 -d
```

```text
QlJDVEZ7bWFuMWYzc3RfMXNfdGgzX2gxZDFuZ19zcDB0fQ==
```

Le résultat est **encore du base64** (il se termine par `==` et ne ressemble pas à du texte). On décode une seconde fois :

```bash
echo "QlJDVEZ7bWFuMWYzc3RfMXNfdGgzX2gxZDFuZ19zcDB0fQ==" | base64 -d
```

```text
BRCTF{man1f3st_1s_th3_h1d1ng_sp0t}
```

**Flag :** `BRCTF{man1f3st_1s_th3_h1d1ng_sp0t}`

> Soit *« manifest is the hiding spot »* — le flag confirme lui-même où il était caché.

---

## Récapitulatif de la chaîne d'exploitation

1. **apktool** → décompilation de l'APK.
2. **`grep BRCTF`** → rien dans le smali, mais un `meta-data sync_token` suspect dans le manifeste.
3. **base64 -d** → donne encore du base64 (double encodage).
4. **base64 -d** (2ᵉ passe) → flag.

> **Concept clé :** le `AndroidManifest.xml` fait partie de la surface d'analyse au même titre que le code. Développeurs et attaquants y planquent parfois des secrets dans des `<meta-data>` d'apparence anodine (`sync_token`, `analytics_id`…). Un encodage (ici un **double base64**) ne protège rien : il suffit de reconnaître la forme (chaîne alphanumérique terminée par `=`/`==`) et de décoder jusqu'à obtenir du texte lisible.

---

***— 3ch0***
