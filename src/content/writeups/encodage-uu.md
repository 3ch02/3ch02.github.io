---
# Imported from Obsidian: RootME/Encodage - UU.md
# Draft: Root-Me rules forbid publishing solutions
title: Encodage - UU
category: Cryptography
difficulty: Easy
ctf: Root-Me
date: 2026-08-13
summary: 'Au lieu de passer par des outils web externes, on utilise l''utilitaire natif uudecode directement dans le terminal pour extraire le fichier :'
tags:
- cryptography
- root-me
lang: fr
draft: true
imported: true
---

> **Détails du Challenge**
> 
> - Plateforme : [Root-Me](https://www.root-me.org/)
> - Catégorie : Cryptographie / Encodage
> - Difficulté : 5 Points (Très Facile)
> - Indice : Très utilisé par le protocole HTTP.

---

##  Informations Générales

- Outils utilisés : `cat`, `uudecode`
- Mot de passe final (PASS) : `ULTRASIMPLE`

---

##  Étape 1 : Analyse et Identification
On récupère le fichier `ch1'''''''''''''''''''''''''''''.txt` associé au challenge pour analyser sa structure brute :

```bash
cat ch1.txt
```

Sortie brute obtenue :

```text
_=_ 
_=_ Part 001 of 001 of file root-me_challenge_uudeview
_=_ 

begin 644 root-me_challenge_uudeview
B5F5R>2!S:6UP;&4@.RD*4$%34R`](%5,5%)!4TE-4$Q%"@``
`
end
```

> **Signature UUencode identifiée à l'œil nu**
> 
> - Présence de la balise d'en-tête caractéristique : `begin 644 root-me_challenge_uudeview` (indiquant les permissions et le nom du fichier d'origine).
> - Présence de la balise de fin unique : `end`.
> - Les lignes de données débutent par un caractère de contrôle de longueur (ex: `B` en ASCII).

---

## 🎯 Étape 2 : Décodage en Ligne de Commande

Au lieu de passer par des outils web externes, on utilise l'utilitaire natif uudecode directement dans le terminal pour extraire le fichier :

```bash
uudecode ch1.txt
```

Une fois le fichier extrait (`root-me_challenge_uudeview`), on affiche son contenu pour récupérer le mot de passe :

```bash
cat root-me_challenge_uudeview
```

Sortie obtenue :

```text
Very simple ;)
PASS = ULTRASIMPLE
```

- Validation du challenge : `ULTRASIMPLE`

---

## ⚡ Mémo Rapide : Reconnaissance des Encodages Texte

|Encodage|Signature / Caractéristiques visuelles|Commande de décodage CLI|
|---|---|---|
|UUencode|Commence par `begin <mode> <file>` et finit par `end`|`uudecode file.txt`|
|Base64|Caractères `[A-Za-z0-9+/=]`, longueur multiple de 4, pas d'espaces|`base64 -d file.txt`|
|Hexadécimal|Suite de chiffres et lettres de `0-9` et `a-f` (paires d'octets)|`xxd -r -p file.txt`|
|URL Encoding|Présence massive de caractères `%` suivis de deux valeurs hexa|`python3 -c "import urllib.parse; ..."`|

Si tu as un autre writeup ou un autre challenge à structurer pour ton coffre-fort Obsidian, envoie-moi les détails et on fait ça !
