---
# Imported from Obsidian: CTF/Writeup CTF Hackropole/Crypto/🚩 SMIC 1.md
# Draft: incomplete: script given but computed flag value never shown
title: SMIC 1
category: Cryptography
ctf: Hackropole (FCSC)
date: 2026-08-07
summary: 'On nous fournit : - Le message en clair m (sous forme d''un entier géant). - La clé publique composée du module n et de l''exposant e. Le but est de calculer le texte chiffré c et…'
tags:
- cryptography
- hackropole
- rsa
lang: fr
draft: true
imported: true
---

#### Données:

Le chiffrement RSA repose sur l’exponentiation modulaire de grands nombres. En utilisant les notations standards, calculez le “message” chiffré `c` correspondant au “message” en clair `m = 29092715682136811148741896992216382887663205723233009270907036164616385404410946789697601633832261873953783070225717396137755866976801871184236363551686364362312702985660271388900637527644505521559662128091418418029535347788018938016105431888876506254626085450904980887492319714444847439547681555866496873380` en utilisant la clé publique : `(n, e) = (115835143529011985466946897371659768942707075251385995517214050122410566973563965811168663559614636580713282451012293945169200873869218782362296940822448735543079113463384249819134147369806470560382457164633045830912243978622870542174381898756721599280783431283777436949655777218920351233463535926738440504017, 65537)`.

Le flag est `FCSC{xxxx}` où `xxxx` est remplacé par la valeur de `c` en écriture décimale.

### 1. Description du Challenge

On nous fournit :

- Le message en clair **m** (sous forme d'un entier géant).
    
- La clé publique composée du module **n** et de l'exposant **e**.
    

Le but est de calculer le texte chiffré **c** et de le soumettre sous le format `FCSC{c}`.

### 2. Notions de Base

#### L'opération de chiffrement RSA

En cryptographie RSA, le chiffrement consiste à élever le message m à la puissance e, le tout modulo n. La formule est la suivante :

c≡me(modn)

#### L'Exponentiation Modulaire

Pourquoi ne peut-on pas simplement faire me sur une calculatrice classique ? Parce que me est un nombre avec des dizaines de milliers de chiffres, ce qui ferait exploser la mémoire de n'importe quel ordinateur. On utilise l'algorithme d'**exponentiation modulaire rapide** (Square and Multiply), qui permet de calculer le reste de la division sans jamais calculer le nombre géant intermédiaire.

---

### 3. Résolution (Script Python)

En Python, l'opération me(modn) est intégrée de façon extrêmement efficace via la fonction `pow(base, exp, mod)`.

```
# Données du challenge
m = 29092715682136811148741896992216382887663205723233009270907036164616385404410946789697601633832261873953783070225717396137755866976801871184236363551686364362312702985660271388900637527644505521559662128091418418029535347788018938016105431888876506254626085450904980887492319714444847439547681555866496873380
n = 115835143529011985466946897371659768942707075251385995517214050122410566973563965811168663559614636580713282451012293945169200873869218782362296940822448735543079113463384249819134147369806470560382457164633045830912243978622870542174381898756721599280783431283777436949655777218920351233463535926738440504017
e = 65537

# Calcul de c = m^e mod n
c = pow(m, e, n)

print(f"Le flag est : FCSC{{{c}}}")
```
