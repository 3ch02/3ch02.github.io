---
# Imported from Obsidian: CTF/Writeup CTF Hackropole/Crypto/🚩 Rien à signaler.md
title: Rien à signaler
category: Cryptography
ctf: Hackropole (FCSC)
date: 2026-08-07
summary: 'Le challenge nous fournit un script de génération de clés RSA et un fichier de sortie contenant trois valeurs : - n (le module) : le produit de deux nombres premiers p et q. - e…'
tags:
- cryptography
- factordb
- hackropole
- rsa
lang: fr
imported: true
---

##### Code Source : 

```
import json

from Crypto.Util.number import getPrime, bytes_to_long

def keygen(n = 1024):

    p = getPrime(n)

    q = getPrime(n)

    n = p * q

    e = 2 ** 16 + 1

    d = pow(e, -1, (p - 1) * (q - 1))

    sk = (d, n)

    pk = (e, n)

    return pk, sk

# Read the flag as an integer

m = bytes_to_long(open("flag.txt", "rb").read())

# Generate RSA keys

sk, pk = keygen()

# Encrypt the flag

c = pow(m, pk[0], pk[1])

# Output public key and ciphertext

d = {

    "e": pk[0],

    "n": pk[1],

    "c": c,

}

print(json.dumps(d, indent = 4))
```
##### Output : 

```
{
    "e": 14939086586092777407540803168471412724086958884607893995687327163153290580760558837291728666456222816453459253012875608081140912518401828609726644228963594136502689596910372270878975142615041204855876795840250744447608791110019817832312337476046798491861483950133453478764973611286365531244274907864964200118887980416350639882907479248120503190137345205402154450552803826178574159801186219948543406588724442253188994068292704744044422267282898105644719291000793491804938648328829611223993162601906075018324472156338267348355427156047595434154590931416765750047893661286247274247632521858558403416012123883148428323057,
    "n": 15796942747309728499758004731551695370913663306666035509299434642801916886496898004446545897149657535285268305926374338100837909963511256277964036962044387829939281166102731090331978991280163210213940391251452338553405036351243486418991475381065523778778374159216111211039724992140348798301914302441933569705494577465736752087544176074475722982600742085989140379907623574747713824460161103249270448563714176784913386788071348191510218812659925461534747629228752452045853041012162619056264262054391967199115369336548943331022933845667724296738334370747384492830658154258526863726939357154899976616849634493499797766299,
    "c": 8974868290281688737233990325600894780715849339628541493919631966007477856153771121147897587192029426714635875587384109624607194486211852465796766441066196469272988076202321557112300294463883797708163984188107199926745938577562219282934551167072277621808474131345695591468145868455419473050498493285402336637848596791275101533878984692539165395918338275186762268105380646876795842765910627488934075701761752437069042340873474933889573307306539126206460702731582652544213958040586038088129224761895431978602343177304095553828090049657631935349611981192723124744317395844933142968117051307548448128268941861109853064071
}

```
### 1. Description du Challenge

Le challenge nous fournit un script de génération de clés **RSA** et un fichier de sortie contenant trois valeurs :

- **n (le module)** : le produit de deux nombres premiers p et q.
    
- **e (l'exposant public)** : utilisé pour chiffrer le message.
    
- **c (le ciphertext)** : le flag chiffré.
    

L'objectif est de retrouver le message clair m (le flag) à partir de ces informations publiques.

### 2. Notions de Base

#### A. Le fonctionnement de RSA

RSA repose sur la difficulté mathématique de factoriser de grands nombres. La sécurité est garantie tant que p et q restent secrets.

- **Chiffrement** : c≡me(modn)
    
- **Déchiffrement** : m≡cd(modn)
    

#### B. La clé privée d

Pour déchiffrer, il nous faut l'exposant privé d. Il se calcule comme l'inverse modulaire de e modulo ϕ(n) :

d≡e−1(modϕ(n))

où ϕ(n)=(p−1)(q−1). Sans p et q, il est impossible de calculer ϕ(n), et donc impossible de trouver d.

### 3. Analyse et Faille

Dans ce challenge, bien que le module n soit de taille standard (2048 bits), il présente une vulnérabilité : il n'est pas "robuste". En utilisant **FactorDB**, une base de données en ligne recensant les factorisations de grands nombres, on s'aperçoit que ce module n a déjà été cassé ou généré avec des paramètres faibles. Une fois p et q obtenus, la barrière mathématique s'effondre.

### 4. Résolution (Exploitation)

Le processus de résolution suit ces étapes mathématiques :

1. **Récupération de p et q** : On soumet n à FactorDB pour obtenir ses deux facteurs premiers.
    
2. **Calcul de l'indicatrice d'Euler** : On calcule ϕ(n)=(p−1)×(q−1).
    
3. **Calcul de l'inverse modulaire** : On utilise l'algorithme d'Euclide étendu pour trouver d.
    
4. **Déchiffrement** : On calcule m=cd(modn) et on convertit le grand entier résultant en texte (bytes).
    

### 5. Script de récupération (Python)

Nous allons utiliser les ressources en ligne comme Factordb pour decomposer le n 

Decomposition : 

```
p=123774417702849779312531334881851636990928569157979444668342920686879229988179542625109923321541168858147049730901300731275805429676592086136842766601094802645747415634382864868330275424719996690187808513194133340319198792709928055006562921128446981448050421904500081126023332293549159550653499220035654850037

q=127626879935998439018255028985697193942589780562791574726209816727180479933107423079101161635647567093773224916512088332633663082377968679059882206615540396948909004068177859470665925423419454479434338523346080647885805634036707113844627206947980446603350465586515930163485120588151583714439276986170287886927
```

```text
from Crypto.Util.number import long_to_bytes, inverse

# 1. Données du challenge
n = 157969...299
e = 149390...057
c = 897486...071

# 2. Facteurs trouvés via FactorDB
p = 123774...037
q = 127626...927

# 3. Calculs RSA
phi = (p - 1) * (q - 1)
d = inverse(e, phi) # Calcul de l'inverse modulaire
m = pow(c, d, n)    # Déchiffrement : c^d mod n

# 4. Résultat
print(f"Flag : {long_to_bytes(m).decode()}")
```
### Flag 🚩: 

```
FCSC{7264bd2db7fae77e0c4e2445e45ed89fbe98f7c1bc8e7796111e32654f1ad1f0}
```
