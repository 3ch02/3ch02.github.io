---
title: "Analyse de logs et détection d'intrusion avec Wazuh (lab SOC)"
summary: "Projet d'équipe de deuxième année : un petit SOC construit autour de Wazuh derrière un pare-feu pfSense, avec des agents Windows et Linux, puis huit scénarios d'attaque lancés depuis Kali pour vérifier ce que le SIEM détecte réellement."
---

## Contexte

Mon projet scolaire (PPE) de deuxième année, réalisé en équipe de trois : construire une infrastructure qui centralise les journaux et détecte les intrusions, puis prouver qu'elle fonctionne en l'attaquant.

Wazuh a été retenu comme plateforme principale parce qu'il réunit dans un seul outil open source un SIEM, la détection sur les hôtes, le contrôle d'intégrité des fichiers, la détection de vulnérabilités et la réponse active. ELK et Splunk ont été étudiés à titre de comparaison.

## Architecture

| Composant | Rôle |
| --- | --- |
| pfSense | Routeur et pare-feu (interfaces WAN, LAN et DMZ), DHCP du LAN, envoie ses journaux au SIEM |
| Serveur Wazuh | Manager, indexer et dashboard sur une seule machine virtuelle |
| Agent Windows 10 | Poste de travail surveillé |
| Agent Ubuntu | Machine Linux surveillée |
| Kali Linux | Attaquant |

Flux des journaux : les agents remontent au manager Wazuh, pfSense transmet ses événements pare-feu et système par syslog distant (UDP 514), et tout est indexé et consulté depuis le dashboard.

## Ce que nous avons déployé

- **pfSense** avec ses interfaces et le DHCP.
- Le **serveur Wazuh**, importé depuis l'appliance virtuelle officielle, et les **agents** installés sur les machines Windows et Ubuntu.
- L'**intégration pfSense → Wazuh** par syslog distant : journalisation distante activée sur le pare-feu, écoute syslog déclarée dans le `ossec.conf` du manager, et réception vérifiée avec `tcpdump`.
- Le **contrôle d'intégrité des fichiers en temps réel** sur l'agent Windows : par défaut l'analyse est périodique, d'où l'ajout de `realtime="yes"` sur le répertoire surveillé.
- Les **alertes par e-mail** : Postfix sur le serveur Wazuh, en relais vers un service SMTP externe, et notifications activées dans le manager au-dessus d'un seuil de sévérité.

## Tests de détection

Chaque test a été lancé depuis la machine attaquante, puis analysé dans la vue Discover du dashboard.

| N° | Scénario | Méthode | Ce que Wazuh a remonté |
| --- | --- | --- | --- |
| 1 | Connectivité | Agents enrôlés et vérifiés dans le résumé des agents | Les deux agents actifs |
| 2 | Force brute RDP sur Windows | `hydra` avec une liste de mots de passe | Règle 60122 (échec d'ouverture de session), 22 échecs corrélés depuis l'attaquant |
| 3 | Force brute SSH sur Ubuntu | `hydra` avec une liste de mots de passe | Règles 5710 / 5712, l'attaquant identifié comme source |
| 4 | Détection de vulnérabilités | Module Vulnerability Detector sur l'agent Windows | CVE-2025-21382 (CVSS 7,8, élevée), affichée comme corrigée après la mise à jour du système |
| 5 | Malware sur Linux | Payload Meterpreter généré avec `msfvenom`, téléchargé sur Ubuntu | Règle 510, signalé dès l'écriture du fichier |
| 6 | Intégrité des fichiers sur Windows | Une ligne ajoutée au fichier `hosts` | Règle 550, niveau 7 : empreinte et taille modifiées, associé à MITRE T1565.001 |
| 7 | Persistance sur Windows | Payload récupéré avec `certutil`, enregistré comme service avec `sc create` | Règle 61138 (nouveau service Windows), associé à MITRE T1543.003 |
| 8 | Alertes par e-mail | Relais Postfix et notifications du manager | E-mails d'alerte reçus |

Les huit démonstrations prévues ont été validées.

## Ce que j'ai appris

- **Un SIEM ne voit que ce qu'on lui envoie.** L'enrôlement des agents, l'écoute syslog et la vérification du trafic sur le réseau passent avant de pouvoir faire confiance au dashboard.
- **Les réglages par défaut comptent.** Le contrôle d'intégrité est périodique tant que le temps réel n'est pas activé, et les e-mails ne partent qu'au-dessus d'un niveau configuré : une alerte de niveau 7 comme la modification du fichier `hosts` est enregistrée, mais personne n'est prévenu par e-mail.
- **Un échec de connexion, c'est du bruit ; c'est la corrélation qui en fait une attaque.** Les détections de force brute viennent de la répétition depuis une même source, pas d'un événement isolé.
- **Jouer l'attaquant rend les alertes lisibles.** Lancer une attaque puis lire l'alerte produite côte à côte montre ce que signifie chaque champ et à quelle technique MITRE ATT&CK la rattacher.

## Limites

C'est un lab sur machines virtuelles, avec un pare-feu et deux hôtes surveillés, et des attaques que nous avons lancées nous-mêmes. La réponse active (isoler automatiquement un fichier ou bloquer une adresse) a été identifiée comme l'étape suivante mais n'a pas été mise en place.
