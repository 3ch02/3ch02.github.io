---
title: "Réseau VoIP avec FreePBX / Asterisk"
summary: "Un lab de téléphonie d'entreprise : FreePBX et Asterisk derrière un pare-feu pfSense, clients softphone, messagerie vocale et messages en français, avec un manuel de déploiement qui couvre aussi le chiffrement des appels en TLS et SRTP."
---

## Contexte

Un projet personnel : monter la téléphonie interne d'une petite entreprise sur un réseau IP plutôt que sur des lignes téléphoniques classiques, et tout consigner dans un manuel de déploiement que quelqu'un d'autre pourrait suivre.

Le projet utilise un IP PBX hébergé sur site (FreePBX, l'interface web d'Asterisk) plutôt qu'une offre hébergée, de sorte que chaque composant est installé et configuré à la main.

## Organisation

1. **Notions de base** — ce qui se passe pendant un appel : SIP pour la signalisation (port 5060), RTP pour l'audio, les codecs, le plan de numérotation, et les protocoles autour (DHCP, DNS, NTP, et STUN/TURN/ICE quand il y a du NAT).
2. **Architecture** — un pare-feu pfSense qui fournit le LAN, le DHCP et l'accès à Internet ; un serveur FreePBX sur ce LAN ; des clients Windows avec le softphone Zoiper.
3. **Manuel de déploiement** — toutes les étapes, de la création des machines virtuelles au premier appel.

## Ce que j'ai fait

- Installation de **pfSense** avec une interface WAN et une interface LAN, et une plage DHCP pour le LAN.
- Installation de la distribution **FreePBX**, configuration initiale (compte administrateur, planification des mises à jour, pare-feu intégré) et placement du serveur sur le LAN de pfSense.
- Création des **extensions PJSIP** pour chaque utilisateur, avec un secret, un identifiant d'appelant et une messagerie vocale optionnelle.
- Enregistrement des softphones **Zoiper** sur les postes clients et appels entre extensions.
- Configuration de la **messagerie vocale** par extension, de la durée de sonnerie avant renvoi vers la messagerie, et des codes de fonction pour écouter les messages.
- Installation des **messages vocaux en français** avec `fwconsole` et choix du français comme langue par défaut, pour tout le système ou par extension.

## Sécurisation des appels

Par défaut, SIP et RTP ne sont pas chiffrés : n'importe qui sur le chemin peut lire la signalisation et écouter l'audio. Le manuel couvre :

- des **secrets forts et aléatoires** pour chaque extension ;
- **TLS pour la signalisation** (SIP sur TLS, port 5061) avec un certificat géré dans FreePBX ;
- **SRTP pour l'audio**, activé par extension, avec TLS comme seul transport autorisé ;
- **Fail2ban**, intégré à FreePBX, pour bannir les adresses après des échecs d'enregistrement répétés.

## Ce que j'ai appris

- Un appel téléphonique, ce sont deux flux distincts — la signalisation et le média — et chacun doit être sécurisé séparément.
- Les softphones doivent être sur le même réseau que le PBX pour s'enregistrer : un problème de téléphonie est souvent d'abord un problème de réseau.
- La plupart des fonctions de sécurité existent mais sont désactivées par défaut : le chiffrement doit être activé explicitement, extension par extension.

## Pas encore fait

Le trunk SIP entre deux sites (appels entre deux entreprises sur des réseaux différents) est prévu dans le manuel mais pas encore documenté.
