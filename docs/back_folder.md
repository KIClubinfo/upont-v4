# Dossier back

## Présentation

Ce dossier est la racine du projet django. Les dossiers *news*, *pochtron*, *social* et *trade* correspondent chacun à une **application** django. Le dossier *upont* correspond à l'application principale du projet.

## Installation d'un nouveau package python

Chaque package installe des dépendances pour fonctionner. Cependant indiquer seulement la version du package ne garantit rien sur les versions des dépendances qui seront installées. On utilise donc Poetry pour fixer les versions de ces dépendances dans le fichier *poetry.lock*. Les packages à installer sont eux indiqués dans le fichier *pyproject.toml*.

Pour ajouter un nouveau package il faut :

Entrer dans le container :
```
$ docker-compose exec back /bin/sh
```

Installer le nouveau package **avec poetry** :
```
$ poetry add "package~1.2.3"
```
En général il faut éviter de spécifier une version exacte car cela peut rendre impossible la résolution des dépendances.

Les nouvelles dépendances s'écrivent directement dans le *poetry.lock* qu'il faut commit.

## Dockerfile

On trouve dans ce dossier le *Dockerfile* du service **back** (service défini dans le *docker-compose.yml*). Ce fichier est utilisé lors du *build* du container. Il se décompose en 3 *stages*:
* Installation de l'environnement Python
* Installation de Poetry et installation des dépendances dans un environnement virtuel. Les dépendances sont indiqués dans le fichier *poertry.lock* s'il existe, sinon ce fichier est créé à ce moment.
* La dernière *stage* peut être **development** ou **production** (on indique par un tag dans le *docker-compose.yml* laquelle de ces deux *stage* doit être utilisée). Dans les deux cas on installe dans cette *stage* les packages Python indiqués dans *pyproject.toml*, sachant que leurs dépendances ont déjà été installées à la *stage* précédente.

## Autres fichiers dans ce dossier

### manage.py

Fichier utilisé par django pour des tâches d'administration du projet.

### gunicorn.conf.py

Fichier de configuration de gunicorn, l'application wsgi utilisée en production.

### entrypoint.dev.sh et entrypoint.prod.sh

Scripts bash qui sont exécutés au lancement du container back (l'un lorsqu'on lance en développement, l'autre lorsqu'on lance en production).