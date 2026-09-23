---
# Imported from Obsidian: Cyberini/Writeup - Crack Me Basique.md
title: Crack Me Basique
category: Reverse Engineering
ctf: Cyberini
date: 2026-08-07
summary: 'L''extension .exe peut être trompeuse. On utilise la commande file pour déterminer la vraie nature du fichier :'
tags:
- cyberini
- reverse-engineering
lang: fr
imported: true
---

##  Aperçu du Challenge
- **Nom :** Crack Me Basique
- **Description :** Retrouver le mot de passe du binaire exécutable.
- **Indice :** `/stɹɪŋ/` (commande `strings`) ou `\de.bœ.ɡe\` (déboguer).
- **Flag / Mot de passe :** `08042023`

---

## Step 1 : Identification du Fichier

L'extension `.exe` peut être trompeuse. On utilise la commande `file` pour déterminer la vraie nature du fichier :

```bash
file crackme-linux.exe
````

**Résultat :**

`crackme-linux.exe: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked... not stripped`

> **Observation**
> 
> Le fichier est un exécutable binaire **ELF 64-bit pour Linux** (et non un exécutable Windows malgré l'extension `.exe`). Il n'est pas strippé (_not stripped_), ce qui signifie que les symboles d'en-tête sont conservés.

## 🛠️ Step 2 : Analyse Statique (`strings`)

Conformément à l'indice `/stɹɪŋ/`, on inspecte les chaînes de caractères imprimables contenues dans le binaire à l'aide de la commande `strings` :

```bash
strings crackme-linux.exe
```

**Extrait pertinent des résultats :**

```text
_ITM_registerTMCloneTable
PTE1
u+UH
-*- Cyberini CrackMe -*-
Password:
08042023
Nope!
;*3$"
GCC: (Debian 11.3.0-5) 11.3.0
```

> **Analyse**
> 
> On repère clairement la logique du programme :
> 
> - Affichage du prompt : `-*- Cyberini CrackMe -*-` / `Password:`
>     
> - Comparaison avec la chaîne : `08042023`
>     
> - Message d'échec : `Nope!`
>     
> 
> Le mot de passe attendu est donc **`08042023`**.

## Step 3 : Exploitation & Validation

### Méthode 1 : Exécution Directe en Ligne de Commande

1. Rendre le fichier exécutable :
    
    ```bash
    chmod +x crackme-linux.exe
    ```
    
2. Exécuter le programme et saisir le mot de passe trouvé :
    
    ```bash
    ./crackme-linux.exe
    ```
    

### Méthode 2 : Automatisation avec `pwntools` (Python)

Il est également possible d'interagir dynamiquement avec le binaire via un script Python utilisant la librairie `pwntools` :

```python
from pwn import *

# Lancement du processus local
p = process("./crackme-linux.exe")

# Attente du prompt "Password:" et envoi du mot de passe
p.recvuntil(b"Password:")
p.sendline(b"08042023")

# Passage en mode interactif pour lire la réponse
p.interactive()
```

## 🔒 Notion Clé

> **A retenir**
> 
> Ne jamais faire confiance aux extensions de fichier (`.exe` ne veut pas toujours dire Windows). Toujours utiliser `file` pour vérifier le format réel d'un binaire. L'utilisation de chaînes en clair (_hardcoded strings_) dans un binaire sans obfuscation permet une extraction immédiate via `strings`.
