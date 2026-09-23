---
# Imported from Obsidian: Cyberini/🚩 Writeup  -- Crackme.md
title: Crackme
category: Reverse Engineering
ctf: Cyberini
date: 2026-08-07
summary: 'Vulnérabilités Identifiées 1. Hardcoded Credentials (CWE-259) : Le mot de passe (secret) est stocké directement en clair/obfusqué dans le code source (plorevav{synt}). 2…'
tags:
- cyberini
- reverse-engineering
lang: fr
imported: true
---

##  1. Code Source Fourni

```python
# "le code secret est caché, personne ne peut le déchiffrer"
code_secret = "plorevav{synt}"

# Correspondance de référence pour le codage/décodage (ROT13)
alphabet = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                         'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm')

def decode_secret(secret):
    # Fonction de décodage ROT13
    return secret.translate(alphabet)

def login():
    # Fonction de connexion au programme
    nom = input("Nom d'utilisateur : ")
    mdp = input("Mot de passe : ")

    if nom == "Michel":
        if mdp == decode_secret(code_secret):
            print("Connecté avec succès !")
        else:
            print("Mot de passe invalide.")
    else:
        print("Nom d'utilisateur invalide.")

login()
```

---

## ⚠️ 2. Analyse des Vulnérabilités

> **Vulnérabilités Identifiées**
> 1. **Hardcoded Credentials (CWE-259) :** Le mot de passe (secret) est stocké directement en clair/obfusqué dans le code source (`plorevav{synt}`).
> 2. **Obfuscation vs Chiffrement (CWE-327) :** L'application utilise le **ROT13**, un simple algorithme de substitution symétrique et réversible sans clé secrète. Ce n'est pas un mécanisme de hachage sécurisé.

---

## 🛠️ 3. Méthodes d'Exploitation

### Méthode 1 : Analyse Statique (Offline via CyberChef / Terminal)
Puisque le secret est présent dans le code, il suffit de le passer dans un décodeur ROT13 :

1. Extraire la chaîne : `plorevav{synt}`
2. Appliquer une rotation de 13 caractères (ROT13) :
   - `plorevav` $\rightarrow$ `cyberini`
   - `synt` $\rightarrow$ `flag`
3. **Résultat :** `cyberini{flag}`

### Méthode 2 : Exécution Dynamique Modifiée
On modifie légèrement le script Python localement pour lui faire afficher la valeur décodée avant la phase de connexion.

```python
# Ajout de l'affichage du mot de passe décodé
print("[+] Mot de passe extrait :", decode_secret(code_secret))

# Identifiants de connexion valides :
# Nom d'utilisateur : Michel
# Mot de passe : cyberini{flag}
```

---

## 4. Recommandations de Sécurité (Remediation)

> **Bonnes Pratiques**
> - **Ne jamais stocker de secrets dans le code source.**
> - **Hachage des mots de passe :** Remplacer le stockage de mots de passe déchiffrables par un hachage fort avec sel (*salt*) utilisant des algorithmes dédiés comme **bcrypt**, **Argon2**, ou **PBKDF2**.
> - **Variables d'environnement :** Utiliser des coffres-forts de clés (*Key Vaults*) ou des variables d'environnement si un secret doit être géré par l'application.
