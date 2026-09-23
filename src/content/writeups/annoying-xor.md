---
# Imported from Obsidian: CTF/hackviser/EcowsCTF{}/Annoying XOR.md
# Draft: incomplete: stops after a partial Ghidra dump, no flag
title: Annoying XOR
category: Cryptography
ctf: EcowsCTF (Hackviser)
date: 2026-08-07
tags:
- cryptography
- ecowsctf
lang: fr
draft: true
imported: true
---

```bash
file annoying-xor  
```

Résultat 

```
annoying-xor: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=5eaa3e29ba0b5f5eb198426a6ca97e414dd14bfb, not stripped
```

Recherche de chaine avec strings 

```
strings annoying-xor
```

Localiser main avec ghidra
main.c

```c

undefined4 main(int param_1,undefined8 *param_2)

{
  char cVar1;
  int iVar2;
  ulong uVar3;
  undefined4 uVar4;
  byte *pbVar5;
  char *pcVar6;
  byte bVar7;
  
  bVar7 = 0;
  if (param_1 != 2) {
    __fprintf_chk(stderr,1,"Usage: %s <flag>\n",*param_2);
                   
    exit(1);
  }
  srandom(0xf04d7e8c);
  pbVar5 = &flag;
  do {
    uVar3 = 0xffffffffffffffff;
    pcVar6 = &flag;
    do {
      if (uVar3 == 0) break;
      uVar3 = uVar3 - 1;
      cVar1 = *pcVar6;
      pcVar6 = pcVar6 + (ulong)bVar7 * -2 + 1;
    } while (cVar1 != '\0');
    if ((byte *)(~uVar3 - 1) <= pbVar5 + -0x301010) {
      iVar2 = strcmp(&flag,(char *)param_2[1]);
      if (iVar2 == 0) {
        puts("Right!");
        uVar4 = 0;
      }
      else {
        puts("Wrong!");
        uVar4 = 10;
      }
      return uVar4;
    }
    uVar3 = random();
    *pbVar5 = *pbVar5 ^ (byte)((long)uVar3 >>
                              (((char)uVar3 + (char)((uVar3 & 0xff) / 3) * -3) * '\b' & 0x3fU));
    pbVar5 = pbVar5 + 1;
  } while( true );
}
```
