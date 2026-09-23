---
# Imported from Obsidian: Cyberini/🚩 Writeup - Crack MD5.md
title: Crack MD5
category: Cryptography
ctf: Cyberini
date: 2026-08-07
summary: 'Le script Python demande une saisie utilisateur et la compare après conversion en hash MD5 :'
tags:
- cryptography
- cyberini
lang: fr
imported: true
---

## 📌 Aperçu du Challenge
- **Nom :** Crack MD5 (CrackMe Cyberini)
- **Objectif :** Retrouver le mot de passe en clair à partir de son empreinte MD5 stockée dans le script Python.
- **Empreinte (Hash) :** `0391ed24d616c90972f4ab4fea4d4a67`
- **Flag / Mot de passe :** `cyberini`

---

## 🔍 Step 1 : Analyse du Code Source

Le script Python demande une saisie utilisateur et la compare après conversion en hash MD5 :

```python
import hashlib

# Empreinte (hash) du mot de passe attendu
MDP = "0391ed24d616c90972f4ab4fea4d4a67"

def check(password):
    # Hachage de la saisie utilisateur en MD5
    digest = hashlib.md5(password.encode()).hexdigest()
    return digest == MDP
````

> **Constat**
> 
> Le programme utilise l'algorithme **MD5** sans grain de sel (_salt_). MD5 étant un algorithme de hachage à sens unique mais non résistant aux attaques par dictionnaire et aux tables arc-en-ciel (_rainbow tables_), il est possible de retrouver le mot de passe s'il s'agit d'un mot courant.

##  Step 2 : Cassage du Hash (Lookup Table)

### Essai 1 : CrackStation

L'utilisation de _CrackStation_ n'a pas retourné de résultat pour ce hash spécifique.

### Essai 2 : MD5decrypt

Une recherche sur l'outil en ligne _MD5decrypt_ a permis de retrouver la correspondance dans leur base de données :

**Réponse JSON reçue :**

```json
{
  "success": true,
  "action": "decrypt",
  "algorithm": "md5",
  "results": [
    {
      "hash": "0391ed24d616c90972f4ab4fea4d4a67",
      "status": "found",
      "algorithm": "md5",
      "plaintext": "cyberini"
    }
  ],
  "found_count": 1
}
```

> **Résultat**
> 
> Le texte en clair correspondant au hash `0391ed24d616c90972f4ab4fea4d4a67` est **`cyberini`**.

## Step 3 : Validation

L'exécution du script Python avec la valeur `cyberini` valide l'accès :

```text
========================================
   CrackMe Cyberini - Niveau Facile
========================================
Entrez le mot de passe secret.

Mot de passe > cyberini

[+] Bravo ! Mot de passe correct, il s'agit du flag à donner.
```

## 🔒 Notion Clé

> **A retenir**
> 
> - **Obsolescence de MD5 :** MD5 ne doit plus être utilisé pour le stockage de mots de passe. Il est vulnérable aux collisions et les tables de pré-calcul (_rainbow tables_) permettent de retrouver instantanément les mots de passe simples.
>     
> - **Protection :** Pour stocker des mots de passe en toute sécurité, il faut utiliser des fonctions de hachage lentes conçues à cet effet comme **bcrypt**, **Argon2** ou **PBKDF2**, combinées à un sel unique (_salt_) pour empêcher les attaques par dictionnaire global.
