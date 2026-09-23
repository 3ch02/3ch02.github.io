---
# Imported from Obsidian: CTF/Writeup CTF Hackropole/Crypto/🚩 Hamac.md
title: Hamac
category: Cryptography
ctf: Hackropole (FCSC)
date: 2026-08-07
summary: 'Le programme demande un mot de passe à l''utilisateur, puis :'
tags:
- cryptography
- hackropole
- hmac
lang: fr
imported: true
---

Code source :
```
# python3 -m pip install pycryptodome

import json

from Crypto.Cipher import AES

from Crypto.Util.Padding import pad

from Crypto.Hash import HMAC, SHA256

from Crypto.Random import get_random_bytes
print("Enter your password")

password = input(">>> ").encode()

h = HMAC.new(password, digestmod = SHA256)

h.update(b"FCSC2022")
iv = get_random_bytes(16)

k  = SHA256.new(password).digest()

c  = AES.new(k, AES.MODE_CBC, iv = iv).encrypt(pad(open("flag.txt", "rb").read(), 16))

r = {

    "iv": iv.hex(),

    "c": c.hex(),

    "h": h.hexdigest(),

}

open("output.txt", "w").write(json.dumps(r))
```

Sortie : 

```
{"iv": "ea425b2ea4bb67445abe967e3bd1b583", "c": "69771c85e2362a35eb0157497e9e2d17858bf11492e003c4aa8ce1b76d8d3a31ccc3412ec6e619e7996190d8693299fc3873e1e6a96bcc1fe67abdf5175c753c09128fd1eb2f2f15bd07b12c5bfc2933", "h": "951bd9d2caae0d9e9a5665b4fc112809aac9f5f9ecbcfc5ad8e23cb1d020201d"}
```

### 1. Description du Challenge

Le programme demande un mot de passe à l'utilisateur, puis :

1. Il calcule un **HMAC** (une sorte de signature) basé sur ce mot de passe et la chaîne `"FCSC2022"`.
    
2. Il utilise ce même mot de passe pour générer une clé **AES-256** (via `SHA256.new(password)`).
    
3. Il chiffre le flag avec cette clé en mode **CBC**.
    

**La faille :** Si le mot de passe est un mot courant (dictionnaire) ou un code court, nous pouvons essayer des milliers de mots de passe, calculer le HMAC pour chacun, et le comparer avec celui de la sortie (`951bd9...`). Si les HMAC correspondent, on a trouvé le mot de passe, et donc la clé AES.

---

### 2. Notions de Base

#### A. HMAC (Hash-based Message Authentication Code)

C'est un mécanisme qui permet de vérifier l'intégrité et l'authenticité d'un message.

- Il utilise une **clé** (ici le `password`) et un **message** (ici `FCSC2022`).
    
- Sa propriété intéressante ici : **On ne peut pas inverser le HMAC** pour retrouver le mot de passe, mais on peut vérifier si un mot de passe est le bon en recalculant le HMAC.
    

#### B. AES-CBC (Cipher Block Chaining)

C'est un mode de chiffrement par blocs où chaque bloc dépend du précédent.

- **IV (Vecteur d'Initialisation) :** Il est nécessaire pour déchiffrer le tout premier bloc. Il est fourni en clair dans ton JSON (`ea425b...`).
    
- **La Clé :** Elle est dérivée du mot de passe via un hash SHA256.
    

---

### 3. Résolution (Le Plan)

Puisque c'est un challenge FCSC, le mot de passe est probablement dans une liste de mots courants (un "wordlist" comme `rockyou.txt`).

**le script de résolution doit :**

1. Charger le fichier de mots de passe.
    
2. Pour chaque mot :
    
    - Calculer le HMAC avec le sel `FCSC2022`.
        
    - Comparer avec le `h` fourni. Si le hmac calculé est identique au h fourni ce qui signifie qu'on a le Password e qu'on peut déchiffré le message
        
3. Une fois le mot de passe trouvé :
    
    - Recréer la clé AES.
        
    - Déchiffrer le message `c` avec l'IV fourni.
        

---

### 4. Le Script de Brute-force

```
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Hash import HMAC, SHA256

# Données extraites de l'output.txt
iv = bytes.fromhex("ea425b2ea4bb67445abe967e3bd1b583")
c = bytes.fromhex("69771c85e2362a35eb0157497e9e2d17858bf11492e003c4aa8ce1b76d8d3a31ccc3412ec6e619e7996190d8693299fc3873e1e6a96bcc1fe67abdf5175c753c09128fd1eb2f2f15bd07b12c5bfc2933")
target_h = "951bd9d2caae0d9e9a5665b4fc112809aac9f5f9ecbcfc5ad8e23cb1d020201d"

# Chemin vers rockyou
wordlist_path = "/usr/share/wordlists/rockyou.txt"

print("[*] Lancement du brute-force avec Rockyou...")

try:
    # On ouvre en 'rb' (read binary) car rockyou contient des caractères non-utf8
    with open(wordlist_path, "rb") as f:
        for line in f:
            # On enlève le retour à la ligne (\n ou \r\n)
            password = line.strip()
            
            # 1. Test du HMAC (beaucoup plus rapide que de tenter le déchiffrement AES directement)
            h = HMAC.new(password, digestmod=SHA256)
            h.update(b"FCSC2022")
            
            if h.hexdigest() == target_h:
                print(f"\n[+] MOT DE PASSE TROUVÉ : {password.decode(errors='ignore')}")
                
                # 2. Une fois trouvé, on déchiffre le flag
                k = SHA256.new(password).digest()
                cipher = AES.new(k, AES.MODE_CBC, iv=iv)
                try:
                    decrypted = cipher.decrypt(c)
                    flag = unpad(decrypted, 16)
                    print(f"[!] FLAG : {flag.decode()}")
                except Exception as e:
                    print(f"[-] Erreur au déchiffrement : {e}")
                
                exit() # On arrête tout
except FileNotFoundError:
    print(f"[-] Erreur : Le fichier {wordlist_path} est introuvable.")
```

Mot de passe : 
```
omgh4xx0r
```

### Flag 🚩:

```
FCSC{5bb0780f8af31f69b4eccf18870f493628f135045add3036f35a4e3a423976d6}
```
