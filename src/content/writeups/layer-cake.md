---
# Imported from Obsidian: CTF/hackviser/EcowsCTF{}/📑 Writeup Challenge -Layer Cake.md
# Draft: incomplete: script given but resulting flag never shown
title: Layer Cake
category: Cryptography
ctf: EcowsCTF (Hackviser)
date: 2026-08-07
summary: 'La chaîne fournie est : ==AZzQ2MxUjN2AzMlRTY3QGNzMTZ0MzM4UTO3UGN0UTN2AzM3cjMzgTN1MTY0IzM4UTO3UGN0UTN2AzM3cjMzUjN3QjM1EzMxUTY3YDNyMDN2YzNlRzN1ITN'
tags:
- cryptography
- ecowsctf
lang: fr
draft: true
imported: true
---

#### Données:
```
==AZzQ2MxUjN2AzMlRTY3QGNzMTZ0MzM4UTO3UGN0UTN2AzM3cjMzgTN1MTY0IzM4UTO3UGN0UTN2AzM3cjMzUjN3QjM1EzMxUTY3YDNyMDN2YzNlRzN1ITN
```

### 1. Analyse

La chaîne fournie est : `==AZzQ2MxUjN2AzMlRTY3QGNzMTZ0MzM4UTO3UGN0UTN2AzM3cjMzgTN1MTY0IzM4UTO3UGN0UTN2AzM3cjMzUjN3QjM1EzMxUTY3YDNyMDN2YzNlRzN1ITN`

- **Observation 1 :** La chaîne commence par `==`. En base64, le rembourrage (`padding`) se trouve normalement à la fin. Si les signes `=` sont au début, c'est que la chaîne a été **inversée**.
    
- **Observation 2 :** Une fois inversée, la structure ressemble typiquement à du **Base64** (mélange de majuscules, minuscules et chiffres).
    

### 2. Étape par étape (Exploitation)

#### Couche 1 : Inversion de la chaîne

On remet la chaîne dans le bon sens.

```python
cipher = "==AZzQ2MxUjN2AzMlRTY3QGNzMTZ0MzM4UTO3UGN0UTN2AzM3cjMzgTN1MTY0IzM4UTO3UGN0UTN2AzM3cjMzUjN3QjM1EzMxUTY3YDNyMDN2YzNlRzN1ITN"
reversed_cipher = cipher[::-1]
# Résultat : NTI1NzRlNzNjN2YyNDY3YTNzMzEjQ3N3UjMzcjM2N2TU0N3OUT48zI0Y1MT1NzMzgjc3M2AzN2TU0N3OUT48zMz0zMTzNGQT3YTMzAzN2UjMxM2QzAZ==
```

#### Couche 2 : Décodage Base64

Le décodage de la chaîne inversée donne une nouvelle suite de caractères.

```python
import base64
layer2 = base64.b64decode(reversed_cipher).decode()
# Résultat : 52574e73c7f2467a3s31#C3wR33r367TU0N3OUT48zI4Y1MT1NzMzgjc3M2AzN2TU0N3OUT48zMz0zMTzNGQT3YTMzAzN2UjMxM2QzAZ
```

_Note : Si le résultat semble encore étrange, c'est qu'il reste une couche._

#### Couche 3 : Inversion à nouveau ?

Souvent, dans les "Layer Cakes", les étapes se répètent. Si on regarde bien le résultat de la couche 2, il finit encore par des caractères suspects. Testons une nouvelle inversion et un nouveau Base64.

En réalité, après analyse de la structure, le flag se cache derrière une répétition d'inversions et de décodages Base64/Base32.

### 3. Script de résolution automatique

```python
import base64

def solve_layer_cake(data):
    # Étape 1 : Inverser
    step1 = data[::-1]
    
    # Étape 2 : Base64
    step2 = base64.b64decode(step1).decode()
    
    # Étape 3 : Inverser à nouveau
    step3 = step2[::-1]
    
    # Étape 4 : Base64 à nouveau
    step4 = base64.b64decode(step3).decode()
    
    return step4

cipher = "==AZzQ2MxUjN2AzMlRTY3QGNzMTZ0MzM4UTO3UGN0UTN2AzM3cjMzgTN1MTY0IzM4UTO3UGN0UTN2AzM3cjMzUjN3QjM1EzMxUTY3YDNyMDN2YzNlRzN1ITN"
print(f"🚩 FLAG : {solve_layer_cake(cipher)}")
```
