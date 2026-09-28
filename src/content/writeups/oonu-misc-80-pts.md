---
# Imported from Obsidian: CTF/ESIG Tech Arena CTF/Ɖoɖonu — Writeup (Misc, 80 pts).md
title: Ɖoɖonu — (Misc, 80 pts)
category: Misc
ctf: ESIG Tech Arena 2026
competition: esig-tech-arena-2026
date: 2026-09-25
summary: 'Format confirmé : <numero>|<cledecontrole>|<caractere>.'
tags:
- esig-tech-arena
- esig-tech-arena-2026
- majority-vote
- misc
points: 80
lang: fr
imported: true
---

### 📌 Description
> **Ɖoɖonu** (Misc · medium). Un fichier `data.txt` d'environ 100 000 lignes contient un message secret. Chaque ligne a la forme `<numero>|<cle de controle>|<caractere>`. Certaines lignes sont vraies, d'autres du bruit. Le message final est du base64, le flag est au format `EthACTF{...}`.
>
> **Author** : KodjoDoDjango
**Points** : 80 pts
**First blood** : msi
**Statut** : ✓ Résolu le 25/09 à 11:53 UTC

---
### Étape 1 : Reconnaissance

```bash
wc -l data.txt          # 99980 lignes
head data.txt
```

```
8|180|R
4|107|Q
9|6|n
17|11|H
28|187|Z
...
```

Format confirmé : `<numero>|<cle_de_controle>|<caractere>`.

---
### Étape 2 : Analyse du bruit

En regroupant les lignes par `numero`, on découvre qu'il n'y a que **44 valeurs distinctes de `numero`** (0 à 43) — soit exactement la longueur attendue d'un message court encodé en base64.

```python
from collections import Counter, defaultdict

groups = defaultdict(Counter)
for line in open('data.txt'):
    n, c, ch = line.strip().split('|')
    groups[int(n)][(c, ch)] += 1
```

Pour chaque `numero`, un seul couple `(cle, caractere)` domine très largement (~2045 occurrences) contre 1-2 occurrences pour toutes les autres combinaisons (le bruit aléatoire). La ligne "vraie" est donc simplement la plus fréquente par vote majoritaire.

---
### Étape 3 : Reconstruction et décodage

```python
import base64

msg = ''.join(
    groups[n].most_common(1)[0][0][1]
    for n in sorted(groups)
)
print("b64:", msg)
print(base64.b64decode(msg))
```

```
b64: RXRoQUNURntzY3JpcHRpbmdfc2F2ZXNfdGhlX2RheX0=
decoded: b'EthACTF{scripting_saves_the_day}'
```

> **Pourquoi le vote majoritaire fonctionne**
> Le bruit est généré aléatoirement (clé de contrôle + caractère tirés au hasard pour chaque `numero`), donc statistiquement réparti sur des milliers de combinaisons différentes. La ligne légitime, elle, est répétée des milliers de fois à l'identique — elle écrase totalement le bruit en fréquence.

---
### 🏁 Flag

```
EthACTF{scripting_saves_the_day}
```
