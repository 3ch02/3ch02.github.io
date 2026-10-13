---
# Imported from Obsidian: csplusplus CTF/Four-Digit Lock.md
title: Four-Digit Lock
category: Forensics
difficulty: Hard
ctf: csplusplus
date: 2026-09-30
summary: 'Énoncé : This ZIP is encrypted with a 4-digit numeric PIN — only 10,000 possibilities. Brute-force it (a short script with Python''s zipfile, or a tool like fcrackzip), extract the…'
tags:
- csplusplus
- forensics
points: 75
lang: fr
imported: true
---

## Informations

- **Catégorie :** Forensics
- **Difficulté :** Hard
- **Points :** 75
- **Auteur du write-up :** 3ch0
- **Flag :** `cspp{z1p_pin_brut3forced}`

> **Énoncé :** This ZIP is encrypted with a 4-digit numeric PIN — only 10,000 possibilities. Brute-force it (a short script with Python's `zipfile`, or a tool like `fcrackzip`), extract the file, and read the flag.

---

## 1. Analyse

L'archive `locked.zip` est protégée par mot de passe. Une tentative d'extraction directe échoue :

```bash
unzip locked.zip
```

```text
[locked.zip] _inner.dat password:
   skipping: _inner.dat              incorrect password
```

L'énoncé nous apprend que le mot de passe est un **PIN numérique de 4 chiffres** : seulement **10 000 combinaisons** possibles (`0000` → `9999`). C'est un espace de recherche trivial à brute-forcer.

---

## 2. Extraction du hash (zip2john)

On extrait le hash de l'archive dans un format exploitable par John the Ripper :

```bash
zip2john locked.zip > lock.hash
```

```text
locked.zip/_inner.dat PKZIP Encr: 2b chk, TS_chk, cmplen=37, decmplen=25, ...
```

Le chiffrement est du **PKZIP** (ZipCrypto legacy), rapide à casser.

---

## 3. Brute force (John the Ripper)

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt lock.hash
```

```text
7531             (locked.zip/_inner.dat)
1g 0:00:00:01 DONE ... 1436Kp/s
```

> **Mot de passe trouvé : `7531`** — cassé en moins d'une seconde (rockyou contient tous les PIN à 4 chiffres).

---

## 4. Extraction et lecture du flag

```bash
unzip locked.zip     # mot de passe : 7531
cat _inner.dat
```

```text
cspp{z1p_pin_brut3forced}
```

---

## Méthode alternative — brute force ciblé

Plutôt que d'utiliser rockyou (qui contient bien plus que des chiffres), on peut générer exactement les 10 000 PIN et les tester. Plus rapide et plus rigoureux vis-à-vis de l'énoncé.

### Avec fcrackzip

```bash
fcrackzip -b -c1 -l4-4 -u locked.zip
```

- `-b` : mode brute force
- `-c1` : charset numérique uniquement
- `-l4-4` : longueur exactement 4
- `-u` : valide en tentant l'extraction (évite les faux positifs)

### Avec Python (zipfile)

```python
import zipfile

z = zipfile.ZipFile("locked.zip")
for pin in range(10000):
    pwd = f"{pin:04d}"                      # 0000 → 9999
    try:
        z.extractall(pwd=pwd.encode())
        print(f"[+] PIN trouvé : {pwd}")
        break
    except (RuntimeError, zipfile.BadZipFile):
        continue
```

---

## Récapitulatif

1. Archive ZIP chiffrée par un **PIN à 4 chiffres** (10 000 possibilités).
2. **`zip2john`** → extraction du hash PKZIP.
3. **`john`** (ou `fcrackzip` / script Python) → PIN = `7531`.
4. Extraction de `_inner.dat` → flag.

> **Concept clé :** un espace de clés minuscule (4 chiffres) rend le chiffrement inutile. La longueur/complexité du mot de passe est ce qui protège une archive, pas le chiffrement seul.

---

***— 3ch0***
