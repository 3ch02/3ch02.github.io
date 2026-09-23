---
# Imported from Obsidian: CTF/picoCTF/Writeup CTF — Reverse Engineering (Medium).md
title: Reverse Engineering
category: Reverse Engineering
ctf: picoCTF
date: 2026-08-07
summary: Le challenge fournit un code source Python d'un service distant qui propose de générer un nombre aléatoire ou d'afficher du code ésotérique, mais une fonction nommée win() semble…
tags:
- picoctf
- reverse-engineering
lang: fr
imported: true
---

## 📝 Description du Challenge

> **Description :** This service can provide you with a random number, but can it do anything else?
> 
> **Connexion :** `nc saturn.picoctf.net 51027`

Le challenge fournit un code source Python d'un service distant qui propose de générer un nombre aléatoire ou d'afficher du code ésotérique, mais une fonction nommée `win()` semble contenir le précieux flag.

## 1. Analyse du Code Source (La vulnérabilité `eval`)

En inspectant la boucle principale du script Python, on repère immédiatement une fonction native très dangereuse :

```python
while(True):
    try:
        print('Try entering "getRandomNumber" without the double quotes...')
        user_input = input('==> ')
        eval(user_input + '()')
    except Exception as e:
        print(e)
        break
```

### Le problème avec `eval()`

La fonction `eval()` évalue et exécute dynamiquement n'importe quelle chaîne de caractères qu'on lui passe comme du code Python légitime. Ici, l'application prend notre entrée (`user_input`) et y concatène des parenthèses `()`.

Si un utilisateur entre la chaîne `getRandomNumber`, le backend exécute dynamiquement la commande :

```python
eval("getRandomNumber" + "()")  # Équivaut à exécuter getRandomNumber()
```

## 2. Exploitation & Détournement de Flux

Puisque nous contrôlons totalement le nom de la fonction appelée, nous n'avons qu'à regarder les fonctions disponibles dans l'espace de nommage du script. La fonction `win()` est définie ainsi :

```python
def win():
    flag = open('flag.txt', 'r').read()
    flag = flag.strip()
    str_flag = ''
    for c in flag:
        str_flag += str(hex(ord(c))) + ' '
    print(str_flag)
```

Cette fonction ouvre le fichier `flag.txt` sur le serveur, convertit chaque caractère en sa valeur hexadécimale ASCII, puis l'affiche.

### Envoi du Payload

Il nous suffit de nous connecter via `netcat` et de soumettre simplement le mot clé `win` pour forcer le serveur à exécuter `win()`.

```bash
nc saturn.picoctf.net 51027
```

**Sortie du serveur :**

```
Try entering "getRandomNumber" without the double quotes...
==> win
0x70 0x69 0x63 0x6f 0x43 0x54 0x46 0x7b 0x34 0x5f 0x64 0x31 0x34 0x6d 0x30 0x6e 0x64 0x5f 0x31 0x6e 0x5f 0x37 0x68 0x33 0x5f 0x72 0x30 0x75 0x67 0x68 0x5f 0x63 0x65 0x34 0x62 0x35 0x64 0x35 0x62 0x7d 
```

## 🏁 3. Décodage du Flag

Le serveur nous renvoie une suite de valeurs hexadécimales. Pour retrouver le texte d'origine, nous pouvons passer cette chaîne dans la recette **"From Hex"** de l'outil **CyberChef** (ou utiliser un script de conversion rapide).

- `0x70` ➔ `p`
    
- `0x69` ➔ `i`
    
- `0x63` ➔ `c`
    
- `0x6f` ➔ `o`
    
- _(Et ainsi de suite...)_
    

**Flag décodé :**

```
picoCTF{4_d14m0nd_1n_7h3_r0ugh_ce4b5d5b}
```

**_3ch0 training_**
