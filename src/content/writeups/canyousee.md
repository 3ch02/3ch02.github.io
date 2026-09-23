---
# Imported from Obsidian: CTF/picoCTF/Writeup CanYouSee.md
title: CanYouSee
category: Forensics
ctf: picoCTF
date: 2026-05-19
summary: On commence par identifier le format exact du fichier pour confirmer qu'il s'agit bien d'une image.
tags:
- base64
- exiftool
- file
- forensics
- picoctf
lang: fr
imported: true
---

### Métadonnées

- **Catégorie :** Forensics
    
- **Outils :** file exiftool base64
    
- **Flag :** `picoCTF{ME74D47A_HIDD3N_4dabddcb}`
    

###  Étape 1 : Analyse préliminaire de l'image

On commence par identifier le format exact du fichier pour confirmer qu'il s'agit bien d'une image.

```bash
file ukn_reality.jpg
```

#### Résultat :

```text
ukn_reality.jpg: JPEG image data, JFIF standard 1.01, resolution (DPI), density 72x72, segment length 16, baseline, precision 8, 4308x2875, components 3
```

Le fichier est une image JPEG standard de haute résolution ($4308 \times 2875$).

### 🕵️ Étape 2 : Inspection des métadonnées

On utilise `exiftool` pour inspecter l'intégralité des en-têtes et des tags EXIF/XMP intégrés dans l'image.

```bash
exiftool ukn_reality.jpg
```

#### Résultat :

Pasted image 20260519225533.png

L'analyse révèle un champ suspect contenant une chaîne encodée en **Base64** :

```text
cGljb0NURntNRTc0RDQ3QV9ISUREM05fNGRhYmRkY2J9Cg==
```

## 🔓 Étape 3 : Décodage de la charge utile

On passe la chaîne extraite dans la commande `base64 -d` pour récupérer le flag en clair.

```bash
echo "cGljb0NURntNRTc0RDQ3QV9ISUREM05fNGRhYmRkY2J9Cg==" | base64 -d
```

#### Résultat :

```text
picoCTF{ME74D47A_HIDD3N_4dabddcb}
```

### 🏁 Étape 4 : Capture du Flag

**Flag :** `picoCTF{ME74D47A_HIDD3N_4dabddcb}`
