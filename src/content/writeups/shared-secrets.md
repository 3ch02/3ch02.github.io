---
# Imported from Obsidian: CTF/picoCTF/Writeup -  Shared Secrets.md
title: Shared Secrets
category: Cryptography
ctf: picoCTF
date: 2026-08-07
summary: Avant de parler de l'attaque, il est essentiel de comprendre comment ce protocole est censé fonctionner lorsqu'il est sécurisé.
tags:
- cryptography
- picoctf
lang: fr
imported: true
---

---
tags:
  - ctf/picoCTF
  - crypto/diffie-hellman
  - writeup
  - attack/implementation-flaw
---

**Flag :** `picoCTF{dh_s3cr3t_2ca97bc6}`

---

## 📌 1. Comprendre le Protocole : L'Échange de clés Diffie-Hellman (DH)

Avant de parler de l'attaque, il est essentiel de comprendre comment ce protocole est censé fonctionner lorsqu'il est sécurisé. 

L'objectif de Diffie-Hellman est de permettre à deux parties (ici, le Serveur et le Client) de se mettre d'accord sur un **secret partagé** via un canal non sécurisé, sans qu'un espion (l'attaquant) ne puisse le découvrir.

### Les étapes théoriques :
1. **Paramètres Publics :** Tout le monde connaît le nombre premier $p$ et le générateur $g$.
2. **Génération des clés privées :**
   * Le serveur choisit un entier secret $a$.
   * Le client choisit un entier secret $b$.
3. **Calcul des clés publiques :**
   * Le serveur calcule sa clé publique : $A = g^a \pmod p$
   * Le client calcule sa clé publique : $B = g^b \pmod p$
   * Ils s'échangent $A$ et $B$.
4. **Calcul du secret partagé :**
   * Le serveur calcule : $\text{shared} = B^a \pmod p$
   * Le client calcule : $\text{shared} = A^b \pmod p$
   
Grâce aux propriétés des puissances, les deux calculs donnent le même résultat : 
$$\text{shared} = (g^b)^a = (g^a)^b = g^{ab} \pmod p$$

---

##  2. L'Analyse de la Vulnérabilité : "Broken Implementation"

La sécurité de Diffie-Hellman repose entièrement sur le **Problème du Logarithme Discret (DLP)** : si un attaquant intercepte $g$, $p$, $A$ et $B$, il lui est mathématiquement impossible (avec de grands nombres) de retrouver les clés privées $a$ ou $b$.

**Code source**
```
from Crypto.Util.number import getPrime
from random import randint

# Public parameters
g = 2
p = getPrime(1048)

# Server's secret
a = randint(2, p-2)
A = pow(g, a, p)

# Client secret
b = '???'  

B = pow(g, b, p)

# Shared key
shared = pow(A, b, p)

# Encrypt flag
flag = b"picoCTF{...}"
enc = bytes([x ^ (shared % 256) for x in flag])

# Write challenge info
with open("file.txt", "w") as f:
    f.write(f"g = {g}\n")
    f.write(f"p = {p}\n")
    f.write(f"A = {A}\n")
    f.write(f"b = {b} \n")
    f.write(f"enc = {enc.hex()}\n")

```
### La faille ici :
L'attaque n'est pas mathématique, elle vient d'une **erreur d'implémentation flagrante du développeur**. Dans le fichier `message.txt` généré par le serveur, on retrouve cette ligne :
```python
f.write(f"b = {b} \n")
````

Le script divulgue directement **la clé privée $b$** du client.

## ⚔️ 3. Type d'Attaque : Le "Leak" de Clé Privée (Exfiltration de Secret)

Ce challenge n'appartient pas aux attaques cryptographiques complexes sur DH (comme l'attaque par petits sous-groupes ou le solveur d'index de Pohlig-Hellman). C'est une catégorie d'attaque orientée **Audit de code / Mauvaise configuration**.

À partir du moment où l'exposant secret $b$ est public, l'attaquant peut se substituer entièrement au client et exécuter la phase 4 du protocole :

$$\text{shared} = A^b \pmod p$$

Une fois le secret partagé calculé, il suffit de reproduire le flux de chiffrement (XOR avec le dernier octet du secret : `shared % 256`) pour inverser le chiffrement et retrouver le flag.

## 💻 4. Script d'Exploitation (Python)

```python
from Crypto.Util.number import long_to_bytes

# 1. Données fournies par le challenge
g = 2
p = 2945889223405899717437265251282889237686559573793157647835455871476745956825847090445335342413729199710024517687795349222366793319464673474527753463753560669805788150720285098020316190185259452659032001767221627644083179050716771774653499262295349651622216757390737536877329949121301682270023803436930269461263978639
A = 1925392662772808546939197421118358205835520399582911779574770525906575552129444284907344977079741952528900583391955529233006061528791931270897227227254591808926119750957182872183751567174771844545921835638466409933832100662725178402589611293977249134084715246989581107542140315824588288700914611275677717166278179527
b = 2348305787882664061354385580996892615192009596530928729579256657766736150757668411620580993437412955274875319957944656861692190542466234368849284411648743737962591564126026461856185033358244834877514472038765378285629252363025584537954693907723097828741999592403090405128852699175959302315102762126018235816973308999
enc_hex = "6178727e5245576a75794e6222726322654e23727028267372276c"

# 2. Reconstitution mathématique du secret partagé
shared = pow(A, b, p)

# 3. Récupération du masque XOR (shared modulo 256 pour obtenir 1 octet)
key = shared % 256

# 4. Opération XOR inverse sur le texte chiffré
enc_bytes = bytes.fromhex(enc_hex)
flag = bytes([x ^ key for x in enc_bytes])

print(f"[+] Flag trouvé : {flag.decode()}")
```

## 🧠 5. Méthodologie CTF : Comment réagir la prochaine fois ?

Si tu te retrouves face à un challenge Diffie-Hellman lors d'un prochain CTF, suis cette checklist mentale pour identifier l'attaque :

1. **Check les variables fournies :** Regarde toujours ce que l'énoncé te donne. Si tu vois passer un petit $a$ ou un petit $b$ au milieu des grosses clés publiques ($A, B$), ne cherche pas plus loin : c'est un leak de clé privée. Calcule immédiatement `pow(Public_Opposée, privee_connue, p)`.
    
2. **Analyse la taille de $p$ :** Si $p$ est petit (inférieur à 256 ou 512 bits), le problème du logarithme discret peut être résolu de force avec l'algorithme _Baby-step Giant-step_ ou via l'outil `SageMath` avec la fonction `.log()`.
    
3. **Vérifie la valeur de $g$ :** Si $g = 1$, $g = p-1$ ou si $g$ génère un groupe très petit, les résultats de $A$ ou $B$ deviennent triviaux à deviner.
