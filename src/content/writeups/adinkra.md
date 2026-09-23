---
# Imported from Obsidian: CTF/hackviser/EcowsCTF{}/📑 Writeup -Adinkra.md
# Draft: incomplete: only shows the data file, no analysis or flag
title: Adinkra
category: Cryptography
ctf: EcowsCTF (Hackviser)
date: 2026-08-07
tags:
- cryptography
- ecowsctf
lang: fr
draft: true
imported: true
---

##### Données:

Fichier scrolls.json

```
{
  "symbols": {
    "sankofa": {
      "meaning": "Return and get it",
      "method_hint": "The old ways encode simply",
      "ciphertext": "R28gYmFjayBhbmQgZmV0Y2ggaXQg4oCUIGJ1dCBub3QgaGVyZS4gVGhlIHBhc3QgaG9sZHMgbWFueSBzZWNyZXRzLCBub25lIG9mIHRoZW0gZmxhZ3Mu"
    },
    "gye_nyame": {
      "meaning": "Except for God",
      "method_hint": "Counted in halves of bytes",
      "ciphertext": "45786365707420666f7220476f642c20492066656172206e6f6e652e204275742074686973206973206e6f742074686520666c616720796f75207365656b2c2074726176656c65722e"
    },
    "dwennimmen": {
      "meaning": "Ram's horns \u2014 humility and strength",
      "method_hint": "A rotation older than Rome",
      "ciphertext": "RpbjnfPGS{tk3_al4z3_3kp3cg_t0q}"
    },
    "adinkrahene": {
      "meaning": "Chief of the Adinkra symbols",
      "method_hint": "Read it backwards before you unwrap",
      "ciphertext": "==gL0JXYlhGIlhGdgkncUBiLl52bgcmbvJ3dgUGa0BSZz9GajBSdvlFIuMXZoNGdhdHIzx2bi1WezBCbsFGIm9GImVWaoNGIlhGV"
    },
    "nyame_dua": {
      "meaning": "Altar of God",
      "method_hint": "A French diplomat's cipher, keyed by tradition",
      "ciphertext": "Cowfo sut qw pynrih auocl. Tkm nvkar rn Tyu doha ayk hool grv fldo gyuay."
    },
    "ese_ne_tekrema": {
      "meaning": "The teeth and the tongue",
      "method_hint": "A single mask covers every letter",
      "ciphertext": "07212d352331011604397131711d2c711d36712930712f761d367171362a3f"
    },
    "akoma": {
      "meaning": "The heart \u2014 patience and tolerance",
      "method_hint": "A block of patience, keyed by name",
      "ciphertext": "e29cde241a699057f58a50742bf7bcb584e979f2bbd7c4d3c0c74c7a8d43b55d9adea5faa3918a6a223315b4a43b67fd"
    },
    "funtunfunefu": {
      "meaning": "Siamese crocodiles \u2014 unity in diversity",
      "method_hint": "A fence with three rails",
      "ciphertext": "Tcoeh  m  ygo dhioof hw rcdlssaeoesoahbtte ih vrfo.Ti sntyu lgete.ooi rntcuhfteo s  rair"
    }
  }
}          

```
