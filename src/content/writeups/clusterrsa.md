---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/ClusterRSA.md
# Draft: incomplete: script given but final flag never shown
title: ClusterRSA
category: Cryptography
ctf: picoCTF 2026
date: 2026-08-07
tags:
- cryptography
- picoctf-2026
- rsa
lang: fr
draft: true
imported: true
---

Faille : 
calacule de 

sortie : 
```
n = 8749002899132047699790752490331099938058737706735201354674975134719667510377522805717156720453193651
e = 65537
ct = 3021569373773402689513257373362764131880473249842187164838297943840513930619586623604677697191914325

```

```
from Crypto.Util.number import inverse, long_to_bytes

# Données du challenge
n = 8749002899132047699790752490331099938058737706735201354674975134719667510377522805717156720453193651
e = 65537
ct = 3021569373773402689513257373362764131880473249842187164838297943840513930619586623604677697191914325

# Facteurs trouvés via factorisation
p = 9671406556917033397931773
q1 = 9671406556917033398314601
q2 = 9671406556917033398439721
q3 = 9671406556917033398454847

# Calcul de d
phi = (p - 1) * (q1 - 1) * (q2 -1) * (q3 - 1)
d = inverse(e, phi)

# Déchiffrement
m = pow(ct, d, n)
msg_bytes = long_to_bytes(m)

print(f"Bytes bruts : {msg_bytes}")
# Si tu vois 'pico' dans la console, tu as gagné !
try:
    print(f"Flag : {msg_bytes.decode('latin-1')}")
except:
    print("Impossible de décoder proprement, vérifie les bytes bruts.")

```

Flag ;
