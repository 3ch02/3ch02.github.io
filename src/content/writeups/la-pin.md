---
# Imported from Obsidian: CTF/Writeup CTF Hackropole/Crypto/🚩 La PIN.md
title: La PIN
category: Cryptography
ctf: Hackropole (FCSC)
date: 2026-08-07
summary: Le programme utilise scrypt, qui est une fonction de dérivation de clé (KDF) conçue pour être lente et gourmande en mémoire afin de décourager le brute-force.
tags:
- aes-gcm
- cryptography
- hackropole
- scrypt
lang: fr
imported: true
---

#### Code source 

```
from Crypto.Cipher import AES

from Crypto.Protocol.KDF import scrypt

from Crypto.Util.number import long_to_bytes  

while True:

    pin = int(input(">>> PIN code (4 digits): "))

    if 0 < pin < 9999:

        break
        
flag = open("flag.txt", "rb").read()
k = scrypt(long_to_bytes(pin), b"FCSC", 32, N = 2 ** 10, r = 8, p = 1)

aes = AES.new(k, AES.MODE_GCM)

c, tag = aes.encrypt_and_digest(flag)

enc = aes.nonce + c + tag

print(enc.hex())
```

#### Output 

```
f049de59cbdc9189170787b20b24f7426ccb9515e8b0250f3fc0f0c14ed7bb1d4b42c09d02fe01e0973a7233d99af55ce696f599050142759adc26796d64e0d6035f2fc39d2edb8a0797a9e45ae4cd55074cf99158d3a64dc70a7e836e3b30382df30de49ba60a

```
### 1. Description du Challenge

Le programme utilise **scrypt**, qui est une fonction de dérivation de clé (KDF) conçue pour être lente et gourmande en mémoire afin de décourager le brute-force.

- **L'obstacle :** `scrypt` ralentit chaque tentative.
    
- **La faille :** 10 000 tentatives, même avec un algorithme lent comme `scrypt`, cela prend moins d'une minute sur un ordinateur moderne.
    
- **AES-GCM :** Contrairement aux modes précédents (CBC ou ECB), le mode GCM fournit un **tag** d'authentification. C'est génial pour nous : si on tente de déchiffrer avec le mauvais PIN, l'AES nous dira "Erreur de tag". Si le tag est valide, on a trouvé le flag !
    

---

### 2. Notions de Base

#### A. scrypt (KDF)

C'est une fonction qui transforme un mot de passe simple (le PIN) en une clé robuste de 32 octets.

- **N (Cost factor) :** Ici 210=1024. C'est le paramètre qui définit l'effort CPU/Mémoire.
    
- **Salt :** "FCSC". Il empêche l'utilisation de tables pré-calculées (Rainbow Tables).
    

#### B. La structure de `enc`

Le code source nous dit comment est construit le message chiffré : `enc = nonce + c + tag`.

- **Nonce (16 octets par défaut) :** Sert à garantir que le même flag chiffré deux fois donne un résultat différent.
    
- **C (Ciphertext) :** Le flag chiffré.
    
- **Tag (16 octets par défaut) :** La signature qui prouve que la clé est la bonne.
    

---

### 3. Résolution (Le Script de Brute-force)

On va boucler de 0 à 9999, générer la clé avec `scrypt` pour chaque PIN, et tenter d'ouvrir le "coffre-fort" AES-GCM.

```
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Util.number import long_to_bytes

# Données de sortie
enc_hex = "f049de59cbdc9189170787b20b24f7426ccb9515e8b0250f3fc0f0c14ed7bb1d4b42c09d02fe01e0973a7233d99af55ce696f599050142759adc26796d64e0d6035f2fc39d2edb8a0797a9e45ae4cd55074cf99158d3a64dc70a7e836e3b30382df30de49ba60a"
enc = bytes.fromhex(enc_hex)

# On découpe enc selon la structure : nonce (16) + ciphertext (?) + tag (16)
nonce = enc[:16]
tag = enc[-16:]
ciphertext = enc[16:-16]

print("[*] Brute-force du PIN (0000-9999)...")

for pin in range(10000):
    # 1. On dérive la clé exactement comme dans le code source
    k = scrypt(long_to_bytes(pin), b"FCSC", 32, N = 2 ** 10, r = 8, p = 1)
    
    # 2. On tente de déchiffrer
    try:
        aes = AES.new(k, AES.MODE_GCM, nonce=nonce)
        # decrypt_and_verify lève une exception si le tag ne correspond pas
        flag = aes.decrypt_and_verify(ciphertext, tag)
        
        print(f"\n[+] PIN trouvé : {pin:04d}")
        print(f"[!] FLAG : {flag.decode()}")
        break
    except ValueError:
        # Si le tag est invalide, on passe au PIN suivant
        continue
    
    if pin % 500 == 0:
        print(f"Tentative en cours : {pin}...")
```

##### PIN trouvée : 
```
6273
```

### Flag 🚩:

```
FCSC{c1feab88e6c6932c57fbaf0c1ff6c32e51f07ae87197fcd08956be4408b2c802}
```
