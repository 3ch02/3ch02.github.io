---
# Imported from Obsidian: CTF/Writeup -- Timestamped Secrets.md
title: Timestamped Secrets
category: Cryptography
difficulty: Medium
ctf: picoCTF 2026
date: 2026-08-18
summary: Someone encrypted a message using AES in ECB mode but they weren't very careful with their key. Turns out it's derived from something as simple as the current time! Can you…
tags:
- aes
- brute-force
- crypto
- cryptography
- ecb
- picoctf
- picoctf-2026
- timestamp
lang: fr
imported: true
---

> **Catégorie : Cryptography — Medium**
> AES-128-ECB avec une clé dérivée d'un timestamp Unix prévisible, réduisant l'espace de clés à un intervalle de temps restreint et bruteforçable.

## Résumé

| Champ | Valeur |
|---|---|
| **Type** | Faiblesse de dérivation de clé — clé à faible entropie (timestamp prévisible) |
| **Challenge** | Timestamped Secrets |
| **Plateforme** | picoCTF 2026 |
| **Difficulté** | Medium |
| **Algorithme** | AES-128, mode ECB |
| **Flag** | `picoCTF{sa3S_sEc9t_91609b3c}` |

---

## Énoncé

> Someone encrypted a message using AES in ECB mode but they weren't very careful with their key. Turns out it's derived from something as simple as the current time! Can you uncover the key and decrypt the flag?

L'énoncé donne la faille directement : la clé est dérivée du **temps courant**, une source de données loin d'être secrète ou aléatoire.

---

## Fichiers fournis

### `encryption.py` (script redacté)

```python
from hashlib import sha256
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def encrypt(plaintext: str, timestamp: int) -> str:
    timestamp = int(time.time())
    key = sha256(str(timestamp).encode()).digest()[:16]
    cipher = AES.new(key, AES.MODE_ECB)
    padded = pad(plaintext.encode(), AES.block_size)
    ciphertext = cipher.encrypt(padded)
    return ciphertext.hex()

if __name__ == "__main__":
    plaintext = "picoCTF{...}"
    result = encrypt(plaintext, key)
    print(f"Hint: The encryption was done around {timestamp} UTC\n")
    print(f"Ciphertext (hex): {ciphertext.hex()}\n")
```

### `message.txt`

```
Hint: The encryption was done around 1770242610 UTC

Ciphertext (hex): 71cd3848348a45b82789f710c3321aceab2171e004200b57fe9cc64d4ea33cec
```

---

## Root cause

La clé AES-128 utilisée pour le chiffrement n'est **pas générée aléatoirement**, mais dérivée directement du timestamp Unix courant au moment du chiffrement :

```python
timestamp = int(time.time())
key = sha256(str(timestamp).encode()).digest()[:16]
```

> **Faiblesse fondamentale**
> `time.time()` retourne le nombre de secondes écoulées depuis epoch (1er janvier 1970) — une valeur **entière, séquentielle et publique**, pas un secret cryptographique. Même si `sha256` est un hash cryptographiquement solide, appliquer une fonction de hash à une entrée à **faible entropie et prévisible** ne produit pas une sortie sécurisée : l'espace de clés réel n'est plus 2¹²⁸ (AES-128 complet), mais se réduit au nombre de valeurs de timestamp plausibles — potentiellement quelques milliers seulement si on connaît une fenraie temporelle approximative.

Le hint fourni dans `message.txt` ("encrypted around 1770242610 UTC") réduit encore davantage cet espace de recherche à une fenêtre de quelques minutes/heures autour de cette valeur, rendant une attaque par force brute triviale.

---

## Exploitation (PoC)

### Étape 1 — Identifier la stratégie d'attaque

Puisque la clé dépend uniquement d'un timestamp connu à quelques milliers de secondes près, il suffit de :
1. Régénérer la clé pour chaque timestamp candidat dans une fenêtre raisonnable autour du hint
2. Tenter un déchiffrement AES-ECB avec chaque clé candidate
3. Détecter la bonne clé via un **oracle de validité structurel** : le padding PKCS#7

### Étape 2 — Script de résolution

```python
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Données fournies par le challenge
target_ciphertext = bytes.fromhex("71cd3848348a45b82789f710c3321aceab2171e004200b57fe9cc64d4ea33cec")
hint_timestamp = 1770242610

# Fenêtre de recherche : 1 heure avant et après l'indice
window = 3600

print("[*] Début de la force brute...")

for ts in range(hint_timestamp - window, hint_timestamp + window):
    # Réplication exacte de la génération de clé du script original
    key = sha256(str(ts).encode()).digest()[:16]

    try:
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted_padded = cipher.decrypt(target_ciphertext)

        # Le retrait du padding échoue presque systématiquement avec une mauvaise clé
        decrypted = unpad(decrypted_padded, AES.block_size)

        if b"picoCTF{" in decrypted:
            print(f"\n[+] Flag trouvé !")
            print(f"[+] Timestamp exact : {ts}")
            print(f"[+] Message : {decrypted.decode()}")
            break

    except (ValueError, KeyError):
        # Padding invalide = mauvaise clé, on continue
        continue
else:
    print("\n[-] Flag non trouvé. Essayez d'élargir la fenêtre de recherche.")
```

### Étape 3 — Exécution

```bash
python solve.py
```
```
[*] Début de la force brute...

[+] Flag trouvé !
[+] Timestamp exact : 1770242610
[+] Message : picoCTF{sa3S_sEc9t_91609b3c}
```

> **Flag obtenu**
> `picoCTF{sa3S_sEc9t_91609b3c}`
>
> Timestamp exact retrouvé : `1770242610` — correspondant exactement à la valeur donnée en hint, confirmant que la fenêtre de recherche n'avait même pas besoin d'être élargie.

---

## Analyse technique

### Pourquoi `unpad()` fonctionne comme détecteur de succès

En mode **ECB**, déchiffrer un ciphertext avec une clé incorrecte produit un résultat qui a l'apparence de données **binaires aléatoires**. Le padding **PKCS#7**, utilisé pour compléter le plaintext à un multiple de la taille de bloc AES (16 octets), a une structure précise : les derniers `N` octets doivent tous avoir la valeur `N`.

Sur un bloc déchiffré avec une clé incorrecte (donc essentiellement aléatoire), la probabilité que les derniers octets respectent cette structure par pur hasard est extrêmement faible (de l'ordre de 1/256 à 1/256^N selon la valeur de padding testée). `unpad()` lève donc une exception `ValueError` dans la quasi-totalité des cas où la clé est fausse, ce qui permet d'utiliser son succès/échec comme un **oracle binaire fiable** : "cette clé est-elle la bonne ?" sans même avoir besoin de connaître à l'avance le contenu attendu du message déchiffré.

C'est une technique de détection très générale en cryptanalyse par force brute : exploiter une **propriété structurelle attendue** du plaintext (ici le padding, mais ça pourrait être un format de fichier connu, un header magique, ou simplement du texte ASCII imprimable) comme critère de validation automatique.

### La leçon cryptographique généralisable

> **Principe clé**
> La robustesse d'un système cryptographique ne dépend pas uniquement de la solidité de l'algorithme utilisé (AES-128 est, en soi, considéré comme sûr), mais de la **qualité et de l'entropie de la clé**. Une clé dérivée d'une source prévisible — timestamp, mot de passe faible, seed non cryptographique, compteur incrémental — réduit l'espace de recherche effectif bien en-deçà de la taille théorique de la clé, rendant l'algorithme sous-jacent inefficace quelle que soit sa robustesse intrinsèque.

En pratique, une génération de clé sécurisée doit s'appuyer sur une source d'aléa cryptographique (ex: `secrets.token_bytes()` en Python, `/dev/urandom` sous Unix), jamais sur une valeur devinable ou reconstructible par un observateur externe.

---

## Enseignements méthodologiques (pour la compet')

- [x] Sur un challenge crypto qui fournit le **script de chiffrement**, toujours l'examiner en premier pour repérer comment la clé est dérivée — c'est souvent là que se situe la faille, pas dans l'algorithme lui-même
- [x] `time.time()` (ou tout timestamp Unix) est une source d'entropie **quasi nulle** en tant que clé cryptographique dès lors qu'un ordre de grandeur du moment de chiffrement est connu ou déductible
- [x] Utiliser une propriété structurelle du plaintext attendu (padding, header, format connu) comme oracle de validation permet d'automatiser la détection de succès dans une attaque par force brute, sans connaître le contenu exact à l'avance
- [x] Toujours élargir progressivvement la fenêtre de recherche si le premier essai échoue (le script prévoit cette possibilité via le message `"[-] Flag non trouvé. Essayez d'élargir la fenêtre de recherche."`)
- [x] Le mode **ECB** ne doit jamais être utilisé en production (il expose des patterns identiques pour des blocs de plaintext identiques), mais dans ce challenge il ne s'agit pas de la vulnérabilité principale exploitée — c'est bien la dérivation de clé qui est en cause

## Commandes clés à retenir

```bash
pip install pycryptodome --break-system-packages   # fournit le module Crypto (PyCryptodome)
python solve.py
```

```python
# Squelette réutilisable pour ce type d'attaque (clé dérivée d'un timestamp)
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

for ts in range(hint - window, hint + window):
    key = sha256(str(ts).encode()).digest()[:16]
    try:
        pt = unpad(AES.new(key, AES.MODE_ECB).decrypt(ciphertext), AES.block_size)
        if b"flag_prefix{" in pt:
            print(ts, pt)
            break
    except (ValueError, KeyError):
        continue
```
