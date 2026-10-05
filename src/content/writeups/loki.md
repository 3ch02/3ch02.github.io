---
# Imported from Obsidian: CTF/BRCTF/Loki.md
title: Loki
category: Forensics
difficulty: Easy
ctf: brCTF 2026
competition: brctf-2026
date: 2026-10-01
summary: 'Énoncé : Named for the trickster god, this capture holds a short but deceptive burst of traffic — grabbed off the wire in the seconds before the analyst lost the connection…'
tags:
- brctf-2026
- forensics
points: 50
lang: fr
imported: true
---

> Compétition : **brCTF** — Challenge ID#2

## Informations

- **Catégorie :** Forensic
- **Difficulté :** Easy
- **Points :** 50
- **Auteur du write-up :** 3ch0
- **Flag :** `BRCTF{p4ck3t_h1d3_4nd_s33k}`

> **Énoncé :** Named for the trickster god, this capture holds a short but deceptive burst of traffic — grabbed off the wire in the seconds before the analyst lost the connection. Nothing here is quite what it appears. Follow the packets. Something is hiding in plain sight.

---

## 1. Analyse de la capture

Le fichier fourni est une capture réseau `Loki-challenge.pcap`. L'indice (« follow the packets », « hiding in plain sight ») oriente vers une donnée transmise en clair dans le trafic HTTP.

On ouvre la capture dans **Wireshark** et on extrait les objets HTTP échangés :

> **File → Export Objects → HTTP**

Plusieurs objets `upload` sont exportés (les requêtes POST capturées), ainsi que leurs réponses.

---

## 2. Lecture des données exfiltrées

On concatène le contenu des fichiers exportés :

```bash
cat u*
```

```text
chunk=1&data=BRCTF{p4ck3t_{"status":"ok","received":1}chunk=2&data=h1d3_4nd_{"status":"ok","received":2}chunk=3&data=s33k}
```

Les données sont exfiltrées **par morceaux** (`chunk`) à travers une série de requêtes POST. Chaque requête envoie un fragment dans le paramètre `data`, et le serveur répond par un accusé de réception JSON (`{"status":"ok","received":N}`).

On sépare les requêtes (le flag) des réponses (le bruit JSON) :

| Chunk | `data=` |
|-------|---------|
| 1 | `BRCTF{p4ck3t_` |
| 2 | `h1d3_4nd_` |
| 3 | `s33k}` |

---

## 3. Reconstruction du flag

Les fragments sont numérotés (`chunk=1/2/3`), l'ordre est donc explicite. On les concatène :

```
BRCTF{p4ck3t_ + h1d3_4nd_ + s33k}
```

**Flag :** `BRCTF{p4ck3t_h1d3_4nd_s33k}`

> Soit *« packet hide and seek »* — la donnée était bien « cachée à la vue de tous », dispersée sur plusieurs paquets.

---

## Récapitulatif de la chaîne d'exploitation

1. **`.pcap`** ouvert dans Wireshark.
2. **Export Objects → HTTP** → récupération des requêtes POST `upload`.
3. **`cat`** des objets → données exfiltrées en 3 `chunk` via le paramètre `data`.
4. Isoler les `data=` (ignorer les réponses JSON) et **concaténer dans l'ordre des chunks** → flag.

> **Concept clé :** l'exfiltration de données fragmentée sur plusieurs requêtes HTTP est une technique classique pour passer sous les radars (petits paquets d'apparence anodine). En analyse forensic réseau, suivre un flux HTTP et reconstituer la charge utile dispersée est un réflexe fondamental.
>
> **Astuce Wireshark :** le filtre `http.request.method == "POST"` isole directement les requêtes d'upload, et `Follow → HTTP Stream` permet de lire une conversation complète d'un seul coup.

---

***— 3ch0***
