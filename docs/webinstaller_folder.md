# Web Installer

Container Node. Permet de lancer des commandes *npm*. Il permet notamment de compiler les fichiers javascript pour React.

## Usage

Lancer des commandes *npm* :

```
docker-compose exec webinstaller npm <command>
```

Par exemple pour installer un package :
```
docker-compose exec webinstaller npm install package
```

## Fonctionnement

La configuration de la compilation des bundles se trouve dans */react/webpack.config.js*. On y a notamment placé le chemin dans lequel doivent être placés les fichiers compilés : */src/upont/static/react/*. On utilise donc un volume *bundles* pour placer ces fichiers dans les fichiers statiques du *back*.

### En développement :

En développement, on re-compile les bundles à chaque fois que le code est modifié.

### En production :

En production, on ne compile les bundles que au lancement du container.