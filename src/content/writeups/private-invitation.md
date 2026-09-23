---
# Imported from Obsidian: CTF/hackviser/EcowsCTF{}/📑 Writeup Challenge -Private Invitation.md
title: Private Invitation
category: Cryptography
ctf: EcowsCTF (Hackviser)
date: 2026-08-07
summary: 'L''input est un nombre entier géant (un "BigInt") : 45869628935703537024006250072939111438334586890787318634838246978308613066427488828159646243765820716013170184703604327526525'
tags:
- crypto
- cryptography
- cyberchef
- ecowsctf
lang: fr
imported: true
---

#### Donnée
```
encoded_flag: 45869628935703537024006250072939111438334586890787318634838246978308613066427488828159646243765820716013170184703604327526525
```

---

#### Etape 1- Analyse de l'input

L'input est un **nombre entier géant** (un "BigInt") :  
`45869628935703537024006250072939111438334586890787318634838246978308613066427488828159646243765820716013170184703604327526525`

En cryptographie CTF, lorsqu'on voit un tel nombre, il s'agit presque toujours d'une chaîne de caractères convertie en octets (bytes), puis ces octets sont interprétés comme un seul grand nombre entier (souvent via une fonction comme `bytes_to_long` de la bibliothèque _PyCryptodome_).

#### Etape 2. Étape de Résolution : "Long to Bytes"

La méthode consiste à inverser ce processus :

1. **Conversion en Hexadécimal** : Transformer le nombre base 10 en base 16.
2. **Conversion Hex vers ASCII** : Transformer chaque paire de caractères hexadécimaux en leur caractère correspondant.

Pour une résolution rapide sans code :

- Allez sur CyberChef.
- Utilisez l'opération **"From Decimal"**.
- Le résultat apparaît instantanément.

Utilisation de Python

En Python, on peut utiliser la méthode native ou la bibliothèque `Crypto.Util.number` :

```python
from Crypto.Util.number import long_to_bytes

encoded_flag = 45869628935703537024006250072939111438334586890787318634838246978308613066427488828159646243765820716013170184703604327526525

# Méthode simple sans bibliothèque externe
hex_string = hex(encoded_flag)[2:] # On enlève le '0x'
flag = bytes.fromhex(hex_string).decode()

print(flag)
```

#### Flag  🚩: `

> **Success**
> **`EcowasCTF{w3lc0m3_t0_th3_l34gu3_f0rk_dbd5e81090a750}`**
