---
# Imported from Obsidian: CTF/BRCTF/Two-Time_Pad.md
title: Two-Time Pad
category: Cryptography
difficulty: Hard
ctf: brCTF 2026
competition: brctf-2026
date: 2026-10-01
summary: 'Énoncé : The cardinal sin of one-time pads: two different messages were XOR-encrypted with the same keystream. One of the plaintexts is the flag. (L''autre message est de l''anglais…'
tags:
- brctf-2026
- cryptography
points: 95
lang: fr
imported: true
---

## Informations

- **Catégorie :** Cryptography
- **Difficulté :** Hard
- **Points :** 95
- **Auteur du write-up :** 3ch0
- **Flag :** `cspp{0tp_keystream_reuse_is_fatal}`

> **Énoncé :** The cardinal sin of one-time pads: two different messages were XOR-encrypted with the same keystream. One of the plaintexts is the flag. (L'autre message est de l'anglais ordinaire.)
>
> ```
> c1 = f16d20200861e559b9d35fba386420a9f517b60a9c643d024b3ceb9176ef22ac7033
> c2 = e67635700224f84a8d9858b124673cecf2159158936423176775f7b875fc76ac3c22
> ```

---

## 1. La vulnérabilité — réutilisation du keystream

Un One-Time Pad est **inconditionnellement sûr… une seule fois**. Le « péché capital » est de réutiliser la même clé `k` pour deux messages :

```
c1 = p1 ⊕ k
c2 = p2 ⊕ k
```

En XORant les deux chiffrés, **la clé s'annule** (`k ⊕ k = 0`) :

```
c1 ⊕ c2 = (p1 ⊕ k) ⊕ (p2 ⊕ k) = p1 ⊕ p2
```

On obtient `p1 ⊕ p2` : le XOR des deux plaintexts, **sans la clé**. Il ne reste qu'à séparer les deux messages.

---

## 2. Attaque — crib-dragging

On ne connaît pas `p1` ni `p2` séparément, seulement `p1 ⊕ p2`. Mais si on **devine** un fragment d'un des messages (un *crib*) à une position donnée, on le XOR contre `p1 ⊕ p2` et **ça révèle le fragment correspondant de l'autre message** :

```
(p1 ⊕ p2) ⊕ crib_p1 = p2    (aux positions du crib)
```

Ici deux cribs évidents :
- le **format du flag** : `cspp{`
- une **phrase anglaise** connue (l'énoncé insiste sur « ordinary English »).

### Premier coup — le préfixe du flag

On place `cspp{` en position 0 :

```python
cspp{  ⊕  (p1⊕p2)[0:5]  ->  b'the q'
```

→ l'autre message commence par **« the q… »** : c'est le pangramme **« the quick brown fox… »**. Les deux cribs se confirment mutuellement.

### Extension — on déroule le pangramme

On XOR la phrase complète contre `p1 ⊕ p2` → le flag apparaît en entier :

```
the quick brown fox jumps over a l…   (34 octets)
cspp{0tp_keystream_reuse_is_fatal}
```

**Flag :** `cspp{0tp_keystream_reuse_is_fatal}`

---

## 3. Script de résolution (réutilisable)

Solveur générique de crib-drag : il glisse un mot/crib à **toutes les positions** et n'affiche que les résultats « lisibles » (ASCII imprimable). Utile pour n'importe quel challenge two-time pad / keystream reuse.

```python
#!/usr/bin/env python3
# crib_drag.py — solveur two-time pad (keystream reuse)
import string

# --- Entrées : les deux chiffrés en hex -------------------------------------
c1 = bytes.fromhex("f16d20200861e559b9d35fba386420a9f517b60a9c643d024b3ceb9176ef22ac7033")
c2 = bytes.fromhex("e67635700224f84a8d9858b124673cecf2159158936423176775f7b875fc76ac3c22")

x = bytes(a ^ b for a, b in zip(c1, c2))   # p1 ⊕ p2
PRINTABLE = set(bytes(string.printable, "ascii"))

def xor(a, b):
    return bytes(i ^ j for i, j in zip(a, b))

def crib_drag(crib):
    """Glisse `crib` à chaque position ; montre les sorties lisibles."""
    crib = crib.encode() if isinstance(crib, str) else crib
    for off in range(0, len(x) - len(crib) + 1):
        res = xor(x[off:off + len(crib)], crib)
        if all(c in PRINTABLE for c in res):
            print(f"off {off:2d} | crib {crib!r:20} -> {res!r}")

def reveal(crib, off=0):
    """Si on connaît un plaintext (crib) à l'offset off, renvoie l'autre."""
    crib = crib.encode() if isinstance(crib, str) else crib
    return xor(x[off:off + len(crib)], crib)

if __name__ == "__main__":
    # 1) crib-drag avec des mots courants + le format du flag
    for w in [" the ", "cspp{", " flag", "quick", "brown", " over "]:
        crib_drag(w)

    # 2) une fois une piste trouvée, on déroule :
    print(reveal("the quick brown fox jumps over a lazy dog"))   # -> le flag
```

Exécution → le flag tombe directement.

---

## Récapitulatif

1. Même keystream pour `c1` et `c2` → `c1 ⊕ c2 = p1 ⊕ p2` (la clé disparaît).
2. **Crib-drag** : deviner `cspp{` (flag) révèle « the q… » (pangramme).
3. Dérouler le pangramme contre `p1 ⊕ p2` → flag complet.

> **Concept clé :** la sécurité de l'OTP repose **entièrement** sur l'unicité du keystream. Le réutiliser détruit toute la garantie : l'attaquant récupère `p1 ⊕ p2` et, avec un peu de texte connu/devinable (format de flag, langue), reconstruit les deux messages **sans la clé**. C'est aussi la faille historique du projet VENONA (messages soviétiques cassés pour cause de pads réutilisés). Règle : une clé de flux ne se réutilise **jamais** (d'où les nonces uniques en ChaCha20/AES-CTR).

---

***— 3ch0***
