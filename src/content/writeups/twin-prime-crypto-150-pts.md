---
# Imported from Obsidian: CTF/ESIG Tech Arena CTF/Twin_Prime — Writeup (Crypto, 150 pts).md
title: Twin_Prime — (Crypto, 150 pts)
category: Cryptography
ctf: ESIG Tech Arena 2026
competition: esig-tech-arena-2026
date: 2026-09-25
summary: 'server.log révèle le bug volontaire : p et q ont été générés dans des fenêtres de recherche adjacentes, donc numériquement très proches l''un de l''autre — condition idéale pour une…'
tags:
- close-primes
- crypto
- cryptography
- esig-tech-arena
- esig-tech-arena-2026
- fermat-factorization
- rsa
points: 150
lang: fr
imported: true
---

### 📌 Description
> **Twin_Prime** (Crypto · medium). "RSA close-prime factorization with Fermat's method." Fichiers fournis : `ciphertext.txt`, `public.txt`, `server.log`.
>
> **Author** : Sy5t3mc4ll
**Points** : 150 → 50 pts (dynamique)
**Statut** : ✓ Résolu le 25/09 à 11:53 UTC

---
### Étape 1 : Reconnaissance

```bash
unzip 01_Twin_Primes.zip
cat 01_Twin_Primes/public.txt
cat 01_Twin_Primes/ciphertext.txt
cat 01_Twin_Primes/server.log
```

```
n = 3471605303404581706642752390571920128726786068134381741206617189546396853235200656986483021271494563418463778559212627900439146664455388132660321135446051
e = 65537

c = 2610654443316311148816207071826955422756359807198807738283574185791721354233120953308528683762441525666665555573172097272751236334844312517971348035942935

keygen: prime source=legacy-nearby-prime
keygen: p and q generated from adjacent search windows
```

`server.log` révèle le bug volontaire : **p et q ont été générés dans des fenêtres de recherche adjacentes**, donc numériquement très proches l'un de l'autre — condition idéale pour une attaque de Fermat.

---
### Étape 2 : Attaque de Fermat

Principe : si `p` et `q` sont proches, alors `n = p·q` peut s'écrire `n = a² - b²` avec `a = (p+q)/2` proche de `√n`. On teste `a = ⌈√n⌉, ⌈√n⌉+1, ...` jusqu'à ce que `a² - n` soit un carré parfait `b²`.

```python
import math

def fermat_factor(n):
    a = math.isqrt(n)
    if a * a < n:
        a += 1
    b2 = a * a - n
    while True:
        b = math.isqrt(b2)
        if b * b == b2:
            return a - b, a + b
        a += 1
        b2 = a * a - n

p, q = fermat_factor(n)
assert p * q == n
```

Convergence quasi instantanée (< 0.2 s) grâce à l'écart minime entre `p` et `q` :

```
p = 58920330136588522908700000493814743445023502692072242165153905317324409591983
q = 58920330136588522908700000493814743445023502692072242165153905317324409633997
```

---
### Étape 3 : Déchiffrement RSA classique

```python
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(c, d, n)
flag = m.to_bytes((m.bit_length() + 7) // 8, 'big')
print(flag)
```

> **Pourquoi Fermat et pas une factorisation générique**
> Une factorisation classique (Pollard rho, etc.) fonctionnerait aussi mais serait bien plus lente. Fermat est *spécifiquement* dévastateur quand `|p - q|` est petit, car le nombre d'itérations est proportionnel à cet écart — ici de l'ordre de quelques dizaines, contre une factorisation générale en `O(n^(1/4))`.

---
### 🏁 Flag

```
EthACTF{fermats_twins}
```
