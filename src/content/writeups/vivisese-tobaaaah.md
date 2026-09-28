---
# Imported from Obsidian: CTF/ESIG Tech Arena CTF/writeup_vivisese_tobaaaah.md
title: Vivisese tobaaaah
category: Cryptography
ctf: ESIG Tech Arena 2026
competition: esig-tech-arena-2026
date: 2026-09-26
summary: Un développeur a déployé un système de signature DSA pour authentifier des transactions bancaires. En auditant les logs réseau, vous interceptez deux transactions signées avec la…
tags:
- cryptography
- esig-tech-arena-2026
points: 150
lang: fr
imported: true
---

- **Catégorie :** Crypto — easy
- **Points :** 150 (dynamiques, 150 → 50)
- **Format du flag :** `CTF{...}`
- **Auteur du write-up :** 3ch0
- **Flag :** `CTF{dsa_n0nc3_r3us3_priv4t3_k3y_r3c0very}`

---

## Énoncé

> Un développeur a déployé un système de signature DSA pour authentifier des transactions bancaires. En auditant les logs réseau, vous interceptez **deux transactions signées avec la même clé privée**. Le flag a été chiffré avec cette clé privée. Retrouvez la clé privée et déchiffrez le flag.

Fichiers fournis : `params.txt` (paramètres DSA `p, q, g, y`), `signatures.txt` (2 messages + signatures), `flag.enc` (flag chiffré en AES).

---

## 1. Observation clé

Dans `signatures.txt`, les deux signatures ont **exactement le même `r`** :

```
r  = 0x296615da7b269db3e42f043a07dff8a17cfa88ad   (message 1)
r  = 0x296615da7b269db3e42f043a07dff8a17cfa88ad   (message 2)
```

En DSA :

```
r = (g^k mod p) mod q          ← ne dépend QUE du nonce k
s = k⁻¹ · (H(m) + x·r) mod q
```

`r` ne dépend que de `k`. Deux signatures avec le même `r` ⇒ **même nonce `k` réutilisé**. C'est la faille fatale de DSA/ECDSA : elle permet de récupérer la clé privée.

---

## 2. Théorie de l'attaque (nonce reuse)

On a deux équations avec le même `k` et le même `x` :

```
s1 = k⁻¹ · (h1 + x·r) mod q
s2 = k⁻¹ · (h2 + x·r) mod q
```

**Étape 1 — retrouver le nonce `k`.** On soustrait :

```
s1 − s2 = k⁻¹ · (h1 − h2) mod q
⇒ k = (h1 − h2) · (s1 − s2)⁻¹ mod q
```

**Étape 2 — retrouver la clé privée `x`.** À partir de `s1 = k⁻¹·(h1 + x·r)` :

```
s1·k = h1 + x·r mod q
⇒ x = (s1·k − h1) · r⁻¹ mod q
```

Tous les calculs se font **modulo `q`** (l'ordre du sous-groupe), pas `p`.

---

## 3. Déchiffrement du flag

`flag.enc` indique la construction :

```
# AES-256-CBC(key = SHA256(x), iv = ...)
iv = ede7c4c10bf0010ecde1c64938c22411
ct = 9634750cd697c28d3a2859a518c7659a4d827ffea75a41f2168d0c198697a5305baf38e3ae4f2a7e06f6841d675e3713
```

Seule ambiguïté : comment `x` (un entier) est transformé en octets avant `SHA256`. En testant les encodages classiques, le bon est **`x` sur 32 octets big-endian** :

```
key = SHA256( x.to_bytes(32, 'big') )
```

Puis AES-256-CBC avec l'IV fourni.

---

## 4. Exploitation — solve.py

```python
import hashlib
from Crypto.Cipher import AES

q  = 0x9760508f15230bccb292b982a2eb840bf0581cf5
h1 = 0x8d042cfd443601ac262a7d6399ad98afd486beb1
h2 = 0xe498728819eef2cc601b9246336399b733349d25
r  = 0x296615da7b269db3e42f043a07dff8a17cfa88ad
s1 = 0x5006f2ded64f88bffef4e663db2449d48aa8ea8e
s2 = 0x7e23c53549e8fc484b22b2eb951f6efb83273ada
inv = lambda a, m: pow(a, -1, m)

# 1) nonce reuse -> k -> x
k = (h1 - h2) * inv((s1 - s2) % q, q) % q
x = (s1 * k - h1) * inv(r, q) % q
print("k =", hex(k))
print("x =", hex(x))

# 2) dechiffrement
iv = bytes.fromhex("ede7c4c10bf0010ecde1c64938c22411")
ct = bytes.fromhex("9634750cd697c28d3a2859a518c7659a4d827ffea75a41f2168d0c198697a5305baf38e3ae4f2a7e06f6841d675e3713")
key = hashlib.sha256(x.to_bytes(32, "big")).digest()   # SHA256(x) sur 32 octets
pt  = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
pt  = pt[:-pt[-1]]                                      # unpad PKCS#7
print(pt.decode())
```

### Sortie

```
k = 0x3787c90128e4098d890b9f09a6fc6524d84c491a
x = 0x3aef71213300eea84ab5176e1c88f726f18b996d
CTF{dsa_n0nc3_r3us3_priv4t3_k3y_r3c0very}
```

*(On peut vérifier `x` en recalculant `y = g^x mod p` et en comparant à la clé publique de `params.txt`.)*

---

## 5. Flag

```
CTF{dsa_n0nc3_r3us3_priv4t3_k3y_r3c0very}
```

---

## 6. Leçons

- En DSA/ECDSA, le nonce `k` doit être **unique et secret** pour chaque signature. Le réutiliser (même `r`) laisse fuiter la clé privée avec deux signatures seulement.
- « Paramètres FIPS standard » ne garantit rien : la faille est dans la **génération du nonce**, pas dans les paramètres de courbe/groupe.
- Bon réflexe crypto : dès qu'on voit deux signatures partageant `r`, penser immédiatement au *nonce reuse*.
- Bonne pratique moderne : nonce **déterministe** (RFC 6979) dérivé du message et de la clé, pour éliminer ce risque.

_**— 3ch0**_
