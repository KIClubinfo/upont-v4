# Upont 4.0

Refonte de uPont en python avec le framework django pour une meilleure accessibilité aux nouveaux développeurs.

* framework full-stack django
* base de données PostgreSQL

Site de développement : https://upont-dev.enpc.org

Ancien repository : https://github.com/KIClubinfo/upont/

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

# Variables d'environnement

Les variables d'environnement suivantes sont placées dans le fichier *.env* :

| Variable | Description | Dev | Prod |
| -------- | -------------|----- | ------|
| DB_HOST | Nom du host de la BDD | db | db |
| DB_PORT | Port de la BDD (interne au container) | 5432 | 5432 |
| DB_USER | Utilisateur de la BDD | upont | upont |
| DB_NAME | Nom de la BDD | upont | upont |
| DB_PASSWORD | Mot de passe de la BDD | upont | SECRET |
| BACK_PORT | Port d'accès au site (externe) | 8000 | **** |
| SENDGRID_API_KEY | Clé permettant d'envoyer des mails avec l'API sendgrid (à récupérer sur le site de Sendgrid) | key | SECRET |
| ADMIN_EMAIL | Adressse recevant les mails d'administration de Django pour alertir de certaines actions (création d'un compte...) | upont@enpc.org | Autre |
| DEFAULT_FROM_EMAIL | Adresse envoyant les mails (avec Sendigrd, n'importe quelle adresse en @enpc.org fonctionne) | upont@enpc.org | upont@enpc.org |
| SECRET_KEY | Clé secrète utilisée par Django | ChangeThatPlease | SECRET |
| DEBUG | Défini si le mode DEBUG est activé. | True | False |
| GUNICORN_NB_WORKERS | Nombre de workers pour le WSGI gunicorn |  | 10 |
| SECURE_SSL_REDIRECT | Redirige automatiquement les requêtes non HTTPS vers des requêtes HTTPS. Laisser à False si un autre proxy fait déjà cete redirection. | False | False |


Commande pour générer une clé secrète (vous devez avoir Django installé):

```
$ python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

# Workflow git

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

# Documentation

Fonctionnement du site :

* [Documentation du site](docs/workings.md)

Les indispensables :

* Gestionnaire de versions : [git](https://doc.ubuntu-fr.org/git)
* [HTML/CSS](http://openclassrooms.com/courses/apprenez-a-creer-votre-site-web-avec-html5-et-css3)
* Framework : [Django](https://docs.djangoproject.com/en/3.2/)
* Utilisation de conteneurs : [Docker](https://docs.docker.com/)
* Pour gérer facilement différents conteneurs : [docker-compose](https://docs.docker.com/compose/)

Autres technologies utilisées :

* Pour uniformiser la syntaxe sur le projet : [pre-commit](https://pre-commit.com/index.html)
* Gestionnaire de dépendances python : [Poetry](https://python-poetry.org/docs/)
* Application WSGI pour la mise en production : [Gunicorn](https://docs.gunicorn.org/en/stable/)
* Serveur web et reverse-proxy : [Nginx](https://docs.nginx.com/)
* Base de données : [PostgreSQL](https://www.postgresql.org/docs/)
* Intégration continue : [Github Actions](https://docs.github.com/en/actions)