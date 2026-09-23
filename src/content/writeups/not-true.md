---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/NOt true.md
title: NOt true
category: Cryptography
ctf: picoCTF 2026
date: 2026-08-07
summary: print("[] Réduction LLL...") L = M.LLL()
tags:
- cryptography
- picoctf-2026
lang: fr
imported: true
---

Code : 
```
from random import randint

from sage.all import *

  

N = 48

p = 3

q = 509

  

R = PolynomialRing(ZZ, 'x')

x = R.gen()

R_modq = PolynomialRing(Integers(q), 'x').quotient(x**N - 1, 'xbar')

R_modp = PolynomialRing(Integers(p), 'x').quotient(x**N - 1, 'xbar')

  

def gen_poly():

    return R([randint(-1,1) for _ in range(N)])

  

def gen_msg(text):

    binary_str = ''.join(format(ord(char), '08b') for char in text)

    padding_length = (N - (len(binary_str) % N)) % N

    binary_str += '0' * padding_length

    chunks = [binary_str[i:i+N] for i in range(0, len(binary_str), N)]

    polynomials = [

        R([int(bit) for bit in chunk])

        for chunk in chunks

    ]

    return polynomials

  

def encrypt(h, m):

    r = gen_poly()

    return R_modq(p*(h*r) + m)

  

def generate_keys():

    while True:

        # Random ternary polynomials f and g

        f = gen_poly()

        g = gen_poly()

        # Check if f is invertible modulo p and q

        try:

            f_p_inv = R_modp(f)**-1

            f_q_inv = R_modq(f)**-1

            break

        except:

            continue

  

    h = R_modq(p*(f_q_inv*g))

    private_key = (f, g, f_p_inv, f_q_inv)

    public_key = h

    return public_key, private_key

  

with open("flag.txt", "r") as f:

    flag = f.read().strip()

  

public_key, private_key = generate_keys()

print(f"h = {public_key.list()}")

  

ciphertext = []

encoded = gen_msg(flag)

for part in encoded:

    ciphertext.append(encrypt(public_key, part))

ct = [c.list() for c in ciphertext]

print(f"ct = {ct}")

  

with open("public.txt", "w") as f:

    f.write(f"N = {N}\n")

    f.write(f"p = {p}\n")

    f.write(f"q = {q}\n")

    f.write(f"h = {public_key.list()}\n")

    f.write(f"ct = {ct}\n")
```

sortie : 

```
N = 48
p = 3
q = 509
h = [311, 273, 153, 392, 105, 426, 45, 159, 421, 30, 404, 38, 313, 480, 37, 195, 82, 382, 236, 230, 340, 66, 199, 121, 279, 273, 271, 22, 270, 227, 26, 253, 213, 408, 323, 263, 283, 168, 88, 164, 383, 247, 5, 313, 150, 170, 89, 235]
ct = [[231, 6, 348, 205, 488, 156, 57, 466, 295, 240, 87, 285, 165, 208, 343, 426, 410, 36, 190, 110, 187, 28, 237, 262, 508, 111, 451, 311, 128, 449, 476, 434, 159, 98, 488, 399, 314, 499, 427, 325, 299, 250, 457, 8, 64, 423, 210, 271], [177, 217, 101, 452, 354, 388, 158, 437, 435, 484, 452, 0, 142, 47, 66, 229, 131, 325, 423, 394, 337, 356, 8, 56, 197, 12, 456, 186, 430, 286, 68, 106, 271, 257, 351, 76, 508, 383, 360, 318, 426, 113, 84, 451, 436, 206, 63, 151], [212, 400, 162, 356, 300, 494, 60, 333, 230, 477, 484, 174, 26, 65, 175, 107, 158, 496, 168, 318, 350, 497, 261, 281, 388, 193, 16, 294, 180, 390, 116, 252, 169, 411, 69, 257, 496, 302, 86, 320, 405, 436, 156, 462, 219, 486, 349, 494], [275, 256, 300, 153, 467, 412, 380, 353, 435, 232, 450, 490, 136, 136, 86, 326, 93, 19, 208, 89, 474, 163, 70, 30, 56, 261, 145, 499, 49, 403, 331, 315, 49, 472, 66, 156, 26, 481, 412, 258, 503, 44, 275, 222, 164, 356, 212, 57], [354, 310, 412, 400, 67, 433, 363, 209, 80, 244, 473, 239, 409, 446, 356, 193, 191, 15, 443, 79, 371, 63, 444, 285, 316, 488, 176, 44, 393, 401, 504, 106, 111, 5, 491, 208, 279, 403, 83, 226, 271, 244, 358, 473, 436, 208, 457, 81], [246, 291, 361, 460, 247, 229, 400, 3, 38, 189, 460, 347, 384, 327, 246, 33, 7, 141, 135, 182, 496, 160, 259, 424, 496, 137, 28, 6, 169, 97, 251, 269, 316, 68, 360, 426, 22, 150, 498, 398, 270, 130, 447, 36, 500, 32, 48, 114]]

```

scrpipt : 
```
from sage.all import *

# Paramètres
N = 48
p = 3
q = 509
h_list = [311, 273, 153, 392, 105, 426, 45, 159, 421, 30, 404, 38, 313, 480, 37, 195, 82, 382, 236, 230, 340, 66, 199, 121, 279, 273, 271, 22, 270, 227, 26, 253, 213, 408, 323, 263, 283, 168, 88, 164, 383, 247, 5, 313, 150, 170, 89, 235]
ct_list = [[231, 6, 348, 205, 488, 156, 57, 466, 295, 240, 87, 285, 165, 208, 343, 426, 410, 36, 190, 110, 187, 28, 237, 262, 508, 111, 451, 311, 128, 449, 476, 434, 159, 98, 488, 399, 314, 499, 427, 325, 299, 250, 457, 8, 64, 423, 210, 271], [177, 217, 101, 452, 354, 388, 158, 437, 435, 484, 452, 0, 142, 47, 66, 229, 131, 325, 423, 394, 337, 356, 8, 56, 197, 12, 456, 186, 430, 286, 68, 106, 271, 257, 351, 76, 508, 383, 360, 318, 426, 113, 84, 451, 436, 206, 63, 151], [212, 400, 162, 356, 300, 494, 60, 333, 230, 477, 484, 174, 26, 65, 175, 107, 158, 496, 168, 318, 350, 497, 261, 281, 388, 193, 16, 294, 180, 390, 116, 252, 169, 411, 69, 257, 496, 302, 86, 320, 405, 436, 156, 462, 219, 486, 349, 494], [275, 256, 300, 153, 467, 412, 380, 353, 435, 232, 450, 490, 136, 136, 86, 326, 93, 19, 208, 89, 474, 163, 70, 30, 56, 261, 145, 499, 49, 403, 331, 315, 49, 472, 66, 156, 26, 481, 412, 258, 503, 44, 275, 222, 164, 356, 212, 57], [354, 310, 412, 400, 67, 433, 363, 209, 80, 244, 473, 239, 409, 446, 356, 193, 191, 15, 443, 79, 371, 63, 444, 285, 316, 488, 176, 44, 393, 401, 504, 106, 111, 5, 491, 208, 279, 403, 83, 226, 271, 244, 358, 473, 436, 208, 457, 81], [246, 291, 361, 460, 247, 229, 400, 3, 38, 189, 460, 347, 384, 327, 246, 33, 7, 141, 135, 182, 496, 160, 259, 424, 496, 137, 28, 6, 169, 97, 251, 269, 316, 68, 360, 426, 22, 150, 498, 398, 270, 130, 447, 36, 500, 32, 48, 114]]

R = PolynomialRing(ZZ, 'x')
x = R.gen()

# Construction du réseau
M = Matrix(ZZ, 2*N, 2*N)
for i in range(N):
    M[i, i] = 1
    for j in range(N):
        M[i, j+N] = h_list[(j-i) % N]
    M[i+N, i+N] = q

print("[*] Réduction LLL...")
L = M.LLL()

R_modp = PolynomialRing(Integers(p), 'x').quotient(x**N - 1)
R_modq = PolynomialRing(Integers(q), 'x').quotient(x**N - 1)

f = None
f_p_inv = None

# On itère sur les lignes (rows) de la matrice réduite L
for row in L.rows():
    f_coeffs = list(row[:N])
    try:
        f_poly_p = R_modp(f_coeffs)
        f_p_inv = f_poly_p**-1
        f = R(f_coeffs)
        print(f"[+] f trouvé : {f_coeffs[:5]}...") # Affiche le début pour vérification
        break
    except (ArithmeticError, ZeroDivisionError):
        continue

if f is None:
    print("[!] Impossible de trouver une clé f inversible dans la base LLL.")
else:
    full_binary = ""
    for c_list in ct_list:
        c = R_modq(c_list)
        # On repasse en R(ZZ) pour le calcul f*c afin d'éviter les erreurs de types de quotients
        a_poly = R(f.list()) * R(c.list())
        # Réduction manuelle modulo x^N - 1
        a_coeffs_raw = a_poly.list()
        a_coeffs_reduced = [0] * N
        for idx, val in enumerate(a_coeffs_raw):
            a_coeffs_reduced[idx % N] += val
            
        # Centrage des coefficients mod q
        a_coeffs = [(int(coeff) + q//2) % q - q//2 for coeff in a_coeffs_reduced]
        
        # m = f_p_inv * a mod p
        m = f_p_inv * R_modp(a_coeffs)
        
        bits = m.list()
        bits += [0] * (N - len(bits))
        full_binary += "".join(map(str, bits))

    flag = ""
    for i in range(0, len(full_binary), 8):
        byte = full_binary[i:i+8]
        if len(byte) == 8:
            flag += chr(int(byte, 2))
    print(f"\n[+] Flag : {flag}")```

Sortie Sag : 
[*] Réduction LLL...
[+] f trouvé : [0, -1, 1, 1, 0]...

[+] Flag : picoCTF{th4ts_s0_N0t_TRU3_38a83032}

Flag : 
picoCTF{th4ts_s0_N0t_TRU3_38a83032}
