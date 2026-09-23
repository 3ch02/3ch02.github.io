---
# Imported from Obsidian: CTF/picoCTF/Writeup - EVEN RSA CAN BE BROKEN.md
title: EVEN RSA CAN BE BROKEN
category: Cryptography
ctf: picoCTF
date: 2026-08-07
summary: Le challenge nous fournit un script de chiffrement RSA classique ainsi que les valeurs publiques générées lors de l'exécution, notamment le module $N$, l'exposant public $e$, et…
tags:
- crypto
- cryptography
- picoctf
- rsa
lang: fr
imported: true
---

## 📝 Description du Challenge
Le challenge nous fournit un script de chiffrement RSA classique ainsi que les valeurs publiques générées lors de l'exécution, notamment le module $N$, l'exposant public $e$, et le message chiffré (`cyphertext`). L'objectif est de retrouver le message en clair (le flag).

---

## 🔍 Analyse du Code Source

```
from sys import exit

from Crypto.Util.number import bytes_to_long, inverse

from setup import get_primes

e = 65537
def gen_key(k):
    """
   Generates RSA key with k bits

    """

    p,q = get_primes(k//2)

    N = p*q

    d = inverse(e, (p-1)*(q-1))

  

    return ((N,e), d)

  

def encrypt(pubkey, m):

    N,e = pubkey

    return pow(bytes_to_long(m.encode('utf-8')), e, N)

  

def main(flag):

    pubkey, _privkey = gen_key(1024)

    encrypted = encrypt(pubkey, flag)

    return (pubkey[0], encrypted)

  if __name__ == "__main__":

    flag = open('flag.txt', 'r').read()

    flag = flag.strip()

    N, cypher  = main(flag)

    print("N:", N)

    print("e:", e)

    print("cyphertext:", cypher)

    exit()
```

En analysant le script Python fourni :
* **Exposant public ($e$)** : `65537` (valeur standard).
* **Taille de la clé** : `1024` bits (ce qui signifie que $p$ et $q$ font environ 512 bits chacun).
* **Faiblesse cachée** : Le titre du challenge (*"EVEN RSA CAN BE BROKEN"*) est un indice majeur. En anglais, *Even* signifie **Pair**. Si le module $N$ est un nombre pair, cela signifie qu'il admet **2** comme facteur premier.

---

## 🛠️ Résolution & Données

### 1. Collecte des Données
* **N** : `21489041650872788199615801181954007174395591740579813115465182095448464994885195176112898557194881225897590401795659394628537714780780634782781701598233242`
* **e** : `65537`
* **Ciphertext ($c$)** : `390015366390254622528445189783290459154841511129068693669906093686881211911176154495905430332334989345447625245659898669620545269168189651673779709767459`

### 2. Factorisation de $N$
En vérifiant la parité de $N$ (ou en l'interrogeant sur **FactorDB**), on confirme le statut `FF` (Fully Factored). $N$ étant pair, sa décomposition en facteurs premiers est triviale :
* $p = 2$
* $q = \frac{N}{2} = 10744520825436394099807900590977003587197795870289906557732591047724232497442597588056449278597440612948795200897829697314268857390390317391390850799116621$

---

## 💻 Script d'Exploit (Python)

Pour récupérer le flag, on calcule l'indicateur d'Euler $\phi(N) = (p-1)(q-1)$, puis l'exposant de déchiffrement $d \equiv e^{-1} \pmod{\phi(N)}$, et enfin $m \equiv c^d \pmod N$.

```python
from Crypto.Util.number import long_to_bytes

# Données récupérées
N = 21489041650872788199615801181954007174395591740579813115465182095448464994885195176112898557194881225897590401795659394628537714780780634782781701598233242
e = 65537
ciphertext = 390015366390254622528445189783290459154841511129068693669906093686881211911176154495905430332334989345447625245659898669620545269168189651673779709767459

# Facteurs premiers (N est pair, donc p = 2)
p = 2
q = N // 2

# 1. Calcul de phi
phi = (p - 1) * (q - 1)

# 2. Calcul de la clé privée d
d = pow(e, -1, phi)

# 3. Déchiffrement
m_long = pow(ciphertext, d, N)

# 4. Conversion en texte
flag = long_to_bytes(m_long)
print(f"[+] Flag : {flag.decode('utf-8', errors='ignore')}")
````

## 🏁 Flag

> ****picoCTF{tw0_1$_pr!m305af7255}****

## 🧠 Ce qu'on a appris

- Un module RSA $N$ doit **impérativement** être le produit de deux grands nombres premiers _impairs_.
    
- Si $N$ est pair, l'attaquant connaît instantanément $p=2$, brisant totalement la sécurité du chiffrement.
