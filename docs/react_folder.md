# Front

Ce dossier contient le **front** React de uPont. Le fonctionnement du front est assez particulier et se structure comme suit :

* Certaines pages n'utilisent pas React, le front est donc entièrement créé avec le moteur de templates de django, *jinja2*.

* Les pages qui utilisent React utilisent quand même le moteur de templates de django, et on insère les composants React dans les templates.

## Structure des fichiers

### Dossier *src*

Dossier dans lequel on place le code source du front.
On place les composants React dans le dossier *src/components*.

### *package.json* et *package-lock.json*

Fichiers indiquants les packages et les dépendances javascript. Pour ajouter des packages, consulter la  [documentation de webinstaller](webinstaller_folder.md).

### webpack.config.js

C'est le fichier de configuration de *webpack* qui compile le front. Il faut y placer dans *entry* les noms des fichiers à compiler, par exemple :
```
entry: {
    index_users: './src/index_users.js',
  }
```
On y indique aussi l'endroit où placer les fichiers compilés :
```
output: {
    path: '/src/upont/static/react/',
    filename: '[name].bundle.js'
  }
```

### .babelrc

Fichier de configuration de *babel* pour la transpilation javascript.

### Dossiers *node_modules* et *static*

Dossiers générés à l'exécution, ne pas les ajouter au gestionnaire de versions.