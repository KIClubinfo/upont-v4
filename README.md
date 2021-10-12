# Upont X.0

Refonte de uPont [TODO : liens vers site et ancien repo] en python (django) pour une meilleure accessibilité aux nouveaux développeurs (et purge).

* framework full-stack django
* base de données PostgreSQL
* [TODO : separate front-end framework if needed, since django is more back-end oriented]

# Installation

Pour lancer le site en local (commandes docker-compose standard, version 1.29.2) :
```
$ docker-compose up -d
```

Site accessible au port 8000 :
```
$ $BROWSER localhost:8000
```

Accès à la DB par docker exec : [TODO : setup django admin site]
```
$ docker exec -it $(docker ps -f 'name=db' --format '{{.ID}}') psql -U upont
```
