---
# Imported from Obsidian: CTF/BRCTF/HideAndSeek_II.md
title: HideAndSeek II
category: Reverse Engineering
difficulty: Easy
ctf: brCTF 2026
competition: brctf-2026
date: 2026-10-01
summary: 'Énoncé : Round two of the game, and the hiding spot is trickier. What worked before won''t cut it now. The developers watched people beat the first round and moved the goalposts…'
tags:
- brctf-2026
- reverse-engineering
points: 70
lang: fr
imported: true
---

> Compétition : **brCTF** — Challenge ID#8

## Informations

- **Catégorie :** Mobile (Android — reverse natif)
- **Difficulté :** Easy
- **Points :** 70
- **Auteur du write-up :** 3ch0
- **Flag :** `BRCTF{s0_1t_w4s_1n_th3_.s0_4ll_4l0ng}`

> **Énoncé :** Round two of the game, and the hiding spot is trickier. What worked before won't cut it now. The developers watched people beat the first round and moved the goalposts. Seek harder.

---

## 1. Décompilation

```bash
apktool d HideAndSeekII.apk
cd HideAndSeekII
grep -ri brctf .
```

Contrairement au round 1 (flag dans le `AndroidManifest.xml`), le manifeste est propre. Le `grep` matche en revanche dans les **bibliothèques natives** :

```text
grep: ./lib/arm64-v8a/libhideandseek2.so: binary file matches
grep: ./lib/x86_64/libhideandseek2.so:   binary file matches
...
```

Le smali révèle une méthode native `ping()` appelée au démarrage de `MainActivity`. Le secret est donc dans `libhideandseek2.so`.

---

## 2. Analyse de la lib x86_64 (le piège)

On désassemble et on inspecte `.rodata` de l'archi x86_64 (réflexe naturel, car c'est celle qu'on analyse le plus facilement) :

```bash
objdump -d lib/x86_64/libhideandseek2.so > disasm.txt
objdump -s -j .rodata lib/x86_64/libhideandseek2.so
```

La fonction `ping()` se contente de retourner la chaîne `"marco"` via `NewStringUTF` (clin d'œil à Marco Polo / cache-cache). Juste après `"marco"` dans `.rodata` traîne un **long blob base64**. On le décode en boucle :

```python
import base64
cur = "VVRKNGRtTXlWV2RNVXpCblpFZG9jR041UW5CamVVSXpaVWRYZVZwVFFuUmlOMDR3U1VkV2RHUlhlR2hrUnpsNVkzbE5qTWxYVGxkMFRXRlVTa1JhUm1oU1dqSlNTR0ZIZUVwVFJYQnpWMVprTTFveGNFaFdha3BvVmpBMWMxTlVhR3RqR0oxVFdka2ExSXlhSGRZTTJ4RFpWZEplbFp1Vm1GRmVsRTU"
for _ in range(3):
    cur = base64.b64decode(cur + "="*((4-len(cur)%4)%4)).decode()
print(cur)
```

```text
Close -- this is where most emulators land. But the real device wins this round.
```

> **C'est un leurre.** Pas de flag — un message troll. Mais ce message **est l'indice** : « most emulators land [here] » = les émulateurs Android tournent en **x86/x86_64** ; « the real device wins this round » = les **vrais téléphones sont en ARM**. Le vrai flag est dans la lib **`arm64-v8a`**.

---

## 3. Analyse de la lib ARM64 (le vrai flag)

On refait exactement la même manip sur la bonne architecture :

```bash
objdump -s -j .rodata lib/arm64-v8a/libhideandseek2.so
```

```text
 0500 6d617263 6f005656 64345331 4a47576b  marco.VVd4S1JGWk
 0510 5a58616d 52715a57 744b6256 52576146  ZXamRqZWtKbVRWaF
 ...
 0560 6c515554 303900                      lQUT09.
```

Un **blob base64 différent** suit le `"marco"`. On le décode de la même façon :

```python
import base64
cur = "VVd4S1JGWkZXamRqZWtKbVRWaFNabVI2VW5wWWVrWjFXRE5TYjAweE9IVmpla0ptVGtkNGMxaDZWbk5OUnpWdVpsRTlQUT09"
for _ in range(3):
    cur = base64.b64decode(cur + "="*((4-len(cur)%4)%4)).decode()
print(cur)
```

Déchiffrement couche par couche (triple base64) :

```text
couche 1 : UWxKRFZFWjdjekJmTVhSZmR6UnpYekZ1WDNSb00xOHVjekJmTkd4c1h6UnNNRzVuZlE9PQ==
couche 2 : QlJDVEZ7czBfMXRfdzRzXzFuX3RoM18uczBfNGxsXzRsMG5nfQ==
couche 3 : BRCTF{s0_1t_w4s_1n_th3_.s0_4ll_4l0ng}
```

**Flag :** `BRCTF{s0_1t_w4s_1n_th3_.s0_4ll_4l0ng}`

> Soit *« so it was in the .so all along »* — le flag confirme la cachette.

---

## Récapitulatif de la chaîne d'exploitation

1. **apktool + grep** → manifeste propre, match dans les `.so` natifs (méthode `ping()`).
2. **lib x86_64** → blob base64 → triple décodage → **message leurre** : « real device wins ».
3. **Interprétation de l'indice** → émulateur = x86, vrai device = **ARM** → analyser `arm64-v8a`.
4. **lib arm64-v8a** → autre blob → triple base64 → flag.

> **Concept clé :** un APK embarque une lib native **par architecture** (`lib/<abi>/`). Un développeur peut y placer des contenus **différents selon l'ABI** : ici, un leurre dans la build x86 (celle des émulateurs, où les analystes travaillent) et le vrai secret dans la build ARM (celle des vrais téléphones). En reverse, il faut penser à **vérifier toutes les architectures**, pas seulement la plus pratique à ouvrir. L'empilement de base64 n'ajoute, lui, aucune sécurité — juste du décodage répété.

---

***— 3ch0***
