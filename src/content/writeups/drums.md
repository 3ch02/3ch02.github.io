---
# Imported from Obsidian: CTF/hackviser/EcowsCTF{}/📑 Writeup Challenge -Drums.md
title: Drums
category: Cryptography
ctf: EcowsCTF (Hackviser)
date: 2026-08-07
summary: 'Le tambour parlant bat un message à travers le village : XvhptlVMY{v43l4kwknf5u34m0gv3} Les anciens disent que le rythme a été décalé (shifted) avant d''être envoyé. De combien de…'
tags:
- cesar
- cryptographie
- cryptography
- ecowasctf
- ecowsctf
lang: fr
imported: true
---

#### 📝 Description

Le tambour parlant bat un message à travers le village :  
`XvhptlVMY{v43l4k_wknf5_u34m_0gv3}`  
Les anciens disent que le rythme a été décalé (_shifted_) avant d'être envoyé. De combien de battements est-il décalé ?

---

#### Etape 1-  Analyse

Le message ressemble immédiatement au format standard des flags du CTF : `EcowasCTF{...}`.  
L'indice **"shifted"** (décalé) confirme qu'il s'agit d'un **Chiffre de César** (ou décalage alphabétique).

Identification du décalage

Pour trouver la clé, on compare le début du texte chiffré avec le préfixe connu du flag :

- **Texte chiffré :** `X v h p t l V M Y`
- **Texte clair :** `E c o w a s C T F`
Après la calcule de distance on remarque qu'il s'agit d'un décalage de 7

#### Etape 2- Résolution

Option 1 : CyberChef

1. Aller sur CyberChef.
2. Utiliser l'opération **ROT13**.
3. Régler le paramètre `Amount` sur **7**.
4. Insérer le texte : `XvhptlVMY{v43l4k_wknf5_u34m_0gv3}`.

Option 2 : Script Python

```python
# Décalage de César (ROT 7)
def decode_cesar(text, shift):
    decoded = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            decoded += chr((ord(char) - base + shift) % 26 + base)
        else:
            decoded += char
    return decoded

cipher = "XvhptlVMY{v43l4k_wknf5_u34m_0gv3}"
print(f"Flag : {decode_cesar(cipher, 7)}")
```

Use code with caution.

---

#### 🚩 Flag

> **Success**
> **`EcowasCTF{c43s4r_drums_b34t_0nt3}`**

**Tags :** CTF Cryptographie Cesar EcowasCTF
