---
# Imported from Obsidian: CTF/Writeup IPNET Cyberbattle/🚩 Writeup CTF - Challenge USB.ad1.md
title: USB.ad1
category: Steganography
difficulty: Medium
ctf: IPNET CyberBattle 2026
competition: ipnet-cyberbattle-2026
date: 2026-08-12
summary: Les fichiers .ad1 (AccessData FTK Imager Logical Image) sont fréquemment utilisés en forensics.
tags:
- ad1
- forensics
- ipnet-cyberbattle-2026
- john-the-ripper
- python
- steganography
- stegsnow
lang: fr
imported: true
---

> ****Aperçu du Challenge****
> * **Nom du fichier** : `USB.ad1` (8.4 Mo)
> * **Catégories** : Forensics & Stéganographie
> * **Système d'analyse** : Kali Linux (Sans FTK Imager GUI)
> * **Flag final** : `c2hhcmQtNA_d2077a62-456b-4093-9963-fd8197689b0e`

---

## 📌 Contextualisation & Défi sous Kali Linux

Les fichiers **`.ad1`** (*AccessData FTK Imager Logical Image*) sont fréquemment utilisés en forensics. 

> ****Note Kali Linux****
> **FTK Imager (GUI)** est un outil Windows non disponible nativement sous Kali Linux. Sous Linux/Kali, nous pouvons soit :
> 1. Dépaqueter l'image AD1 via un script **Python** automatisé exploitant la structure des blocs `zlib`.
> 2. Utiliser `stegsnow`, `zip2john` et `john` directement depuis le terminal Kali.

---

## 🔍 Étape 1 : Extraction de l'image AD1 sous Kali Linux

La signature magique d'un fichier `.ad1` est `ADSEGMENTEDFILE` (`41 44 53 45 47 4d 45 4e 54 45 44 46 49 4c 45`). Les données des fichiers sont stockées sous forme de flux **zlib** (`0x789c` / `0x7801`).

### 🐍 Script d'extraction Python (`extract_ad1.py`)

Afin d'extraire tous les fichiers sans FTK Imager :

```python
import os, re, zlib

ad1_path = "USB.ad1"
out_dir = "./extracted_files"
os.makedirs(out_dir, exist_ok=True)

with open(ad1_path, "rb") as f:
    data = f.read()

# Recherche des noms de fichiers dans les métadonnées AD1
matches = re.finditer(rb'([A-Za-z0-9_\-\.\ ]+\.(txt|py|pdf|zip|png|jpg|jpeg))', data, re.IGNORECASE)

for m in matches:
    fname = m.group(1).decode("latin1", errors="ignore")
    fn_start = m.start()
    
    # Recherche du bloc zlib (0x78) suivant le nom de fichier
    search_region = data[fn_start:fn_start+500]
    z_idx = -1
    for i in range(len(search_region)-2):
        if search_region[i:i+1] == b'\x78' and search_region[i+1] in (0x01, 0x9c, 0xda):
            z_idx = fn_start + i
            break
            
    if z_idx != -1:
        try:
            decomp = zlib.decompress(data[z_idx:z_idx+65536])
            out_path = os.path.join(out_dir, fname)
            with open(out_path, "wb") as f_out:
                f_out.write(decomp)
            print(f"[+] Extrait : {fname} ({len(decomp)} bytes)")
        except Exception:
            pass
```

### 📦 Fichiers extraits :
* `100` fichiers journaux : `Day_01.txt` à `Day_100.txt`
* `1` image : `Quantum.jpeg`
* `1` archive ZIP chiffrée : **`TheLastQuantumSearch.zip`**

---

## 🕵️‍♂️ Étape 2 : Stéganographie Whitespace (`stegsnow`)

En examinant le fichier `Day_72.txt`, la taille du fichier et la présence de nombreuses tabulations (`\t`) et d'espaces invisibles en fin de ligne révèlent une stéganographie de type **SNOW / Whitespace**.

### 💻 Commande sous Kali Linux :

```bash
stegsnow extracted_files/Day_72.txt
```

> ****Découverte****
> L'extraction `stegsnow` confirme la présence de données masquées liées à l'archive chiffrée **`TheLastQuantumSearch.zip`** contenant le fichier cible `Nouveau dossier/donT_Look_4T_me.txt`.

---

## 🔓 Étape 3 : Cassage du mot de passe de l'archive ZIP (`zip2john` + `john`)

L'archive `TheLastQuantumSearch.zip` est protégée par un chiffrement **WinZip AES-256**.

### 1️⃣ Extraction du Hash du ZIP

Sous Kali Linux, on extrait le hash compatible avec John the Ripper :

```bash
zip2john TheLastQuantumSearch.zip > zip.hash
```

*Contenu du hash généré* :
```text
TheLastQuantumSearch.zip/Nouveau dossier/donT_Look_4T_me.txt:$zip2$*0*3*0*fd6e0fa4a195fe456980b309407c7d5e*...
```

### 2️⃣ Attaque par dictionnaire avec John the Ripper

On utilise le dictionnaire standard `rockyou.txt` :

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt zip.hash
```

### 🎯 Résultat de la commande :

```text
Using default input encoding: UTF-8
Loaded 1 password hash (ZIP, WinZip [PBKDF2-SHA1 256/256 AVX2 8x])
volleyball       (TheLastQuantumSearch.zip/Nouveau dossier/donT_Look_4T_me.txt)     
1g 0:00:00:00 DONE (2026-08-12 09:59) 2.702g/s
```

> ****Mot de passe trouvé** : `volleyball`**

---

## 🚩 Étape 4 : Extraction & Révélation du Flag

Une fois le mot de passe extrait, déchiffrement de l'archive en Python / 7z :

```python
import pyzipper

with pyzipper.AESZipFile("TheLastQuantumSearch.zip") as zf:
    zf.setpassword(b"volleyball")
    zf.extractall("./final_flag")

with open("./final_flag/Nouveau dossier/donT_Look_4T_me.txt", "r") as f:
    print(f.read())
```

### 📄 Contenu du fichier `donT_Look_4T_me.txt` :

```text
c2hhcmQtNA_d2077a62-456b-4093-9963-fd8197689b0e
```

> ****Analyse du Flag****
> * `c2hhcmQtNA` en Base64 = `shard-4`.
> * **Flag final à soumettre** : `c2hhcmQtNA_d2077a62-456b-4093-9963-fd8197689b0e` (ou `shard-4_d2077a62-456b-4093-9963-fd8197689b0e`).

---

## ⚡ Cheatsheet Kali Linux (Mémo Rapide CTF)

| Situation | Commande Kali Linux |
| --- | --- |
| **Inspecter les en-têtes d'un fichier anonyme** | `file USB.ad1` ou `head -c 32 USB.ad1 \| xxd` |
| **Extraire un hash de ZIP** | `zip2john fichier.zip > zip.hash` |
| **Casser un hash avec rockyou** | `john --wordlist=/usr/share/wordlists/rockyou.txt zip.hash` |
| **Afficher le mot de passe cassé** | `john --show zip.hash` |
| **Extraire de la stéganographie d'espaces (Whitespace)** | `stegsnow fichier.txt` (ou avec pass: `stegsnow -p "password" fichier.txt`) |
