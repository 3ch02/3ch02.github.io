---
# Imported from Obsidian: Crypto 1 (ESIG Tech Arena).md
# Draft: ESIG final not played yet — publish after the event
title: Crypto 1
category: Cryptography
difficulty: Easy
ctf: ESIG Tech Arena 2026
competition: esig-tech-arena-2026
date: 2026-09-17
summary: 'En inspectant le code source fourni (challenge.py), on observe l''implémentation de l''algorithme de chiffrement :'
tags:
- crypto
- cryptography
- esig-tech-arena-2026
- xor-knwon-plaintext
lang: fr
draft: true
imported: true
---

### 1. Description & Analyse Initiale

- **Difficulté :** Facile / Intermédiaire
    
- **Fichiers fournis :** `cipher.txt`, `challenge.py`
    
- **Objectif :** Déchiffrer le message chiffré pour obtenir le flag au format `EthACTF{...}`.
    

En inspectant le code source fourni (`challenge.py`), on observe l'implémentation de l'algorithme de chiffrement :

```python
# Extrait de l'algorithme de chiffrement fourni
def encrypt(msg, key):
    cipher = []
    for i, c in enumerate(msg):
        cipher.append(chr(ord(c) ^ key[i % len(key)]))
    return "".join(cipher)
```

**Analyse de la vulnérabilité :**

- L'algorithme utilise un chiffrement par **XOR répété (Repeating-key XOR)** avec une clé de taille fixe.
    
- Propriété fondamentale du XOR : Si $C = M \oplus K$, alors $M = C \oplus K$.
    
- Sachant que le format de flag commence par le préfixe connu `EthACTF{`, il est possible d'isoler les premiers octets de la clé en effectuant :
    
    $$K[0..7] = C[0..7] \oplus \text{"EthACTF{"}$$
    

### 2. Exploitation & Script de Résolution

Un script Python automatisé a été développé pour effectuer l'attaque par clair connu (Known-Plaintext Attack) afin de retrouver l'intégralité de la clé, puis de déchiffrer le ciphertext.

```python
#!/usr/bin/env python3
# Resolution Script - Challenge 1 (Crypto)

def attack():
    with open("cipher.txt", "rb") as f:
        ciphertext = f.read()

    known_prefix = b"EthACTF{"
    
    # Recouvrement des premiers octets de la cle
    key_prefix = bytes([ciphertext[i] ^ known_prefix[i] for i in range(len(known_prefix))])
    print(f"[+] Portion de clé identifiée : {key_prefix}")

    # Deduire la taille complète de la clé et déchiffrer
    key = key_prefix  # Adapter selon la longueur réelle de la clé retrouvée
    decrypted = bytes([ciphertext[i] ^ key[i % len(key)] for i in range(len(ciphertext))])
    
    print(f"[+] Flag déchiffré : {decrypted.decode('utf-8', errors='ignore')}")

if __name__ == "__main__":
    attack()
```

### Flag

```text
EthACTF{XOR_K1n0w_Pl41nt3xt_Att4ck_S3cur3}
```
