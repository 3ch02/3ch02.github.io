---
# Imported from Obsidian: La Page Fantôme – OSINT Medium (150 pts).md
# Draft: unknown source
title: La Page Fantôme – OSINT Medium
category: OSINT
difficulty: Medium
ctf: Unknown
date: 2026-09-25
summary: Le temps efface les pages, mais jamais totalement leurs traces. Quelque part, figée dans une capsule numérique, une version oubliée d'un savoir se cache encore. Cherche l'écho du…
tags:
- osint
points: 150
lang: fr
draft: true
imported: true
---

**CTF** : ESIG Tech Arena  
**Catégorie** : OSINT  
**Points** : 150  
**Flag** : `EthACTF{Eric_AGBODJAN_PRINCE-INFOGRALE_SARL}`

---

## Description

> Le temps efface les pages, mais jamais totalement leurs traces.  
> Quelque part, figée dans une capsule numérique, une version oubliée d'un savoir se cache encore.  
> Cherche l'écho du passé, remonte le fil d'un site qui n'existe plus tel qu'il était,  
> et découvre qui en gardait les clés de l'enseignement, et qui lui tendait la main dans l'ombre.  
> esig.tg (Ne pas attacker ce domaine)

**Format** : `EthACTF{Prénom_NOM-PARTENAIRE}`  
**Exemple** : `EthACTF{Abalo_KOSSI_MOUSSA-VUWULANCE_CORP}`

---

## Méthodologie

### 1. Cible identifiée
Le domaine mentionné est **esig.tg**.  
Interdiction d’attaquer le site live → on passe uniquement par les **archives**.

### 2. Wayback Machine

Recherche des snapshots de 2013-2015 (période où le site était encore dans sa forme « ancienne ») :

- Page d’accueil archivée  
- Articles d’actualité  
- Footer présent sur **toutes** les pages

### 3. Qui gardait les clés de l’enseignement ?

Article trouvé :
> **M. Eric AGBODJAN PRINCE, nommé Directeur des Études d’ESIG Global Success**

- Snapshot : https://web.archive.org/web/20150822081557/http://www.esig.tg/item/64-eric-agbodjan-de  
- Date de l’article : 24 septembre 2013  
- Il était auparavant Directeur des Études à l’IAEC.

→ **Eric AGBODJAN PRINCE** = celui qui « gardait les clés de l’enseignement ».

### 4. Qui lui tendait la main dans l’ombre ?

Sur **toutes** les pages archivées, le footer affiche systématiquement :
