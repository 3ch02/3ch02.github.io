---
# Imported from Obsidian: CTF/picoCTF/picoCTF_2026/Front_Running.md
# Draft: incomplete: attack described but never executed, no flag
title: Front_Running
category: Cryptography
ctf: picoCTF 2026
date: 2026-08-07
summary: Le contrat demande une solution (une chaîne de caractères) dont le hash keccak256 doit correspondre à targetHash.
tags:
- blockchain
- cryptography
- picoctf-2026
lang: fr
draft: true
imported: true
---

#### Catégorie :  Blockchain

Source : 
```
pragma solidity ^0.8.0;

contract MempoolChallenge {
    address public owner;
    address public studentAddress;
    string private flag; 
    bool public revealed;
    
    bytes32 public constant targetHash = 0xd781033f8619ec5d3ab5387d3ad9b87203acce775bc100b32bfbac009e596cd6;

    event FlagRevealed(string flag);

    constructor(string memory _flag, address _studentAddress) {
        owner = msg.sender;
        flag = _flag;
        studentAddress = _studentAddress; 
        revealed = false;
    }

    function solve(string memory solution) public {
        require(!revealed, "Challenge already solved!");
        require(keccak256(abi.encodePacked(solution)) == targetHash, "Incorrect solution!");

        require(msg.sender == studentAddress, "Only the student can claim the flag!");

        revealed = true;
        emit FlagRevealed(flag);
    }

    function getFlag() public view returns (string memory) {
        require(revealed, "Challenge not yet solved!");
        return flag;
    }
}
```

### Analyse de la vulnérabilité

Le contrat demande une `solution` (une chaîne de caractères) dont le hash `keccak256` doit correspondre à `targetHash`.

1. **Le problème de confidentialité :** En Solidity, le mot-clé `private` pour la variable `flag` empêche seulement les autres contrats de la lire, mais n'importe qui peut la voir en examinant le stockage de la blockchain.
    
2. **Le piège de la Mempool :** Lorsqu'un utilisateur (le `studentAddress`) envoie une transaction pour appeler `solve(solution)`, cette transaction reste dans la **Mempool** (la file d'attente des mineurs) avant d'être validée.
    
3. **Visibilité totale :** Pendant que la transaction attend, n'importe qui peut voir le contenu de l'input `solution` en clair.
    

###  Scénario d'attaque (Front-running)

Si tu n'es pas le `studentAddress`, tu ne peux pas appeler `solve`. Mais le challenge s'appelle "Mempool", ce qui suggère que quelqu'un (probablement un bot ou le créateur du challenge) va envoyer la solution.

**Voici comment tu récupères le flag :**

1. **Surveillance :** Tu surveilles les transactions entrantes vers l'adresse du contrat sur le nœud RPC.
    
2. **Interception :** Dès que tu vois une transaction appeler `solve(string solution)`, tu extrais l'argument `solution`.
    
3. **Consultation des logs :** Si la transaction du student est déjà passée, il suffit de regarder les **Events** (les journaux) du contrat. L'événement `FlagRevealed(flag)` contient le flag en clair !
