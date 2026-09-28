---
# Imported from Obsidian: CTF/ESIG Tech Arena CTF/writeup_le_fil_du_marche_gbeta.md
title: Le Fil du Marché Gbéta
category: Cryptography
ctf: ESIG Tech Arena 2026
competition: esig-tech-arena-2026
date: 2026-09-25
summary: Au port d'Aného, les tisserands du marché Gbéta scellent leurs contrats maritimes dans une langue de signes oubliée des archivistes européens. Un registre unicode extravagant…
tags:
- cryptography
- esig-tech-arena-2026
points: 400
lang: fr
imported: true
---

- **Catégorie :** Crypto — hard
- **Points :** 400 (dynamiques, 400 → 50)
- **Créateur :** ESIG Tech Arena
- **Auteur du write-up :** 3ch0
- **Flag :** `EthACTF{m4rch3_Gb3ta_tiss3_Aneho_2026}`

---

## Énoncé

> Au port d'Aného, les tisserands du marché Gbéta scellent leurs contrats maritimes dans une langue de signes oubliée des archivistes européens. Un registre unicode extravagant circule encore dans les salons — on murmure qu'il viendrait d'une fausse piste laissée par un comptoir parisien obsédé par des « soixante-cinq mille » glyphes.
> Vous avez récupéré une note du marchand, un sceau unicode suspect, et le fil tissé qui contient, dit-on, la relique numérique du syndicat.
> **Mission :** retrouver le décret lisible caché dans le fil, sans vous fier aux apparences du sceau.

Fichiers fournis :

| Fichier | Taille | Contenu |
|---|---|---|
| `sceau_unicode.txt` | 286 o | Glyphes unicode exotiques |
| `note_marchand.txt` | 284 o | Note du marchand (la méthode) |
| `fil_tisseur.gbe` | 57 o | Le message encodé |

---

## 1. Reconnaissance et identification des leurres

L'énoncé plante deux fausses pistes explicites :

- **« un comptoir parisien obsédé par des soixante-cinq mille glyphes »** → 65 536 = 2¹⁶ = le plan Unicode BMP. C'est une allusion au fichier **`sceau_unicode.txt`**.
- **« sans vous fier aux apparences du sceau »** → le sceau est un **leurre assumé**. On ne le décode pas.

Le décret est donc dans **`fil_tisseur.gbe`** :

```
83jR?MQjjGtj?6QdWW6?My0ogRo8_WK2oWeQn2W!0onCQGyMQ0oxhldni
```

Longueur = 57 caractères, jeu de caractères restreint (lettres, chiffres, `?`, `_`, `!`). Un décodage `base85` direct ne donne rien de lisible → l'alphabet et l'ordre ne sont pas standards. La méthode est dans la note.

---

## 2. La note = la clé

```
Sur le linteau du marché Gbéta, le cantique est gravé ainsi (une seule ligne, sans rien ajouter) :

KpeGbagbaGlidjiAnehoMinaQWXZ012346789_t!EthACT?voyagxRndMs

Les vieux disent : « trois fils, deux grains ; le noble avant le commun ».
Le décret tissé est dans fil_tisseur.gbe.
```

Deux informations décisives.

### a) Le cantique = un alphabet personnalisé

Le cantique mélange des mots togolais (Kpe, Gbagba, Glidji, Aného, Mina) et des caractères. Il contient des doublons. En **gardant la première occurrence de chaque caractère** (déduplication en préservant l'ordre), on obtient un alphabet de **41 symboles** :

```
KpeGbaglidjAnhoMQWXZ012346789_t!ECT?vyxRs
```

### b) Le mode d'encodage

- **« trois fils, deux grains »** → **3 symboles encodent 2 octets**.
  Vérification mathématique : pour coder une valeur de 2 octets (0–65535) sur une base *N*, il faut *N*³ ≥ 65536. Avec **N = 41**, on a 41³ = **68 921 ≥ 65 536** ✓. → **base-41, groupes de 3 symboles.**
- **« le noble avant le commun »** → l'octet de **poids fort d'abord** = reconstruction **big-endian** des 2 octets.

**Contrôle de cohérence :** 57 caractères = **19 groupes de 3** → 19 × 2 = **38 octets** en sortie. Longueur crédible pour un flag.

---

## 3. Exploitation

Pour chaque groupe `c0 c1 c2`, on récupère les indices `d0 d1 d2` dans l'alphabet base-41, on reconstruit un entier, puis on le découpe en 2 octets big-endian.

Le seul paramètre à fixer par essai est l'ordre des chiffres dans le groupe. En testant les combinaisons, la bonne est **chiffre de poids faible en tête** :

```
val = d0 + d1·41 + d2·41²      (poids faible d'abord)
octets = [val >> 8, val & 0xFF]  (big-endian)
```

Les autres combinaisons (poids fort d'abord, ou little-endian) produisent des octets aléatoires — ce qui confirme qu'on tient la bonne.

### solve.py

```python
cant = "KpeGbagbaGlidjiAnehoMinaQWXZ012346789_t!EthACT?voyagxRndMs"
fil  = "83jR?MQjjGtj?6QdWW6?My0ogRo8_WK2oWeQn2W!0onCQGyMQ0oxhldni"

# 1) alphabet base-41 : dedup en préservant l'ordre
seen = []
for ch in cant:
    if ch not in seen:
        seen.append(ch)
alpha = "".join(seen)                     # 41 symboles
idx = {c: i for i, c in enumerate(alpha)}
B = len(alpha)                            # 41

# 2) groupes de 3 symboles -> 2 octets (big-endian)
out = bytearray()
for i in range(0, len(fil), 3):
    d = [idx[c] for c in fil[i:i+3]]
    val = d[0] + d[1] * B + d[2] * B * B  # poids faible en tête
    out += bytes([(val >> 8) & 0xFF, val & 0xFF])

print(out.decode())
```

### Sortie

```
EthACTF{m4rch3_Gb3ta_tiss3_Aneho_2026}
```

---

## 4. Flag

```
EthACTF{m4rch3_Gb3ta_tiss3_Aneho_2026}
```

---

## 5. Leçons

- Les éléments les plus voyants (sceau unicode, « 65 536 glyphes ») étaient des leurres — l'énoncé le disait littéralement (« ne vous fiez pas aux apparences du sceau »).
- Toute la crypto tenait dans la lecture au premier degré de la note :
  - *cantique* → alphabet base-41 (dedup en préservant l'ordre) ;
  - *trois fils, deux grains* → groupes de 3 symboles ↔ 2 octets ;
  - *le noble avant le commun* → octets big-endian.
- Un contrôle de longueur (57 → 19×3 → 38 octets) valide l'hypothèse avant même de coder.

*— 3ch0*
