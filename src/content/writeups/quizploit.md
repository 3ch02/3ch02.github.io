---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/Quizploit.md
# Draft: incomplete: stops before the exploit script and flag
title: Quizploit
category: Pwn
ctf: picoCTF 2026
date: 2026-08-07
summary: 'Le problème saute aux yeux dans la fonction vuln() :'
tags:
- buffer-over-f
- file
- picoctf-2026
- pwn
lang: fr
draft: true
imported: true
---

Source :
```
#include <stdio.h>

#include <stdlib.h>

  

/*

This is not the challenge, just a template to answer the questions.

To get the flag, answer all the questions.

There are no bugs in the quiz.

There are 0xD questions in total.

  

*/

  

void win(){

        system("cat flag.txt");

}

  

void vuln(){

        char buffer[0x15] = {0};

        fprintf(stdout, "\nEnter payload: ");

        fgets(buffer, 0x90, stdin);

}

  

void main(){

        vuln();

}
```

### identifier le type d'exe

```
file vuln        
vuln: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=19251d430d5dd4b44a3e8489a8c76f1894676f7d, for GNU/Linux 3.2.0, not stripped

```

Explication:

un exécutable linux , système 64bits

### Analyse de la vulnérabilité

Le problème saute aux yeux dans la fonction `vuln()` :

```c
void vuln(){
    char buffer[0x15] = {0}; // On réserve 21 octets (0x15)
    fprintf(stdout, "\nEnter payload: ");
    fgets(buffer, 0x90, stdin); // On lit jusqu'à 144 octets (0x90) !
}
```

Le programme alloue **21 octets**, mais `fgets` accepte d'en lire **144**. On peut donc déborder du tampon (Buffer OverFlow), écraser les données adjacentes sur la pile, et surtout écraser l'**adresse de retour** (Saved Return Address).
###  L'objectif : Redirection vers `win()`

Puisque la fonction `win()` existe et qu'elle affiche le flag, notre but est d'écraser l'adresse de retour de `vuln()` pour qu'elle pointe vers l'adresse de `win()`

### Identifier les protections 

On utilise checksec 

Commande 

```
checksec vuln 
```

Sortie
```
checksec --file=./vuln
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols         FORTIFY Fortified     Fortifiable     FILE
Partial RELRO   No canary found   NX enabled    No PIE          No RPATH   No RUNPATH   40 Symbols        No    0    1./vuln

```

Protection NX

Explication

NX 

Identifier l'adresse de la fonction win 
```
└─$ objdump -d vuln | grep "<win>:"

```
