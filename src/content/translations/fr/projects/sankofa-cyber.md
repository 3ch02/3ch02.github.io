---
title: "Sankofa Cyber"
summary: "Une plateforme de sensibilisation à la sécurité et de gestion du risque humain : simulations d'ingénierie sociale réalistes et multicanales, labs pratiques, et un Human Risk Score par utilisateur pour mesurer et réduire l'exposition."
---

## Le problème

Les pare-feu, EDR et XDR ne cessent de s'améliorer, mais la plupart des intrusions réussies commencent encore par une personne : un e-mail convaincant, un QR code sur une affiche, un SMS à propos d'un colis, un appel qui ressemble à celui du patron. L'IA générative rend ces leurres moins chers et plus crédibles.

La plupart des programmes de sensibilisation y répondent par des quiz théoriques ou une simulation de phishing générique par an. Ils disent rarement à une organisation **à quel point elle est réellement exposée**, ni **qui a besoin de quelle formation**.

## L'idée : former → tester → mesurer → corriger

Sankofa Cyber est construit autour d'une boucle continue :

1. **Former** — des modules courts et pratiques, et des labs.
2. **Tester** — des simulations d'ingénierie sociale réalistes et multicanales.
3. **Mesurer** — traduire les comportements observés en un **Human Risk Score (HRS)**.
4. **Corriger** — attribuer une remédiation ciblée selon ce qui s'est réellement mal passé.

## Menaces couvertes

| Vecteur | Ce qui est simulé |
| --- | --- |
| Phishing / spear-phishing | E-mails contextualisés imitant des collègues, des partenaires ou des services internes |
| Smishing | Leurres par SMS visant le recoupement entre usage personnel et professionnel (BYOD) |
| Quishing | Affiches à QR code générées par campagne, avec suivi des scans |
| Vishing | Appels vocaux générés par IA avec une voix synthétique *générique* de type dirigeant — jamais la voix clonée d'une vraie personne |
| Ingénierie sociale | Fausses pages d'atterrissage, scénarios de prétexte |

## Deux espaces

- **Sankofa Academy** — un espace d'apprentissage pour les étudiants et les particuliers : modules, quiz, badges, classement, et labs pratiques (corrigés automatiquement) où l'on analyse des en-têtes d'e-mail, inspecte des URL suspectes ou repère les anomalies d'une fausse page de connexion.
- **Sankofa Enterprise** — une console pour les équipes de sécurité : gestion des employés et des départements, constructeur de campagnes multicanales, suivi de la délivrabilité, et tableau de bord du risque humain de l'organisation.

## Ce qui est réellement construit

Ce n'est pas une maquette : la [démo en ligne](https://cyber-sankofa.vercel.app/) fait tourner une vraie application Next.js avec authentification (vérification de l'e-mail, 2FA, réinitialisation du mot de passe), une base Postgres et un panneau d'administration. Concrètement, aujourd'hui :

- **Academy** : modules et leçons, labs corrigés automatiquement, quiz, certifications, classement et badges.
- **Console Enterprise** : constructeur de campagnes e-mail / SMS / QR / voix, gestion des départements et des employés, tableaux de bord de délivrabilité et de rapports.
- **Suivi** : un pixel de suivi d'ouverture, des liens de redirection, des événements de soumission sur les pages d'atterrissage, et un pipeline d'appels vocaux (collecte → statut → débriefing) — tout est journalisé sous forme d'événements, sans jamais stocker ce qu'un utilisateur a saisi.
- **Sankofa Shield** : une API `/shield/check` avec un parcours analyse → débriefing, et une première version d'un module Gmail pour signaler un phishing en un clic.
- **Human Risk Score** : un calculateur pondéré (avec ses propres tests unitaires) qui transforme les comportements en simulation et en lab en un score de 0 à 100, décrit ci-dessous, et une petite **Human Risk API** (`/api/v1/risk`) que d'autres outils pourraient interroger.
- **IA** : conseils de campagne pour les administrateurs et débriefings après les labs, générés avec Gemini ; génération de voix synthétique pour le canal vishing.

Ce qui n'y est *pas* encore : c'est un projet étudiant en cours de construction, pas un système de production durci. Il reste des aspérités, des parcours d'administration incomplets et des fonctions encore en réglage, plutôt qu'une plateforme aboutie et auditée.

## Mesurer le risque humain

Chaque utilisateur reçoit un score de 0 à 100 construit à partir de quatre dimensions pondérées :

| Dimension | Poids | Fondée sur |
| --- | --- | --- |
| Vigilance | 0,25 | Taux de signalement, délai de signalement, justesse des signalements |
| Résistance | 0,35 | Comportement pendant les simulations : pas de clic, survol puis clic, clic, identifiants soumis |
| Compétence | 0,25 | Résultats dans les labs pratiques |
| Hygiène | 0,15 | Signaux externes optionnels (par exemple mots de passe compromis via HIBP), avec consentement |

Un coefficient contextuel (exposition du département, ancienneté) ajuste le score, mais il est **plafonné à 1,5** pour que le contexte seul ne puisse jamais faire passer quelqu'un dans la tranche « critique » : il faut que ce soit le comportement.

## Protection de la vie privée dès la conception

Une plateforme qui simule des attaques sur des personnes doit être prudente avec leurs données :

- Les fausses pages de connexion enregistrent **qu'une** saisie a été soumise, **jamais ce qui** a été saisi.
- Seuls des prompts anonymisés et génériques sont envoyés au modèle d'IA externe ; les noms, les détails d'infrastructure et les scores restent dans la base de l'application.
- Contrôle d'accès par rôles et isolation entre organisations.

## Stack

Next.js 15 (App Router, Server Actions) et TypeScript, Tailwind CSS, Prisma sur PostgreSQL, Auth.js pour les sessions et les rôles, et l'API Gemini pour la génération de scénarios, les conseils de campagne et les débriefings.
