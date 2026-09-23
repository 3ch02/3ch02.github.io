---
# Imported from Obsidian: CTF/hackviser/EcowsCTF{}/📑 Writeup Challenge -Reversed Logic.md
title: Reversed Logic
category: Reverse Engineering
ctf: EcowsCTF (Hackviser)
date: 2026-08-07
summary: 'Le script encoder.py applique quatre étapes distinctes pour chiffrer le message :'
tags:
- ecowsctf
- reverse-engineering
lang: fr
imported: true
---

##### Données:

Le fichier encoder.py
```
#!/bin/env python3
from random import randint, seed
import sys

def modular_power(base, exp, mod):
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp = exp >> 1
        base = (base * base) % mod
    return result

def transform_char(char, key, salt):
    val = ord(char) + salt
    val = val * key
    val = val ^ (key & 0xFF)
    val = val * 47
    return val

def reverse_rotate(text, shift):
    if len(text) == 0:
        return text
    shift = shift % len(text)
    return text[-shift:] + text[:-shift]

def xor_layer(plaintext, key_phrase):
    result = ""
    key_len = len(key_phrase)
    
    for idx, char in enumerate(plaintext):
        key_char = key_phrase[idx % key_len]
        xor_val = ord(char) ^ ord(key_char)
        shifted = (xor_val + idx) % 256
        result += chr(shifted)
    
    return result

def validate_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

def encrypt_message(message, secret_phrase):
    P = 137
    G = 41
    
    if not validate_prime(P) or not validate_prime(G):
        print("error: Invalid parameters")
        return
    
    seed(1337)
    private_a = randint(P - 20, P - 5)
    private_b = randint(G - 15, G - 3)
    
    print(f"public_a = {private_a}")
    print(f"public_b = {private_b}")
    
    public_key_a = modular_power(G, private_a, P)
    public_key_b = modular_power(G, private_b, P)
    
    secret_a = modular_power(public_key_b, private_a, P)
    secret_b = modular_power(public_key_a, private_b, P)
    
    if secret_a != secret_b:
        print("Key exchange failed!")
        return
    
    master_key = secret_a
    rotated = reverse_rotate(message, 7)
    
    xor_encrypted = xor_layer(rotated, secret_phrase)
    

    salt_value = 42
    final_cipher = []
    
    for character in xor_encrypted:
        encrypted_val = transform_char(character, master_key, salt_value)
        final_cipher.append(encrypted_val)
    
    print(f"encrypted_data = {final_cipher}")
    return final_cipher

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 encoder.py <message>")
        sys.exit(1)
    
    payload = sys.argv[1]
    encrypt_message(payload, "ecowas")
```

**Données :**
```
public_a = 128 
public_b = 35 
encrypted_data = [5828, 2068, 6486, 3102, 6345, 3055, 3431, 4042, 2961, 3478, 3525, 3290, 3619, 4042, 5358, 5029, 3995, 3901, 6862, 2820, 4230, 6345, 3760, 3431, 6956, 3525, 5499, 4136, 4277, 3290, 4136, 7379, 3619, 5358, 7473, 5029, 3995, 4559, 4841, 4183, 7661, 4277, 7943, 7943, 4042, 5922, 4183, 7285, 4465]
```

#### Etape 1- Analyse du Code Source

Le script `encoder.py` applique quatre étapes distinctes pour chiffrer le message :

1. **Échange de clés (Diffie-Hellman)** : Utilise des paramètres P=137 et G=41 pour générer une `master_key` secrète.
    
2. **Rotation (`reverse_rotate`)** : Décale les caractères du message de 7 positions vers la droite.
    
3. **Couche XOR (`xor_layer`)** : Applique un XOR entre le message et une phrase secrète ("ecowas"), puis ajoute l'index de chaque caractère modulo 256.
    
4. **Transformation arithmétique (`transform_char`)** : Applique une série d'opérations (addition de sel, multiplication par la clé, XOR avec la clé, multiplication par 47).
    

#### Etape 2- Détermination de la Master Key

Bien que le script simule un échange de clés, il affiche les valeurs `private_a` et `private_b` sous les noms `public_a` et `public_b`.

- Données : `public_a = 128`, `public_b = 35`, P=137, G=41.
    
- La `master_key` est calculée par Ga×b(modP).
    
- Calcul : `pow(41, 128 * 35, 137)` donne **`master_key = 9`**.
    

#### Etape 3- Inversion des étapes (Exploitation)

Pour retrouver le flag, il faut appliquer les opérations inverses dans l'ordre strictement opposé :

###### Étape A : Inverser `transform_char`

La formule originale est : 
$$
val=((ord(char)+salt)×key⊕(key&0xFF))×47
$$
L'inverse est : 
$$
char=((val/47)⊕(key&0xFF))/key−salt
$$

###### Étape B : Inverser `xor_layer`

Le script faisait : 
$$
shifted=(xor_val+idx)(mod256) 
$$
L'inverse est : 
$$
xor_val=(shifted−idx)(mod256)
$$
Ensuite, on applique 
$$
char=xor_val⊕key_phrase[idx(modlen)]
$$

###### Étape C : Inverser la rotation

La rotation était de 7 vers la droite. Pour l'annuler, on effectue une rotation de 7 vers la **gauche**.

#### Etape 4. Script de Décodage

```python
def decrypt():
    public_a = 128
    public_b = 35
    encrypted_data = [5828, 2068, 6486, 3102, 6345, 3055, 3431, 4042, 2961, 3478, 3525, 3290, 3619, 4042, 5358, 5029, 3995, 3901, 6862, 2820, 4230, 6345, 3760, 3431, 6956, 3525, 5499, 4136, 4277, 3290, 4136, 7379, 3619, 5358, 7473, 5029, 3995, 4559, 4841, 4183, 7661, 4277, 7943, 7943, 4042, 5922, 4183, 7285, 4465]
    
    P, G, salt = 137, 41, 42
    key_phrase = "ecowas"

    # 1. Calcul de la master key
    master_key = pow(G, public_a * public_b, P)
    
    # 2. Inversion transformation arithmétique
    xor_layer_chars = []
    for val in encrypted_data:
        v = (val // 47) ^ (master_key & 0xFF)
        xor_layer_chars.append((v // master_key) - salt)

    # 3. Inversion XOR et Shift d'index
    rotated_chars = []
    for idx, val in enumerate(xor_layer_chars):
        xor_val = (val - idx) % 256
        key_char = ord(key_phrase[idx % len(key_phrase)])
        rotated_chars.append(xor_val ^ key_char)

    # 4. Inversion de la rotation (7 vers la gauche)
    n = len(rotated_chars)
    shift = 7 % n
    # On reprend la logique inverse de text[-7:] + text[:-7]
    flag_ints = rotated_chars[shift:] + rotated_chars[:shift]
    
    return "".join(chr(x) for x in flag_ints)

print(f"🚩 FLAG : {decrypt()}")
```

#### 🚩 FLAG

> **Success**
> **`EcowasCTF{d2cr0pt6d_cust0m_3ncryp1t10n_a2a6a0a9b}
`**
