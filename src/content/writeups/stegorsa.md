---
# Imported from Obsidian: CTF/picoCTF/Writeup - StegoRSA.md
title: StegoRSA
category: Steganography
ctf: picoCTF
date: 2026-06-21
summary: La première étape consiste à inspecter l'image à la recherche d'informations cachées. En sécurité et en CTF, le premier réflexe avec un fichier multimédia est d'analyser ses…
tags:
- exiftool
- openssl
- picoctf
- steganography
- xxd
points: 100
lang: fr
imported: true
---

tags:

---

## 📑 Writeup : tegoRSA (Cryptography - 100 pts)

**Challenge :** tegoRSA  
**Catégorie :** Cryptography / Steganography  
**Auteur :** Yahaya Meddy  
**Flag :** `picoCTF{rs4_k3y_1n_1mg_51611ab8}`

---

### 📝 1. Description du Challenge
Le challenge nous indique qu'un message a été chiffré avec RSA. La clé publique est manquante, mais le créateur sous-entend qu'une erreur a été commise avec la clé privée. Deux fichiers nous sont fournis :
* `image.jpg` : Une image standard.
* `flag.enc` : Le flag chiffré.

---

### 🔍 2. Phase de Reconnaissance & Analyse

La première étape consiste à inspecter l'image à la recherche d'informations cachées. En sécurité et en CTF, le premier réflexe avec un fichier multimédia est d'analyser ses métadonnées.

#### Outil utilisé : ExifTool
**ExifTool** est un outil en ligne de commande permettant de lire, écrire et analyser les métadonnées (EXIF, IPTC, XMP) contenues dans une grande variété de fichiers (images, PDF, vidéos).

**Commande exécutée :**
```bash
exiftool image.jpg
````

**Résultat clé obtenu :**

Dans la sortie de la commande, le champ `Comment` contenait une très longue chaîne de caractères au format hexadécimal commençant par :

```
Comment : 2d2d2d2d2d424547494e2050524956415445204b45592d2d2d2d2d0a...
```

![Screenshot](./images/obsidian/stegorsa/pasted-image-20260621121342.png)

#### Analyse de la signature hexadécimale :

En observant les premiers octets, on peut appliquer une traduction ASCII rapide :

- `2d` correspond au caractère `-` (tiret).
    
- `42 45 47 49 4e` correspond aux lettres `B E G I N`.
    

Cinq octets `2d` suivis de `BEGIN` traduisent la chaîne textuelle `-----BEGIN`. C'est la signature exacte d'une clé privée au format **PEM**. La clé privée a donc été convertie en hexadécimal puis injectée dans les commentaires de l'image.

### 3. Extraction et Décodage de la Clé Privée

Il faut maintenant extraire cette chaîne hexadécimale brute pour la reconstruire en un fichier texte ASCII valide.

#### Outil utilisé : xxd

`xxd` est un utilitaire Linux puissant qui permet de créer des dumps hexadécimaux à partir de fichiers binaires, ou inversement, de reconstruire un binaire (ou du texte) à partir d'un dump hexadécimal.

- L'option `-r` (reverse) : Demande à `xxd` de convertir de l'hexadécimal vers du texte/binaire.
    
- L'option `-p` (plain) : Indique que le dump est continu (sans colonnes d'adresses ni espaces superflus).
    

**Commande de reconstruction :**

```
echo -n "2d2d2d2d2d424547...[CHAINE_COMPLETE]...2d0a" | xxd -r -p > private.key
```

En faisant un `cat private.key`, on valide la bonne structure du fichier :

```
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCtVf6CDwFYrEnH
...
-----END PRIVATE KEY-----
```

### 4. Déchiffrement du Message avec RSA

Nous disposons désormais de la clé privée (`private.key`) et du fichier chiffré (`flag.enc`). Le chiffrement RSA étant un mécanisme asymétrique, la clé privée possède les propriétés mathématiques nécessaires pour inverser l'opération de chiffrement appliquée par la clé publique.

#### Outil utilisé : OpenSSL (pkeyutl)

**OpenSSL** est la boîte à outils de référence pour les protocoles de sécurité et la cryptographie sous Linux. Nous utilisons son sous-module `pkeyutl` (Public Key Utility) dédié aux opérations de chiffrement, déchiffrement, signature et vérification avec des paires de clés asymétriques.

**Commande de déchiffrement :**

```bash
openssl pkeyutl -decrypt -inkey private.key -in flag.enc -out flag.txt
```

#### Explication des arguments de la commande :

- `pkeyutl` : Appelle le sous-module de gestion des clés asymétriques.
    
- `-decrypt` : Spécifie que l'opération demandée est un déchiffrement.
    
- `-inkey private.key` : Indique le chemin du fichier contenant la clé privée de déchiffrement.
    
- `-in flag.enc` : Spécifie le fichier d'entrée contenant le message chiffré (le ciphertext).
    
- `-out flag.txt` : Indique le nom du fichier de sortie où écrire le résultat clair.
    

### 🏁 5. Obtention du Flag

Il ne reste plus qu'à lire le fichier généré :

```
cat flag.txt
```

```
picoCTF{rs4_k3y_1n_1mg_51611ab8}
```

### 🧠 Résumé de la méthodologie CTF

1. **Analyse des formats :** Toujours inspecter les fichiers annexes (`image.jpg`) avec `exiftool` pour détecter les fuites d'informations dans les métadonnées.
    
2. **Reconnaissance de motifs :** Savoir que la suite d'octets `2d2d2d2d2d424547494e` représente la bannière de sécurité `-----BEGIN`.
    
3. **Maîtrise de la chaîne d'outils :** Combiner `xxd` pour la manipulation de flux bruts et `openssl` pour l'application des primitives cryptographiques.
