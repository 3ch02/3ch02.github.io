---
# Imported from Obsidian: CTF/Writeup CTF Hackropole/Crypto/🚩 Smolekey.md
title: Smolekey
category: Cryptography
ctf: Hackropole (FCSC)
date: 2026-08-07
summary: On nous donne un texte chiffré c, un module n de 2048 bits (trop grand pour être factorisé) et un exposant public e=3. Le flag est converti en entier avant d'être chiffré.
tags:
- cryptography
- hackropole
- rsa
lang: fr
imported: true
---

RSA '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''#Smolekey

#### Code source : 

```
from gmpy2 import powmod as pow

from Crypto.PublicKey import RSA

class Smolkkey:

    def __init__(self):

        k = RSA.generate(2048, e = 3)

        self.pk = (k.n, k.e)

        self.sk = (k.n, k.d)
        
    def encrypt(self, m):

        n, e = self.pk

        c = pow(m, e, n)

        return int(c)

    def decrypt(self, c):

        n, d = self.sk

        m = pow(c, d, n)

        return int(m)

# Generate a key

E = Smolkkey()
# Encrypt the fag

flag = open("flag.txt", "rb").read()

flag = int.from_bytes(flag, "little")

c = E.encrypt(flag)

# Test decryption

assert flag == E.decrypt(c)
# Output public values

n, e = E.pk

print(f"{n = }")

print(f"{e = }")

print(f"{c = }")
```
#### Sortie:

```
n = 20828609401338794038836680655046788059251524928933537772275737490132096798900518851229365799426251400151127719543434160180496659560792762761336988343332946920310984844136554433346165529108260963140451576722579583104830933409454682160084747257400706214980238995436388944310800852033141986598424966358149711167942491331040747300866718813771865768701794983365111208518863175847678947437360554933091347604616653687980177405805542214635577758515398014710929022135522835744517328114492844837858920033569071591971676487452812830920525469634367387593309067794509735740140745616085618489218115494716811261406227449967579233657
e = 3
c = 6317668510138686569655374990729607736156413707292408158720036346854309670467296052918552527575331589363290061240725095262980389263184520673983411112154423282089471021996509038472493779143273789325774414352608726252566350689111876373836913240644190951995980896093509379920452743478551321978067299216590452459233562642920123055978471365092000347562228787318105538018723376505390423730687522026043802357456368003656219942603097205774742385485995835519133581552096067468551713114231926639878045212204590071768

```

### 1. Description du Challenge

On nous donne un texte chiffré c, un module n de 2048 bits (trop grand pour être factorisé) et un exposant public **e=3**. Le flag est converti en entier avant d'être chiffré.

### 2. Notions de Base

#### La faille de l'exposant faible

En RSA, l'opération de chiffrement est $c≡m^e(modn)$. Normalement, me est beaucoup plus grand que n, donc le résultat "rebondit" plusieurs fois autour du modulo (opération modulo).

Cependant, si m est petit (ce qui est souvent le cas d'un flag de 30-40 caractères) et que e est très petit (ici 3) : Il est possible que **me soit inférieur à n**.

Si me<n, alors l'opération modulo n n'a aucun effet ! L'équation devient une simple puissance mathématique :

$$
c=m^3
$$

### 3. Résolution (Analyse)

Si c=m3 dans les réels (sans modulo), alors pour retrouver m, il suffit de calculer la **racine cubique** de c.

Même si m3 est légèrement supérieur à n (par exemple m3 est entre n et 2n), on peut tester de calculer la racine cubique de c, c+n, c+2n, etc. Mais dans 99% des challenges de ce type, la racine cubique directe de c donne le résultat.

### 4. Exploitation (Python)

On ne peut pas utiliser `math.pow(c, 1/3)` car les nombres sont trop grands pour les nombres à virgule flottante de Python. On utilise une fonction de racine entière (comme `gmpy2.iroot` ou `pow` avec une fraction dans certaines bibliothèques).

```
import gmpy2
from Crypto.Util.number import long_to_bytes

# Valeurs du challenge
e = 3
n = 20828609401338794038836680655046788059251524928933537772275737490132096798900518851229365799426251400151127719543434160180496659560792762761336988343332946920310984844136554433346165529108260963140451576722579583104830933409454682160084747257400706214980238995436388944310800852033141986598424966358149711167942491331040747300866718813771865768701794983365111208518863175847678947437360554933091347604616653687980177405805542214635577758515398014710929022135522835744517328114492844837858920033569071591971676487452812830920525469634367387593309067794509735740140745616085618489218115494716811261406227449967579233657
c = 6317668510138686569655374990729607736156413707292408158720036346854309670467296052918552527575331589363290061240725095262980389263184520673983411112154423282089471021996509038472493779143273789325774414352608726252566350689111876373836913240644190951995980896093509379920452743478551321978067299216590452459233562642920123055978471365092000347562228787318105538018723376505390423730687522026043802357456368003656219942603097205774742385485995835519133581552096067468551713114231926639878045212204590071768

# ÉTAPE 1 : Calcul de la racine cubique entière
# iroot(x, 3) renvoie (racine, est_parfaite)
m, exact = gmpy2.iroot(c, 3)

if exact:
    print("[+] Racine exacte trouvée !")
    # ÉTAPE 2 : Conversion en texte
    # Attention : le code source utilise "little" endian pour le flag !
    flag = long_to_bytes(m)[::-1] # On inverse car "little" endian
    # Ou plus simplement si on suit strictement le code source :
    flag_correct = m.to_bytes((m.bit_length() + 7) // 8, byteorder='little')
    
    print(f"Le flag est : {flag_correct.decode()}")
else:
    print("[-] La racine n'est pas exacte, m^3 était peut-être > n.")

```
### Flag 🚩: 

```
FCSC{30f7c4b2fa7f0fb48bfbd9bbd413491c0a6da660764961b862fe38a83b4bc00f}
```
