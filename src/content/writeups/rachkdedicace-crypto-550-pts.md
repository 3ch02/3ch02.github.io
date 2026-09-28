---
# Imported from Obsidian: CTF/ESIG Tech Arena CTF/RachkDedicace — Writeup (Crypto, 550 pts).md
title: RachkDedicace — (Crypto, 550 pts)
category: Cryptography
ctf: ESIG Tech Arena 2026
competition: esig-tech-arena-2026
date: 2026-09-25
summary: 'app.py (Flask + cryptography) expose un service CipherVault :'
tags:
- aes-cbc
- crypto
- cryptography
- esig-tech-arena
- esig-tech-arena-2026
- padding-oracle
- vaudenay
points: 550
lang: fr
imported: true
---

### 📌 Description
> **RachkDedicace** (Crypto · insane). "Un document confidentiel a été chiffré en AES-128-CBC (padding PKCS#7) sous une clé que seul le serveur connaît. Le serveur accepte de vérifier, pour n'importe quel jeton, si le padding déchiffré est correct… et rien d'autre. Ça devrait suffire. Retrouve le contenu du document." Fichiers fournis : `RachkDedicace.zip` (`app.py`, `Dockerfile`, `requirements.txt`).
>
> **Author** : Daniel-tout-court-sans-caractère-alpha-numérique
**Points** : 550 pts
**First blood** : Lazarus_hack
**Statut** : ✓ Résolu

---
### Étape 1 : Reconnaissance du code source

`app.py` (Flask + `cryptography`) expose un service **CipherVault** :

- Au démarrage, le serveur génère un IV aléatoire et chiffre `FLAG` en AES-128-CBC/PKCS#7 sous une clé secrète (`KEY`, jamais exposée) → `TOKEN = IV || CT`.
- `GET /token` renvoie ce jeton cible en hex.
- `POST /verify` prend n'importe quel jeton `{"token": "<hex>"}`, le déchiffre avec la clé secrète, et répond **uniquement** `{"padding":"ok"}` ou `{"padding":"bad"}` selon la validité du padding PKCS#7 — sans jamais révéler le texte clair.

```python
def pkcs7_unpad_valid(data: bytes) -> bool:
    if not data or len(data) % BS != 0:
        return False
    n = data[-1]
    if n < 1 or n > BS:
        return False
    return data[-n:] == bytes([n]) * n
```

C'est l'archétype de l'**oracle de padding CBC** (attaque de Vaudenay, 2002) : ce simple bit d'information ("padding valide ou non") suffit à déchiffrer **tout** le ciphertext, sans jamais connaître la clé.

> **Le commentaire du serveur**
> Le code précise explicitement : *"impossible à résoudre en collant les fichiers dans une IA : il faut attaquer l'oracle live."* — confirmation que la seule voie est l'attaque adaptative réelle contre `/verify`, à coups de milliers de requêtes.

---
### Étape 2 : Rappel du principe de l'attaque

Pour un bloc de ciphertext `C_i` et le bloc précédent `C_{i-1}` (ou l'IV pour le premier bloc) :

$$P_i = D_K(C_i) \oplus C_{i-1}$$

L'oracle ne nous laisse contrôler que `C_{i-1}` (on peut le remplacer par un IV/bloc forgé arbitraire) sans jamais connaître `D_K(C_i)` directement. En forçant un padding valide connu (`0x01`, puis `0x02 0x02`, etc.) en faisant varier byte par byte le bloc précédent forgé, on retrouve `D_K(C_i)` octet par octet en partant de la fin du bloc :

1. Pour le dernier octet (`pos = 15`) : on teste les 256 valeurs possibles de `IV_forgé[15]` jusqu'à obtenir `padding: ok` → cela révèle `intermediate[15] = guess ⊕ 0x01`.
2. On fixe alors les octets déjà connus pour produire un padding `0x02 0x02` sur les 2 derniers octets, et on brute-force `IV_forgé[14]` → révèle `intermediate[14]`.
3. On répète jusqu'au premier octet du bloc (padding `0x10 × 16`).
4. Le texte clair du bloc est enfin : `P_i = intermediate ⊕ C_{i-1}`.

> **Faux positif sur le dernier octet**
> Quand on cherche l'octet de padding `0x01`, un faux positif est possible si les 2 derniers octets du clair forment déjà un padding valide différent (`0x02 0x02`). Pour l'éviter, dès qu'un candidat matche pour `pos=15`, on flippe l'avant-dernier octet du bloc forgé et on re-teste : un vrai `0x01` reste valide, un faux positif `0x02 0x02` devient invalide.

---
### Étape 3 : Implémentation de l'attaque

```python
import requests

BASE = "http://<host>:<port>"   # instance CipherVault ciblée
BS = 16
session = requests.Session()

def verify(iv: bytes, ct: bytes) -> bool:
    token = (iv + ct).hex()
    r = session.post(BASE + "/verify", json={"token": token}, timeout=10)
    return r.json().get("padding") == "ok"

def get_token():
    raw = bytes.fromhex(session.get(BASE + "/token").text.strip())
    return raw[:BS], raw[BS:]

def decrypt_block(prev_block: bytes, block: bytes) -> bytes:
    intermediate = bytearray(BS)
    for pad_val in range(1, BS + 1):
        pos = BS - pad_val
        for guess in range(256):
            iv = bytearray(BS)
            for i in range(pos + 1, BS):
                iv[i] = intermediate[i] ^ pad_val
            iv[pos] = guess
            if verify(bytes(iv), block):
                if pad_val == 1:
                    iv2 = bytearray(iv); iv2[pos - 1] ^= 0xFF
                    if not verify(bytes(iv2), block):
                        continue  # faux positif
                intermediate[pos] = guess ^ pad_val
                break
    return bytes(intermediate[i] ^ prev_block[i] for i in range(BS))

iv, ct = get_token()
blocks = [ct[i:i+BS] for i in range(0, len(ct), BS)]
prevs = [iv] + blocks[:-1]
plaintext = b"".join(decrypt_block(p, b) for p, b in zip(prevs, blocks))
flag = plaintext[:-plaintext[-1]]   # retrait du padding PKCS#7
print(flag)
```

**Résultat** (4 blocs de 16 octets, ~4096 requêtes max, ~90 s avec 1 worker / 16 threads gunicorn) :

```
block 0: b'EthACTF{p4dd1ng_'
block 1: b'0r4cl3_l1v3_n0_c'
block 2: b'h4tb0t_c4n_sk1p_'
block 3: b'th3_qu3r13s}\x04\x04\x04\x04'
```

> **Aucun brute-force sur le flag**
> Chaque octet du texte clair est retrouvé un par un via l'oracle de padding réel (`/verify`), jamais deviné — conformément à la contrainte de l'énoncé.

---
### 🏁 Flag

```
EthACTF{p4dd1ng_0r4cl3_l1v3_n0_ch4tb0t_c4n_sk1p_th3_qu3r13s}
```
