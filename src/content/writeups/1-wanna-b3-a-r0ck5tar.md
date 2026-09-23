---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2019/1_wanna_b3_a_r0ck5tar.md
title: 1_wanna_b3_a_r0ck5tar
category: Reverse Engineering
ctf: picoCTF 2019
date: 2026-08-07
summary: 'Le challenge fournit un fichier contenant un texte ressemblant à des paroles de musique : Rocknroll is right Silence is wrong A guitar is a six-string Tommy''s been down Music is a…'
tags:
- picoctf-2019
- reverse-engineering
lang: fr
imported: true
---

Challenge: _1_wanna_b3_a_r0ck5tar_  
Catégorie: General Skills

### Description

Le challenge fournit un fichier contenant un texte ressemblant à des paroles de musique :

Rocknroll is right  
Silence is wrong  
A guitar is a six-string  
Tommy's been down  
Music is a billboard-burning razzmatazz!  
...

L'objectif est de retrouver le flag au format **picoCTF{}**.

---

## 1. Identification du langage

En observant le contenu du fichier, certaines instructions ressortent :

- `Shout`
    
- `Scream`
    
- `Say`
    
- `Listen to`
    
- `Break it down`
    

Ces mots-clés correspondent au **langage ésotérique Rockstar**.

Rockstar est un langage de programmation où le code ressemble à des **paroles de rock**.

---

## 2. Exécution du script

Pour comprendre ce que fait le programme, on peut l’exécuter avec un interpréteur Rockstar.

Installation :

git clone https://github.com/RockstarLang/rockstar.git  
cd rockstar

Puis exécution :

./rockstar fichier.rock

Le programme demande deux entrées :

Listen to the music  
Listen to the rhythm

On entre :

guitar  
nothing

---

## 3. Résultat du programme

Après l’exécution, le programme affiche :

66  
79  
78  
74  
79  
86  
73

---

## 4. Conversion ASCII

Ces nombres correspondent à des **codes ASCII décimaux**.

Conversion :

|Décimal|ASCII|
|---|---|
|66|B|
|79|O|
|78|N|
|74|J|
|79|O|
|86|V|
|73|I|

Cela donne :

BONJOVI

---

## 5. Flag

En respectant le format picoCTF :

picoCTF{BONJOVI}

---
