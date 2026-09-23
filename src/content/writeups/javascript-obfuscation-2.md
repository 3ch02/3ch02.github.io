---
# Imported from Obsidian: CTF/Writeup -- Javascript Obfuscation 2.md
# Draft: Root-Me rules forbid publishing solutions
title: Javascript - Obfuscation 2
category: Cryptography
ctf: Root-Me
date: 2026-08-20
summary: Retrouver le password contenu dans la variable JavaScript pass.
tags:
- cryptography
- root-me
lang: fr
draft: true
imported: true
---

## Objectif

Retrouver le password contenu dans la variable JavaScript `pass`.

## Code source

```html
<script type="text/javascript">
    var pass = unescape("unescape%28%22String.fromCharCode%2528104%252C68%252C117%252C102%252C106%252C100%252C107%252C105%252C49%252C53%252C54%2529%22%29");
</script>
```

## Analyse

La valeur est obfusquee en plusieurs etapes :

1. Les caracteres `%XX` sont de l'encodage URL.
2. La fonction JavaScript `unescape()` decode cette premiere couche.
3. Le resultat contient un appel `String.fromCharCode()` qui convertit des codes ASCII en caracteres.

### Premiere couche

En decodant la chaine URL, on obtient :

```javascript
unescape("String.fromCharCode(104,68,117,102,106,100,107,105,49,53,54)")
```

### Deuxieme couche

La fonction `String.fromCharCode()` transforme les codes ASCII :

```javascript
String.fromCharCode(
    104, 68, 117, 102, 106, 100,
    107, 105, 49, 53, 54
)
```

Correspondance des caracteres :

| Code | Caractere |
| --- | --- |
| 104 | h |
| 68 | D |
| 117 | u |
| 102 | f |
| 106 | j |
| 100 | d |
| 107 | k |
| 105 | i |
| 49 | 1 |
| 53 | 5 |
| 54 | 6 |

## Decodage avec la console JavaScript

```javascript
const encoded = 'unescape%28%22String.fromCharCode%2528104%252C68%252C117%252C102%252C106%252C100%252C107%252C105%252C49%252C53%252C54%2529%22%29';
const source = decodeURIComponent(encoded);
console.log(source);
// unescape("String.fromCharCode(104,68,117,102,106,100,107,105,49,53,54)")

const flag = String.fromCharCode(104, 68, 117, 102, 106, 100, 107, 105, 49, 53, 54);
console.log(flag);
```

## Flag / Password

```text
hDufjdki156
```

## Conclusion

Le password n'est pas chiffre. Il est simplement cache derriere un encodage URL, puis une conversion ASCII avec `String.fromCharCode()`.
