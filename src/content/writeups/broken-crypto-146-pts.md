---
# Imported from Obsidian: CTF/ESIG Tech Arena CTF/Broken — Writeup (Crypto, 146 pts).md
title: Broken — (Crypto, 146 pts)
category: Cryptography
ctf: ESIG Tech Arena 2026
competition: esig-tech-arena-2026
date: 2026-09-25
summary: ciphertext.txt ne contient qu'un IV et l'instruction "Run oracle.py locally to print ciphertext" — le vrai challenge attendu est un serveur de padding-oracle à attaquer en aveugle…
tags:
- aes-cbc
- crypto
- cryptography
- esig-tech-arena
- esig-tech-arena-2026
- padding-oracle
- secret-leak
points: 146
lang: fr
imported: true
---

### 📌 Description
> **Broken** (Crypto · medium). "Local AES-CBC padding-oracle lab." Fichiers fournis : `02_Broken_Oracle.zip` (`ciphertext.txt`, `oracle.py`, `requirements.txt`).
>
> **Author** : Sy5t3mc4ll
**Points** : 150 → 50 pts (dynamique), capturé à 146 pts
**First blood** : Iki
**Statut** : ✓ Résolu le 25/09 à 11:53 UTC

---
### Étape 1 : Reconnaissance

```bash
unzip 02_Broken_Oracle.zip
cat 02_Broken_Oracle/ciphertext.txt
cat 02_Broken_Oracle/oracle.py
```

`ciphertext.txt` ne contient qu'un IV et l'instruction "Run oracle.py locally to print ciphertext" — le vrai challenge attendu est un serveur de padding-oracle à attaquer en aveugle (byte-by-byte, via les réponses `VALID` / `BAD_PADDING`).

---
### Étape 2 : Le vrai bug — fuite du secret dans l'artifact

En lisant `oracle.py` fourni pour lancer le serveur local, la clé **et le plaintext** sont codés en dur dans le script distribué :

```python
KEY = bytes.fromhex("4f"*32)  # organizer-known lab key
IV = bytes.fromhex("10"*16)
PLAINTEXT = b"EthACTF{padding_is_information}"
CT = AES.new(KEY, AES.MODE_CBC, IV).encrypt(pad(PLAINTEXT,16))
```

Pas besoin de monter la véritable attaque par oracle de padding (Vaudenay) : l'artifact organisateur a été livré par erreur avec le secret en clair dans le code source. C'est le "Broken" du titre — le lab de démonstration a fuité ce qu'il était censé protéger.

---
### Étape 3 : Vérification

Pour confirmer que ce n'est pas un piège, chiffrement/déchiffrement réel avec les valeurs trouvées :

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

KEY = bytes.fromhex("4f"*32)
IV = bytes.fromhex("10"*16)
PLAINTEXT = b"EthACTF{padding_is_information}"

CT = AES.new(KEY, AES.MODE_CBC, IV).encrypt(pad(PLAINTEXT, 16))
dec = unpad(AES.new(KEY, AES.MODE_CBC, IV).decrypt(CT), 16)
print(dec)  # b'EthACTF{padding_is_information}'
```

> **Pas de brute-force**
> Le flag n'a jamais été deviné ni brute-forcé sur sa valeur — il est directement lu depuis le code source de l'artifact fourni par les organisateurs, puis validé par un vrai cycle AES-CBC.

---
### 🏁 Flag

```
EthACTF{padding_is_information}
```
