---
# Imported from Obsidian: Cyberini/🚩 Writeup -- Crack py.md
title: Crack py
category: Reverse Engineering
ctf: Cyberini
date: 2026-08-07
summary: 'Le programme utilise deux fonctions : verifmdp et main.'
tags:
- code-reviews
- crackage
- cyberini
- reverse-engineering
lang: fr
imported: true
---

## Analyse du Code Source

```python
def verif_mdp(mdp):
    correct = ''.join([chr(x ^ 0x13) for x in [112, 106, 113, 32, 97]])
    correct += ''.join(chr(y ^ 0x13) for y in[39])
    
    if len(mdp) != len(correct)+1:
        print("Accès refusé.")
        return
    
    if mdp == correct + "2":
        print("Bravo, mot de passe correct !")
    else:
        print("Accès refusé.")

def main():
    user_input = input("Entrez le mot de passe : ")
    verif_mdp(user_input)

if __name__ == "__main__":
    main()
```

Le programme utilise deux fonctions : `verif_mdp` et `main`.
### Logique de chiffrement
La variable `correct` est construite dynamiquement :
1. Une liste d'entiers `[112, 106, 113, 32, 97]` subit un XOR avec la clé hexadécimale `0x13`.
2. L'entier `39` subit également un XOR avec `0x13`.
3. Le mot de passe final attendu est la concaténation de ce résultat et du caractère `"2"`.

**Vulnérabilité :** La clé XOR et les valeurs cibles sont codées en dur (Hardcoded). L'opération XOR étant réversible, on peut retrouver le clair en ré-appliquant la même clé.

## 🛠️ Exploitation (Script de décodage)
```python
def solve():
    # Valeurs extraites du code source
    encoded_vals = [112, 106, 113, 32, 97, 39]
    key = 0x13
    
    # Inversion du XOR
    decoded = "".join([chr(v ^ key) for v in encoded_vals])
    
    # Ajout du suffixe statique "2"
    password = decoded + "2"
    print(f"Mot de passe trouvé : {password}")

solve()
```

## 🚩 Flag / Résultat

**Mot de passe :** `cyb3r42`
**Validation :** "Bravo, mot de passe correct !"
