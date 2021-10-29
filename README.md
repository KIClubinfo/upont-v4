# Upont 4.0

Refonte de uPont [TODO : liens vers site et ancien repo] en python (django) pour une meilleure accessibilité aux nouveaux développeurs (et purge).

* framework full-stack django
* base de données PostgreSQL
* [TODO : separate front-end framework if needed, since django is more back-end oriented]

# Installation

Pour lancer le site en local (commandes docker-compose standard, version 1.29.2) :
```
$ docker-compose up -d
```

Site accessible au port 8000 : (configurable dans le fichier .env)
```
$ $BROWSER localhost:8000
```

Accès à la DB par docker exec : [TODO : setup django admin site]
```
$ docker exec -it $(docker ps -f 'name=db' --format '{{.ID}}') psql -U upont
```

Accès à django par docker-compose exec :
```
$ docker-compose exec back /bin/sh
```

# Développement d'une feature

Toujours travailler sur une nouvelle branche :
```
$ git branch feature
$ git checkout feature
```

Mettre la branche en ligne et créer une pull request :
```
$ git push --set-upstream origin feature
```

Quand un reviewer a validé la pull request, faire un rebase de master dans la nouvelle branche pour ne pas avoir de conflits :
```
$ git checkout master
$ git rebase feature
```

Faire un rebase dans master :
```
$ git checkout feature
$ git rebase master
```

Mettre les changements en ligne :
```
$ git checkout master
$ git push
```