# Upont 4.0

Refonte de uPont [TODO : liens vers site et ancien repo] en python (django) pour une meilleure accessibilité aux nouveaux développeurs (et purge).

* framework full-stack django
* base de données PostgreSQL

# Installation

Pour lancer le site en local (commandes docker-compose standard, version 1.29.2) :
```
$ docker-compose up -d
```

Site accessible au port 8000 : (configurable dans le fichier .env)
```
$ $BROWSER localhost:8000
```


Installation des pre-commit hooks :
```
$ pip install pre-commit
$ pre-commit install
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

Quand un reviewer a validé la pull request, faire un rebase de la nouvelle branche dans master :
```
$ git checkout feature
$ git rebase master
```

Faire un rebase de master dans la feature :
```
$ git checkout master
$ git rebase feature
```

Mettre les changements en ligne :
```
$ git checkout master
$ git push
```

# Commandes Django

Accès à la DB par docker exec :
```
$ docker exec -it $(docker ps -f 'name=db' --format '{{.ID}}') psql -U upont
```

Pour les commandes python, commencer par entrer dans le conteneur :
```
$ docker-compose exec back /bin/sh
```

Remplir la base de données avec des données de test :
```
$ python manage.py loaddata upont/fixtures/populate.json
```

Ajouter un administrateur :
```
$ python manage.py createsuperuser
```

Créer les migrations :
```
$ python manage.py makemigrations
```

Appliquer les migrations :
```
$ python manage.py migrate
```

# Mise en production

À l'intérieur du container back, nginx reçoit les requêtes et les transmet à gunicorn, qui se charge de faire le lien avec le serveur python.

Lancer le build :
```
$ bash scripts/build.sh
```

Lancer le serveur :
```
$ bash scripts/start.sh
```

Stopper le serveur :
```
$ bash scripts/stop.sh
```
