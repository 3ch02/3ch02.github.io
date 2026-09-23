---
# Imported from Obsidian: CTF/Writeup CTF Hackropole/Crypto/🚩 SMIC 2.md
title: SMIC 2
category: Cryptography
ctf: Hackropole (FCSC)
date: 2026-08-07
summary: Nous avons un message chiffré c et une clé publique (n,e). L'objectif est de retrouver le message original m. En temps normal, le déchiffrement RSA nécessite la clé privée d. Pour…
tags:
- cryptography
- hackropole
lang: fr
imported: true
---

#### Données:

La sécurité du cryptosystème RSA repose sur un problème calculatoire bien connu.

On vous demande de déchiffrer le “message” chiffré `c` ci-dessous pour retrouver le “message” en clair `m` associé à partir de la clé publique `(n, e)`.

Valeurs :

- `e = 65537`
- `n = 632459103267572196107100983820469021721602147490918660274601`
- `c = 63775417045544543594281416329767355155835033510382720735973`

Le flag est `FCSC{xxxx}` où `xxxx` est remplacé par la valeur de `m` en écriture décimale.

### 1. Description du Challenge

Nous avons un message chiffré c et une clé publique (n,e). L'objectif est de retrouver le message original m. En temps normal, le déchiffrement RSA nécessite la clé privée d. Pour obtenir d, il faut impérativement connaître les facteurs premiers p et q du module n.

### 2. Notions de Base

#### La faille du petit module

La sécurité de RSA repose sur l'impossibilité de factoriser n en un temps raisonnable. Cependant, ici, n est un nombre de **60 chiffres** (environ 200 bits).

- Un module de **2048 bits** est considéré comme sûr.
    
- Un module de **200 bits** peut être factorisé en quelques secondes par un ordinateur moderne.
    

#### L'exposant privé d

Une fois que nous avons p et q, nous pouvons calculer l'indicatrice d'Euler ϕ(n)=(p−1)(q−1) et trouver d par la formule :

$$
d≡e−1(modϕ(n))

$$
### 3. Résolution (Le Plan)

1. **Factorisation** : Utiliser un outil comme `factordb.com` ou l'algorithme de Pollard's rho pour trouver p et q.
    
2. **Calcul de la clé privée** : Calculer d.
    
3. **Déchiffrement** : Calculer m=cd(modn).
    

### 4. Exploitation (Python)

Voici le script pour extraire le flag :

```
from Crypto.Util.number import inverse

# Données du challenge
e = 65537
n = 632459103267572196107100983820469021721602147490918660274601
c = 63775417045544543594281416329767355155835033510382720735973

p = 650655447295098801102272374367
q = 972033825117160941379425504503  

# ÉTAPE 2 : Calcul de d
phi = (p - 1) * (q - 1)
d = inverse(e, phi)

# ÉTAPE 3 : Déchiffrement
m = pow(c, d, n)

print(f"Le flag est : FCSC{{{m}}}")
```

### Flag 🚩:

```
FCSC{563694726501963824567957403529535003815080102246078401707923}
```
