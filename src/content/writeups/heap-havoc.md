---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/Heap Havoc.md
# Draft: incomplete: stops before the exploit payload and flag
title: Heap Havoc
category: Web
ctf: picoCTF 2026
date: 2026-08-07
summary: 'Description: Un programme apparemment inoffensif prend deux noms comme arguments, mais il y a un hic. En débordant le tampon d''entrée, vous pouvez écraser l''adresse de retour…'
tags:
- picoctf-2026
- web
lang: fr
draft: true
imported: true
---

Description:
Un programme apparemment inoffensif prend deux noms comme arguments, mais il y a un hic. En débordant le tampon d'entrée, vous pouvez écraser l'adresse de retour enregistrée et rediriger l'exécution vers une partie cachée du binaire qui imprime le drapeau. Vous pouvez télécharger le fichier du programme [ici](https://challenge-files.picoctf.net/c_foggy_cliff/2284b53768f69b22d640e88e37300cc2e1af2af063f710c0c10c2e38b555d3e4/vuln) et le [code](https://challenge-files.picoctf.net/c_foggy_cliff/2284b53768f69b22d640e88e37300cc2e1af2af063f710c0c10c2e38b555d3e4/vuln.c) source.

Des détails supplémentaires seront disponibles après le lancement de votre instance de déf

### Source: 
```
#include <stdlib.h>

#include <unistd.h>

#include <string.h>

#include <stdio.h>

#include <sys/types.h>

#include <time.h>

  

struct internet {

    int priority;

    char *name;

    void (*callback)();

};

  

void winner() {

    FILE *fp;

    char flag[256];

  

    fp = fopen("flag.txt", "r");

    if (fp == NULL) {

        perror("Error opening flag.txt");

        exit(1);

    }

  

    if (fgets(flag, sizeof(flag), fp) != NULL) {

        printf("FLAG: %s\n", flag);

    } else {

        printf("Error reading flag\n");

    }

  

    fclose(fp);

}

  

int main(int argc, char **argv) {

    struct internet *i1, *i2, *i3;

    printf("Enter two names separated by space:\n");

    fflush(stdout);  

    if (argc != 3) {

        printf("Usage: ./vuln <name1> <name2>\n", argv[0]);

        fflush(stdout);  

        return 1;

    }

  

i1 = malloc(sizeof(struct internet));

i1->priority = 1;

i1->name = malloc(8);

i1->callback = NULL;

  

i2 = malloc(sizeof(struct internet));

i2->priority = 2;

i2->name = malloc(8);

i2->callback = NULL;

  

strcpy(i1->name, argv[1]);  

strcpy(i2->name, argv[2]);

  

if (i1->callback) i1->callback();

if (i2->callback) i2->callback();

  

    printf("No winners this time, try again!\n");

}
```

### Payload 'automatisation :
