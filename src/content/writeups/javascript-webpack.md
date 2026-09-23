---
# Imported from Obsidian: RootME/Writeup -- Javascript - Webpack.md
# Draft: Root-Me rules forbid publishing solutions
title: Javascript - Webpack
category: Web
ctf: Root-Me
date: 2026-08-20
summary: Analyser une application JavaScript construite avec Webpack et retrouver le flag expose dans sa source map.
tags:
- root-me
- web
lang: fr
draft: true
imported: true
---

## Objectif

Analyser une application JavaScript construite avec Webpack et retrouver le flag expose dans sa source map.

## 1. Recuperer le code JavaScript

La page charge un bundle JavaScript compile, par exemple :

```html
<script src="/static/js/app.a92c5074dafac0cb6365.js"></script>
```

Le bundle contient le code necessaire au navigateur, mais il est transforme et regroupe par Webpack.

## 2. Role de Webpack

Webpack est un bundler JavaScript. Il prend plusieurs fichiers du projet, comme :

- `src/main.js` ;
- les composants Vue ;
- le routeur ;
- les dependances ;
- les fichiers CSS et assets ;

puis les regroupe dans un ou plusieurs fichiers JavaScript optimises pour le navigateur.

Le resultat est souvent minifie, ce qui rend le code plus difficile a lire, mais cela ne constitue pas une protection. Le navigateur doit recevoir le code, donc un utilisateur peut le telecharger.

## 3. Identifier la source map

A la fin du bundle, on trouve une directive comme :

```javascript
//# sourceMappingURL=app.a92c5074dafac0cb6365.js.map
```

Cette ligne indique le nom de la source map associee au bundle.

Une source map est un fichier JSON qui permet au navigateur de relier le code compile au code source original. Elle peut contenir :

- les chemins des fichiers originaux ;
- les noms des fonctions et variables ;
- les fichiers Vue originaux ;
- les commentaires du developpeur ;
- la propriete `sourcesContent`, qui contient parfois le code source complet.

Une source map ne sert pas a decoder un mot de passe. Elle fournit directement les informations de debug utilisees par les DevTools.

## 4. Telecharger la source map

Depuis le terminal :

```bash
curl -O http://challenge01.root-me.org/web-client/ch27/static/js/app.a92c5074dafac0cb6365.js.map
```

Le fichier peut ensuite etre recherche avec :

```bash
grep -RniE 'flag|password|secret|root-me' app.a92c5074dafac0cb6365.js.map
```

On peut aussi formater le JSON pour le lire plus facilement :

```bash
python3 -m json.tool app.a92c5074dafac0cb6365.js.map > app-formatted.json
```

## 5. Decouverte dans la source map

La source map revele notamment un composant non utilise par le routeur visible :

```text
src/components/YouWillNotFindThisRouteBecauseItIsHidden.vue
```

Le champ `sourcesContent` contient le code source original de ce composant. Dans ses commentaires, on trouve :

```javascript
// Did you know that comment are readable by the end user ?
// Well, this because I build the application with the source maps enabled !!!
// So please, disable source map when you build for production
// Here is your flag : BecauseSourceMapsAreGreatForDebuggingButNotForProduction
```

## 6. Flag

```text
BecauseSourceMapsAreGreatForDebuggingButNotForProduction
```

## 7. Voir la source map dans le navigateur

### Methode directe

A partir de l'URL du bundle, remplacer le nom du fichier `.js` par `.js.map` :

```text
http://challenge01.root-me.org/web-client/ch27/static/js/app.a92c5074dafac0cb6365.js.map
```

Le navigateur affiche le JSON de la source map.

### Avec les DevTools

1. Ouvrir la page du challenge.
2. Appuyer sur `F12`.
3. Ouvrir l'onglet **Sources**.
4. Chercher le bundle JavaScript ou le dossier `webpack://`.
5. Ouvrir les dossiers `src/` et `components/`.
6. Lire `YouWillNotFindThisRouteBecauseItIsHidden.vue`.
7. Rechercher `flag` avec `Ctrl+F`.

Si la source map est disponible, Chrome ou Firefox affiche souvent les fichiers originaux sous `webpack://`.

### Avec Burp Suite

1. Ouvrir **Proxy > HTTP history**.
2. Selectionner la reponse du fichier `.js`.
3. Rechercher `sourceMappingURL`.
4. Recuperer l'URL du fichier `.js.map`.
5. Envoyer la requete vers **Repeater** ou la telecharger avec `curl`.
6. Rechercher `flag` dans la reponse JSON.

## 8. Pourquoi c'est un probleme en production

Activer les source maps en production peut exposer :

- le code source de l'application ;
- des commentaires internes ;
- des routes non documentees ;
- des noms d'API ;
- des informations de debug ;
- des secrets accidentellement presents dans le code.

Dans ce challenge, le flag est volontairement place dans un commentaire. Dans une vraie application, une source map publique devient critique si elle contient des cles privees, des tokens, des mots de passe ou de la logique sensible.

## Conclusion

Webpack assemble les fichiers JavaScript du projet dans un bundle distribue au navigateur. La directive `sourceMappingURL` permet de retrouver la source map correspondante. En telechargeant cette map et en inspectant `sourcesContent`, on retrouve le fichier Vue cache et le flag.
