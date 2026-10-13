---
title: "Portail captif avec pfSense"
summary: "Projet scolaire de première année : un pare-feu pfSense qui oblige les utilisateurs d'un réseau à s'authentifier sur une page web personnalisée avant d'accéder à Internet, avec un manuel de déploiement pas à pas."
---

## Contexte

Mon projet scolaire (PPE) de première année : contrôler qui accède à Internet sur un réseau. Un utilisateur qui se connecte est redirigé vers une page de connexion et n'a aucun accès tant qu'il ne s'est pas authentifié.

## Conception

![Architecture cible : lien Internet, pare-feu pfSense, commutateur Cisco, VLAN 100 où s'applique le portail captif et VLAN 200 pour les utilisateurs authentifiés](../../../projects/images/captive-portal-architecture.jpg)

L'architecture cible place un pare-feu pfSense entre le lien Internet et un commutateur, avec deux VLAN : un où le portail captif s'applique aux utilisateurs non encore authentifiés, et un pour les utilisateurs authentifiés.

Je l'ai monté et testé en lab virtuel : une VM pfSense avec une interface WAN et un segment LAN interne, et des VM clientes sur ce segment.

## Ce que j'ai fait

- Installation de **pfSense** et configuration de ses interfaces WAN et LAN.
- Mise en place du **serveur DHCP** sur le LAN pour que les clients reçoivent automatiquement adresse, passerelle et DNS.
- Création des comptes dans la **base d'utilisateurs locale** de pfSense, choisie comme méthode d'authentification du portail.
- Activation d'une **zone de portail captif** sur l'interface LAN.
- Écriture des **règles de pare-feu** sur le LAN : autoriser HTTP et HTTPS, bloquer tout le reste.
- Création d'une **page de connexion personnalisée** en HTML, avec les variables attendues par pfSense pour l'action du formulaire et l'URL de redirection, puis import dans le portail.
- Rédaction du **manuel de déploiement** qui reprend l'ensemble.

## Ce que j'ai appris

- Comment le DHCP, le DNS, les règles de pare-feu et le portail dépendent les uns des autres : un client qui ne reçoit ni adresse ni DNS n'atteint même pas la page de connexion.
- Les règles de pare-feu sont évaluées dans l'ordre : la règle de blocage générale doit être placée sous les règles qui autorisent le trafic.
