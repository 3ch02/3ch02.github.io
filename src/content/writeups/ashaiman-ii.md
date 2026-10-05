---
# Imported from Obsidian: CTF/BRCTF/Ashaiman_II.md
title: Ashaiman II
category: Reverse Engineering
difficulty: Easy
ctf: brCTF 2026
competition: brctf-2026
date: 2026-10-01
summary: 'Énoncé : The crew learned from their first release. This version hardens what the original left exposed — the easy road is closed. You''ll need to go deeper than last time to reach…'
tags:
- brctf-2026
- reverse-engineering
points: 70
lang: fr
imported: true
---

> Compétition : **brCTF** — Challenge ID#6

## Informations

- **Catégorie :** Mobile (Android — reverse natif)
- **Difficulté :** Easy
- **Points :** 70
- **Auteur du write-up :** 3ch0
- **Flag :** `BRCTF{ash4iman2_l3dg3r_r00t_r3qu1r3d}`

> **Énoncé :** The crew learned from their first release. This version hardens what the original left exposed — the easy road is closed. You'll need to go deeper than last time to reach the same kind of secret. They patched the obvious. Can you find the way around?

---

## 1. Décompilation et constat

On décompile l'APK comme pour la v1 :

```bash
apktool d AshaimanII.apk
cd AshaimanII
```

Première différence notable : un dossier **`lib/`** apparaît (absent de la v1). En analysant le smali de `MainActivity`, on comprend le durcissement :

```text
# <clinit> charge une bibliothèque native
const-string v0, "ashaiman2"
invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

# la logique sensible est native
.method public final native writeLedger(Ljava/lang/String;)V
.end method
```

Le flag n'est **plus dans le bytecode** : il est traité dans `writeLedger`, une fonction **native** du fichier `libashaiman2.so`. C'est la « route facile » (grep sur le smali) qui a été fermée.

> L'app expose une interface JavaScript `BackRoom.enter()` qui appelle `writeLedger(filesDir)` → la lib écrit un fichier `ledger.dat`. En reverse **statique**, on n'exécute rien : on va lire directement le `.so`.

---

## 2. Analyse de la bibliothèque native

### `strings` ne suffit plus

```bash
find lib -name '*.so'
strings -n 6 lib/arm64-v8a/libashaiman2.so | grep -i brctf
```

```text
Java_com_brctf_ashaiman2_MainActivity_writeLedger
```

Seul le nom de la fonction JNI ressort — le flag est **construit à l'exécution**. On désassemble (archi x86_64, la plus lisible) :

```bash
objdump -d lib/x86_64/libashaiman2.so > disasm.txt
```

### La routine de déchiffrement

Le cœur de `writeLedger` est une boucle XOR :

```asm
88d:  lea -0x264(%rip),%rax   # 630  → données chiffrées (FLAG_ENC)
894:  lea -0x23b(%rip),%rcx   # 660  → clé (KEY)
...
8a0:  mov %r12,%rsi           ; i
8a3:  sub $0x19,%rsi          ; i - 25        (0x19 = 25 = longueur de la clé)
8ab:  cmovb %r12,%rsi         ; si i < 25, garde i   → indice = i % 25
8af:  movzbl (%rsi,%rcx,1),%esi ; KEY[i % 25]
8b3:  xor (%r12,%rax,1),%sil    ; ^ FLAG_ENC[i]
8b7:  mov %sil,(%rsp,%r12,1)    ; buf[i] = résultat
8bb:  cmp $0x25,%rdx            ; longueur == 0x25 (37) ?
```

Traduction : `flag[i] = FLAG_ENC[i] XOR KEY[i % len(KEY)]`, sur **37 octets** (`0x25`). Le résultat est ensuite écrit dans `ledger.dat` via `fwrite` (taille `0x25`).

---

## 3. Extraction des données (`.rodata`)

```bash
objdump -s -j .rodata lib/x86_64/libashaiman2.so
```

```text
 0610 25732f6c 65646765 722e6461 74007762  %s/ledger.dat.wb
 0630 03070d00 0f3e3e30 27792f22 333a6d13  .....>>0'y/"3:m.
 0640 29772322 612d1437 69712111 267a342a  )w#"a-.7iq!.&z4*
 0650 723d7e22 32000000 00000000 00000000  r=~"2...........
 0660 41554e54 49455f43 4f4d464f 52545f4c  AUNTIE_COMFORT_L
 0670 45444745 525f4b45 59                 EDGER_KEY
```

On identifie :
- **`0x610`** : chaîne de format `%s/ledger.dat` (chemin de sortie) + mode `wb`.
- **`0x630`** : `FLAG_ENC` — 37 octets chiffrés.
- **`0x660`** : `KEY` = `AUNTIE_COMFORT_LEDGER_KEY` (25 octets).

---

## 4. Déchiffrement du flag

On reproduit le XOR hors de l'app :

```python
key = b"AUNTIE_COMFORT_LEDGER_KEY"
enc = bytes.fromhex(
    "03070d000f3e3e3027792f22333a6d13"
    "29772322612d14376971211126 7a342a".replace(" ", "")
    + "723d7e2232"
)   # 37 octets lus en .rodata à 0x630

flag = bytes(enc[i] ^ key[i % len(key)] for i in range(len(enc)))
print(flag.decode())
```

```text
BRCTF{ash4iman2_l3dg3r_r00t_r3qu1r3d}
```

**Flag :** `BRCTF{ash4iman2_l3dg3r_r00t_r3qu1r3d}`

---

## Récapitulatif de la chaîne d'exploitation

1. **apktool** → présence d'un dossier `lib/` + `writeLedger` déclarée `native` → le secret est passé en code natif.
2. **`strings`** sur le `.so` → échec (flag construit à l'exécution).
3. **`objdump -d`** → routine XOR identifiée (`FLAG_ENC` ^ `KEY[i%25]`, 37 octets).
4. **`objdump -s -j .rodata`** → extraction de `FLAG_ENC` (0x630) et `KEY` (0x660).
5. **XOR en Python** → flag, sans jamais lancer l'app ni appeler `BackRoom.enter()`.

> **Concept clé :** passer un secret du bytecode Java au code **natif (JNI/`.so`)** complique légèrement l'analyse (il faut désassembler au lieu de lire du smali) mais ne protège rien : la clé et le texte chiffré restent dans le binaire livré (`.rodata`). Le reverse statique les récupère sans exécuter l'app. La leçon de la v1 reste valable — **aucun secret embarqué côté client n'est sûr**, qu'il soit en Java, en Kotlin ou en C.

---

***— 3ch0***
