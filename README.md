# 3ch0 — Portfolio & CTF write-ups

Portfolio, blog technique et journal de CTF de **KERIM Loukouman (3ch0)**, étudiant en cybersécurité à IPNET Institute of Technology.

Site 100 % statique généré avec **Astro 7**, **TypeScript**, **Tailwind CSS 4** et du **Markdown/MDX**, déployé sur **GitHub Pages** via **GitHub Actions**. Pas de backend, pas de base de données, pas de tracker.

---

## Sommaire

1. [Prérequis](#prérequis)
2. [Installation et développement local](#installation-et-développement-local)
3. [Structure du projet](#structure-du-projet)
4. [Modifier les informations personnelles](#modifier-les-informations-personnelles)
5. [Ajouter du contenu](#ajouter-du-contenu)
6. [Mettre à jour ESIG Tech Arena après la finale](#mettre-à-jour-esig-tech-arena-après-la-finale)
7. [Déploiement sur GitHub Pages](#déploiement-sur-github-pages)
8. [Sécurité, performance, SEO](#sécurité-performance-seo)
9. [Importer les write-ups depuis Obsidian](#importer-les-write-ups-depuis-obsidian)

---

## Prérequis

- **Node.js ≥ 22.12** (la CI utilise Node 24)
- npm

## Installation et développement local

```bash
npm install        # installe les dépendances
npm run dev        # serveur de dev : http://localhost:4321
npm run build      # vérification TypeScript (astro check) + build dans dist/
npm run preview    # sert le build de production en local
```

> Avec Astro 7, `npm run dev` lance le serveur en arrière-plan. Commandes utiles :
> `npx astro dev status`, `npx astro dev logs`, `npx astro dev stop`.
> Si une modification de `src/content.config.ts` n'est pas prise en compte, redémarrez le serveur.

Le serveur de dev affiche aussi les **brouillons** (`draft: true`), marqués d'un badge `DRAFT`. Le build de production ne les inclut jamais.

## Structure du projet

```text
├── .github/workflows/deploy.yml   # build + déploiement GitHub Pages
├── content-templates/             # modèles à copier pour créer du contenu
├── public/                        # fichiers servis tels quels (favicon, OG image, CV…)
├── scripts/generate-images.mjs    # régénère favicon PNG + image Open Graph
└── src/
    ├── config/site.ts             # ⚙️  identité, liens, CV, navigation, compétences
    ├── content.config.ts          # schémas des collections (validation du frontmatter)
    ├── content/
    │   ├── writeups/              # write-ups CTF (.md / .mdx)
    │   ├── projects/              # projets
    │   ├── ctf/                   # compétitions CTF (résultats, équipes, étapes)
    │   ├── achievements/          # réalisations (liées aux compétitions)
    │   └── certifications/        # certifications ET formations (séparées)
    ├── components/                # Navbar, Hero, Terminal, cartes, badges…
    ├── layouts/                   # Layout (SEO, nav, footer) et ArticleLayout (lecture)
    ├── lib/                       # helpers (URLs, dates, requêtes de contenu, Shiki/CSP)
    ├── pages/                     # routes (une page par fichier)
    └── styles/global.css          # thème Tailwind, typographie des articles, code
```

Chaque fichier ajouté dans `src/content/<collection>/` est **détecté automatiquement** : page générée, listes, tags, catégories, flux RSS et sitemap. Aucun composant à modifier. Les fichiers dont le nom commence par `_` sont ignorés.

Le frontmatter est **validé au build**. Un champ manquant ou une valeur invalide (catégorie inconnue, date mal formée…) fait échouer le build avec un message explicite, donc rien de cassé n'est publié.

## Modifier les informations personnelles

Tout est dans **`src/config/site.ts`** :

| Élément | Où |
| --- | --- |
| Nom, pseudo, rôle, école, description SEO | `SITE` |
| GitHub, LinkedIn, email, CTFtime, TryHackMe, HackTheBox, Root-Me | `links` (mettre `null` pour masquer) |
| CV | `CV` (voir ci-dessous) |
| Menu | `NAV` |
| Compétences | `SKILLS` |
| Centres d'intérêt (terminal du hero) | `INTERESTS` |

Un lien à `null` n'est **jamais affiché**, donc aucun lien mort ou inventé.

**CV :** placez le PDF dans `public/cv/KERIM_Loukouman_CV.pdf` puis passez `CV.available` à `true`. Tant qu'il est à `false`, le bouton du hero devient « Request CV » et renvoie vers la page Contact.

**Image de partage / favicon :** modifiez `public/favicon.svg` ou le SVG dans `scripts/generate-images.mjs`, puis lancez `npm run images`.

## Ajouter du contenu

Copiez le modèle correspondant depuis `content-templates/`. Le nom du fichier devient l'URL.

### Un write-up

```bash
cp content-templates/writeup.md src/content/writeups/ma-solution.md
# → /writeups/ma-solution/
```

Frontmatter :

```yaml
---
title: "ECDSA Nonce Reuse"
category: "Cryptography"   # Forensics | Cryptography | Web | Reverse Engineering | Steganography | OSINT | Pwn | Misc | Boot2Root
difficulty: "Medium"       # Easy | Medium | Hard | Insane
ctf: "IPNET CyberBattle 2026"
competition: ipnet-cyberbattle-2026   # optionnel : lie le write-up à la page de la compétition
date: 2026-09-22
summary: "Une phrase affichée sur les cartes et utilisée par la recherche."
tags: [crypto, ecdsa, secp256k1]
featured: false            # optionnel : bloc « Featured » de /writeups
draft: true                # retirer pour publier
---
```

Le rendu gère : blocs de code avec coloration syntaxique, nom du langage et bouton copier ; tableaux défilants sur mobile ; images optimisées ; sommaire automatique (titres `##` et `###`) ; temps de lecture ; articles précédent/suivant et liés.

**Images :** placez-les à côté du write-up (ex. `src/content/writeups/images/`) et utilisez un chemin relatif `![légende](./images/capture.png)`. Astro les convertit en WebP, ajoute les dimensions et le lazy loading.

**MDX :** renommez le fichier en `.mdx` pour utiliser des composants. Évitez les attributs `style="…"` en ligne, que la CSP bloque (voir [Sécurité](#sécurité-performance-seo)) ; utilisez des classes Tailwind.

**Source (`ctf`)** : nom de la compétition ou de la plateforme (`picoCTF 2026`, `Hack The Box`, `Hackropole (FCSC)`…). Le site regroupe les write-ups par source, sans l'année ni la parenthèse (`picoCTF 2019/2024/2026` → **picoCTF**), avec une page `/writeups/source/<source>/` et un filtre en deux groupes :

- **Competitions** : sources liées à une fiche de `src/content/ctf/` (champ `competition`) ou listées dans `COMPETITION_EVENTS` (`src/lib/content.ts`) ;
- **Platforms** : tout le reste (plateformes d'entraînement).

`difficulty` est optionnelle : ne la renseignez que si le challenge en a une officielle. `lang: fr` indique que l'article est en français.

### Un projet

```bash
cp content-templates/project.md src/content/projects/mon-projet.md
```

`featured: true` affiche le projet en grand sur la page d'accueil, `order` contrôle l'ordre.

### Une compétition CTF

```bash
cp content-templates/ctf.md src/content/ctf/nom-du-ctf-2026.md
```

Les résultats sont décrits par **étapes** (`stages`). La dernière étape terminée avec un classement est présentée comme « le résultat ». Les étapes non terminées sont **toujours** affichées comme en attente, donc un résultat de qualification ne peut pas apparaître comme un résultat final.

Pour la faire apparaître dans **Achievements**, ajoutez un fichier dans `src/content/achievements/` avec `competition: nom-du-ctf-2026`. Classement, équipe, pseudo et étapes sont lus depuis la fiche CTF (une seule source de vérité).

### Une certification ou une formation

```bash
cp content-templates/certification.md src/content/certifications/nom.md
```

- `kind: certification` : examen réussi, certificat délivré (`status: obtained | in-progress | planned`)
- `kind: training` : cours ou parcours suivi (`status: completed | in-progress | planned`)

Le schéma **refuse** une formation marquée `obtained`. Une formation ne peut donc pas être affichée comme une certification.

Le champ optionnel `expires` affiche « Valid until » ou « Expired » (calculé au build). Le lien Credly est dans `src/config/site.ts` (`CREDLY_URL`).

## Mettre à jour ESIG Tech Arena après la finale

Un seul fichier à modifier : `src/content/ctf/esig-tech-arena-2026.md`.

```yaml
stages:
  - name: "Qualification stage"
    status: completed
    rank: 1
  - name: "Final"
    status: completed   # était: upcoming
    rank: 2             # ← classement réel de la finale
```

La carte CTF, la page Achievements et la page de la compétition se mettent à jour automatiquement. Pensez aussi à adapter le texte sous le frontmatter (« The final has not taken place yet… »).

## Déploiement sur GitHub Pages

Le workflow `.github/workflows/deploy.yml` se déclenche à chaque `git push` sur `main` :

```text
git push → GitHub Actions → npm ci → npm run build (astro check + build) → upload dist/ → deploy → GitHub Pages
```

### Première mise en ligne

1. Créez un dépôt GitHub :
   - **`3ch02.github.io`** → site servi à `https://3ch02.github.io/` (recommandé pour un portfolio)
   - ou n'importe quel nom, ex. `3ch0-portfolio` → `https://3ch02.github.io/3ch0-portfolio/`
2. Dans le dépôt : **Settings → Pages → Build and deployment → Source : GitHub Actions**.
3. Poussez le code :

   ```bash
   git init
   git add .
   git commit -m "Initial portfolio"
   git branch -M main
   git remote add origin https://github.com/3ch02/<nom-du-depot>.git
   git push -u origin main
   ```

4. Suivez le déploiement dans l'onglet **Actions**.

L'URL du site et le chemin de base sont **détectés automatiquement** par `actions/configure-pages` et passés au build (`SITE_URL`, `BASE_PATH`) : rien à modifier, que ce soit un site utilisateur ou un site de projet. Tous les liens internes passent par `url()` (`src/lib/utils.ts`), qui ajoute le chemin de base.

Pour un **domaine personnalisé** : configurez-le dans Settings → Pages et ajoutez un fichier `public/CNAME` contenant le domaine.

Pour tester localement un build « site de projet » :

```bash
SITE_URL=https://3ch02.github.io BASE_PATH=/3ch0-portfolio npm run build
```

## Sécurité, performance, SEO

- **Content-Security-Policy** : Astro génère une balise `<meta http-equiv="content-security-policy">` avec les empreintes (SHA-256) de chaque script et style. La coloration syntaxique Shiki est convertie en classes (`src/lib/shiki-csp.mjs`), car la CSP bloque les attributs `style` en ligne.
  Le build affiche `[WARN] [config] Shiki syntax highlighting uses inline styles that are not compatible with Content Security Policy`. Ce message est **attendu** : Astro l'émet pour toute combinaison Shiki + CSP, sans tenir compte du transformer qui supprime ces styles (le HTML généré n'en contient aucun).
- **JavaScript minimal** : menu mobile, recherche des write-ups, bouton copier et sommaire actif. Les animations d'apparition sont en CSS pur (`animation-timeline: view()`) et désactivées si `prefers-reduced-motion` est activé.
- **Polices auto-hébergées** (Inter, JetBrains Mono) avec préchargement, aucune requête vers un service tiers.
- **SEO** : titre et description par page, URL canonique, Open Graph et Twitter card, données structurées `Person`, `sitemap-index.xml`, `robots.txt`, flux RSS `/rss.xml`.
- **« Articles populaires » sans backend** : utilisez `featured: true` sur un write-up.
- Recherche : champ de recherche plein texte côté client (titre, catégorie, CTF, tags, résumé), filtres par catégorie (pages statiques), pages par tag. Le paramètre `?q=` est conservé dans l'URL.

## Importer les write-ups depuis Obsidian

Les write-ups viennent du vault Obsidian et sont convertis par `scripts/import-obsidian.py` :

```bash
python3 scripts/import-obsidian.py "/home/echo/Obsidian Vault" --report   # simulation : tableau titre / source / catégorie / brouillon
python3 scripts/import-obsidian.py "/home/echo/Obsidian Vault"            # écrit src/content/writeups/
```

Le script :

- ne garde que les write-ups (cours, labs, fiches, projets et `Ohana-security-review.md` sont exclus) ;
- convertit la syntaxe Obsidian (`![[image.png]]`, `[[liens]]`, callouts, `#tags`, `==surlignage==`) et copie les images dans `src/content/writeups/images/obsidian/` ;
- déduit titre, source (d'après le dossier), catégorie, difficulté, points, date, tags et résumé ;
- supprime les doublons (garde la note la plus longue) ;
- met en **brouillon** ce qui ne doit pas être publié : ESIG Tech Arena (finale pas encore jouée), Root-Me (règlement interdisant la publication des solutions), machines Hack The Box non retirées, sources inconnues, notes trop courtes, **et toute note relue à la main et jugée incomplète** (pas de flag, script inachevé, doublon) — voir `OVERRIDES` dans le script, section « Reviewed » (30 notes concernées, relecture du 2026-09-23).

Les fichiers importés portent `imported: true` et sont **régénérés** à chaque import. Pour corriger un titre, une catégorie ou une source de façon durable, ajoutez une entrée dans `OVERRIDES` du script plutôt que d'éditer le fichier généré. Un write-up écrit à la main (sans `imported: true`) n'est jamais touché.

Pour publier un brouillon (par ex. ESIG après la finale), retirez la règle correspondante dans `DRAFT_RULES` ou ajoutez `{"draft": False}` dans `OVERRIDES`, puis relancez l'import.
