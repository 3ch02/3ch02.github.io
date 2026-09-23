---
# Imported from Obsidian: CTF/Writeup CTF Hackropole/Crypto/🚩 Claire connu (Known Plaintext)-  XOR.md
title: Clair connu (XOR, known plaintext)
category: Cryptography
ctf: Hackropole (FCSC)
date: 2026-08-07
summary: 'Le XOR est réversible. Si A⊕B=C, alors :'
tags:
- cryptography
- hackropole
- known-plaintext
- xor
lang: fr
imported: true
---

##### Code source : 
```
import os

from Crypto.Util.number import long_to_bytes

from Crypto.Util.strxor import strxor
FLAG = open("flag.txt", "rb").read()
key = os.urandom(4) * 20

c = strxor(FLAG, key[:len(FLAG)])

print(c.hex())
```

##### Sortie:
```
d91b7023e46b4602f93a1202a7601304a7681103fd611502fa684102ad6d1506ab6a1059fc6a1459a8691051af3b4706fb691b54ad681b53f93a4651a93a1001ad3c4006a825
```
### Description du Challenge

- **L'obstacle :** Le message est chiffré par un XOR. Normalement, si la clé était aussi longue que le flag et totalement aléatoire (One-Time Pad), ce serait inviolable.
    
- **Le problème :** Ici, la clé est très courte (4 octets seulement) et se répète. C'est ce qu'on appelle **XOR à clé répétitive**.
    
- **La faille :** Nous connaissons probablement le début du flag (le format standard comme `FCSC{`, `picoCTF{`, `IPNET{` etc.). **En cryptographie XOR, si on connaît une partie du message clair (M) et le message chiffré (C), on peut retrouver la clé (K) avec la propriété :** 
$$
K=M⊕C
$$
    

---

### 3. Notions de Base : Le XOR répétitif

#### A. La propriété magique du XOR (⊕)

Le XOR est réversible. Si A⊕B=C, alors :

$$
- A⊕C=B
$$
    
$$
 B⊕C=A
$$
    
 C'est pour cela qu'on utilise la même fonction pour chiffrer et déchiffrer.
#### B. La répétition

Si la clé est `[k1, k2, k3, k4]`, alors :

- L'octet 0 du flag est XORé avec `k1`.
    
- L'octet 1 avec `k2`.
    
- L'octet 2 avec `k3`.
    
- L'octet 3 avec `k4`.
    
- **L'octet 4 est à nouveau XORé avec `k1` !**
    

#### C. L'attaque par "Clair Connu" (Known Plaintext Attack)

Si tu devines les 4 premiers caractères du flag (par exemple `FCSC` dans notre cas ou encore IPNET), tu peux retrouver les 4 octets de la clé. Une fois que tu as la clé, tu n'as plus qu'à déchiffrer tout le reste.

---

### Résolution 

Ainsi vu qu'on connaît le début du flag qui est **FCSC{** , nous allons lancer **l'attaque par Known Plaintext (Claire connu)**

### 1. La Logique de calcul

**Le XOR fonctionne octet par octet.** Si Message⊕Cle=Cypher, alors Cle=Message⊕Cypher.

Calculons les 4 premiers octets de la clé :

1. `'F'` ⊕ `0xd9`
    
2. `'C'` ⊕ `0x1b`
    
3. `'S'` ⊕ `0x70`
    
4. `'C'` ⊕ `0x23`
    

### 2. Le Script de Résolution

Voici le code Python pour extraire la clé et déchiffrer tout le message :

```
from Crypto.Util.strxor import strxor

# Le message chiffré (hex)
hex_c = "d91b7023e46b4602f93a1202a7601304a7681103fd611502fa684102ad6d1506ab6a1059fc6a1459a8691051af3b4706fb691b54ad681b53f93a4651a93a1001ad3c4006a825"
c = bytes.fromhex(hex_c)

# 1. On retrouve la clé grâce au début du flag "FCSC" (4 octets)
# On XOR les 4 premiers octets du chiffré avec "FCSC"
prefix = b"FCSC"
key = strxor(c[:4], prefix)
print(f"[*] Clé trouvée : {key} (hex: {key.hex()})")

# 2. On étend la clé pour qu'elle fasse la taille du message chiffré
# La clé se répète : key * (longueur_message // 4 + 1)
full_key = (key * (len(c) // len(key) + 1))[:len(c)]

# 3. On déchiffre le message complet
flag = strxor(c, full_key)

print(f"\n[!] FLAG : {flag.decode()}")
```

La clé trouvée : **b'\x9fX#`'**

### Flag 🚩 : 
```
FCSC{3ebfb1b880d802cb96be0bb256f4239c27971310cdfd1842083fbe16b3a2dcf7}
```
