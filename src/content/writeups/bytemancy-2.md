---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/📝 Writeup Chall - Bytemancy-2.md
title: Bytemancy-2
category: Web
ctf: picoCTF 2026
date: 2026-08-07
summary: 'Can you conjure the right bytes? The program''s source code can be downloaded here. Additional details will be available after launching your challenge instance. Code: Flag :'
tags:
- picoctf-2026
- web
lang: fr
imported: true
---

#### Description

Can you conjure the right bytes? The program's source code can be downloaded [here](https://challenge-files.picoctf.net/c_lonely_island/a6767dde47334a8130dc9cc8d1f65f6952e070403565c1d350b4378ed777fa4e/app.py).

Additional details will be available after launching your challenge instance.

Code:
```
import sys

  

while(True):

  try:

    print('⊹──────[ BYTEMANCY-2 ]──────⊹')

    print("☍⟐☉⟊☽☈⟁⧋⟡☍⟐☉⟊☽☈⟁⧋⟡☍⟐☉⟊☽☈⟁⧋⟡☍⟐")

    print()

    print('Send me the HEX BYTE 0xFF 3 times, side-by-side, no space.')

    print()

    print("☍⟐☉⟊☽☈⟁⧋⟡☍⟐☉⟊☽☈⟁⧋⟡☍⟐☉⟊☽☈⟁⧋⟡☍⟐")

    print('⊹─────────────⟡─────────────⊹')

    print('==> ', end='', flush=True)

    user_input = sys.stdin.buffer.readline().rstrip(b"\n")

    if user_input == b"\xff\xff\xff":

      print(open("./flag.txt", "r").read())

      break

    else:

      print("That wasn't it. I got: " + str(user_input))

      print()

      print()

      print()

  except Exception as e:

    print(e)

    break
```

Flag : 
```
picoCTF{3ff5_4_d4yz_5ce8506f}

```

### 🔍 Observation du code source

Le script Python utilise `sys.stdin.buffer.readline()`. L'utilisation du **`.buffer`** est cruciale : elle indique que le programme lit l'entrée standard en mode **binaire (bytes)** et non en mode texte (string).

La condition de victoire est la suivante :

```python
if user_input == b"\xff\xff\xff":
    print(open("./flag.txt", "r").read())
```

Le préfixe `b` devant la chaîne signifie que le programme attend exactement trois octets dont la valeur hexadécimale est `0xFF` (soit 255 en décimal).

### 💡 Pourquoi une saisie classique échoue ?

Tenter de taper `\xff\xff\xff` ou `ffffff` directement au clavier ne fonctionnera pas pour deux raisons :

1. **Représentation vs Valeur** : Si on tape `\xff`, le terminal envoie quatre caractères ASCII distincts (`\`, `x`, `f`, `f`). Le programme recevrait alors les octets `0x5c 0x78 0x66 0x66` au lieu de l'octet unique `0xff`.
    
2. **Problème d'encodage (UTF-8)** : Même en utilisant des caractères spéciaux comme `ÿ` (qui correspond au code 255 en Latin-1), la plupart des terminaux modernes encodent la saisie en **UTF-8**. En UTF-8, le caractère `ÿ` est envoyé sous la forme de deux octets (`0xc3 0xbf`), ce qui ne correspondra jamais à la comparaison binaire du script.
    

### 🛠️ Stratégie d'Exploitation

Pour réussir, il faut "injecter" des octets bruts dans le flux d'entrée (`stdin`). On utilise pour cela des outils capables d'interpréter les séquences d'échappement hexadécimales et de les transmettre via un **pipe** (`|`).

- **`printf`** : L'outil le plus fiable pour formater des données binaires.
    
- **`echo -ne`** : L'option `-e` interprète le hex et `-n` évite d'ajouter un saut de ligne indésirable.
    
- **`python3 -c`** : Permet d'écrire directement dans le buffer de sortie pour une précision totale.
    

---

### 🚀 Payload

```bash
# Utilisation de printf pour envoyer les octets bruts au serveur
printf "\xff\xff\xff" | nc [HOST] [PORT]
```
