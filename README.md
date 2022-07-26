# Upont 4.0

Refonte de uPont en python avec le framework django pour une meilleure accessibilité aux nouveaux développeurs.

* framework back-end django
* framework front-end mixte Jinja2 et ReactJS
* base de données PostgreSQL

[Site de développement](https://upont-dev.enpc.org)

[Ancien repository](https://github.com/KIClubinfo/upont/)

# Installation

Pour construire les images des conteneurs :
```
docker-compose build
```

Pour lancer le site en local (commandes docker-compose standard, version 1.29.2) :
```
docker-compose up -d
```

Site accessible au port 8000 : (configurable dans le fichier .env)
```
$BROWSER localhost:8000
```


Installation des pre-commit hooks :
```
pip install pre-commit
pre-commit install
```

# Commandes Django

Accès à la DB par docker exec :
```
docker exec -it $(docker ps -f 'name=db' --format '{{.ID}}') psql -U upont
```

Pour les commandes python, commencer par entrer dans le conteneur :
```
docker-compose exec back /bin/sh
```

Remplir la base de données avec des données de test :
```
python manage.py loaddata upont/fixtures/populate.json
```

Ajouter un administrateur :
```
python manage.py createsuperuser
```

Créer les migrations :
```
python manage.py makemigrations
```

Appliquer les migrations :
```
python manage.py migrate
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

# Sauvegarde

## Base de données
### Réaliser une sauvegarde de la base de données

`$ bash scripts/backup_database.sh`

La sauvegarde se trouve dans le dossier `backups/database` sous le nom `AnnéeMoisJourHeureMinute.dump`.

**Attention** bien vérifier que les valeurs de `DB_USER` et `DB_NAME` dans le script sont les bonnes !

### Restorer une sauvegarde de la base de données
Exécuter dans le container de la base de données :

`$ pg_restore -d $DB_NAME --clean --create save.dump`

**Attention** cette commande supprime le contenu actuel de la base de données pour le remplacer par celui de la
sauvegarde

# Variables d'environnement

Les variables d'environnement suivantes sont placées dans le fichier *.env* :

| Variable              | Description                                                                                                                            | Dev              | Prod                                      |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------|------------------|-------------------------------------------|
| DB_HOST               | Nom du host de la BDD.                                                                                                                 | db               | db                                        |
| DB_PORT               | Port de la BDD (interne au container).                                                                                                 | 5432             | 5432                                      |
| DB_USER               | Utilisateur de la BDD.                                                                                                                 | upont            | upont                                     |
| DB_NAME               | Nom de la BDD.                                                                                                                         | upont            | upont                                     |
| DB_PASSWORD           | Mot de passe de la BDD.                                                                                                                | upont            | SECRET                                    |
| BACK_PORT             | Port d'accès au site (externe).                                                                                                        | 8000             | ****                                      |
| SENDGRID_API_KEY      | Clé permettant d'envoyer des mails avec l'API sendgrid (à récupérer sur le site de Sendgrid).                                          | key              | SECRET                                    |
| ADMIN_EMAIL           | Adressse recevant les mails d'administration de Django pour alertir de certaines actions (création d'un compte...).                    | upont@enpc.org   | Autre                                     |
| DEFAULT_FROM_EMAIL    | Adresse envoyant les mails (avec Sendigrd, n'importe quelle adresse en @enpc.org fonctionne).                                          | upont@enpc.org   | upont@enpc.org                            |
| SECRET_KEY            | Clé secrète utilisée par Django.                                                                                                       | ChangeThatPlease | SECRET                                    |
| DEBUG                 | Défini si le mode DEBUG est activé.                                                                                                    | True             | False                                     |
| DOMAIN_NAME           | Nom de domaine utilisé en production. Toutes les requêtes ne provenant pas de ce domaine seront rejetées.                              | upont.enpc.org   | upont.enpc.org                            |
| GUNICORN_NB_WORKERS   | Nombre de workers pour le WSGI gunicorn.                                                                                               |                  | 10                                        |
| SECURE_SSL_REDIRECT   | Redirige automatiquement les requêtes non HTTPS vers des requêtes HTTPS. Laisser à False si un autre proxy fait déjà cete redirection. | False            | False                                     |
| REMOTE_STATIC_STORAGE | Variable indiquant si le site utilise un serveur distant pour servir les fichiers statiques.                                           | False            | True                                      |
| FTP_STORAGE_LOCATION  | URL de connexion FTP au serveur de stockage distant pour y placer les fichiers statiques.                                              |                  | ftp://\<user>:\<password>@\<host>:\<port> |
| REMOTE_STATIC_URL     | URL pour l'accès aux fichiers statiques distants (peut être différent de FTP_STORAGE_LOCATION).                                        |                  | https://upont.cdn.enpc.org                |


Commande pour générer une clé secrète (vous devez avoir Django installé):

```
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

# Workflow git

Toujours travailler sur une nouvelle branche :
```
git checkout dev
git branch feature
git checkout feature
```

Ajouter vos changements :
```
git add ...
git commit -m "Nom de commit explicite"
```

Mettre la branche en ligne et créer une pull request :
```
git push --set-upstream origin feature
```

### Méthode 1 :

Quand un reviewer a validé la pull request et que les checks sont réussis, faire un rebase de la nouvelle branche dans dev :
```
git checkout feature
git rebase dev
```

Faire un rebase de dev dans la feature (on pourra faire un rebase interactif pour squash plusieurs commits):
```
git checkout dev
git rebase feature
```

Mettre les changements en ligne :
```
git checkout dev
git push --force-with-lease
```

### Méthode 2 :

Sur la page de la pull request, utiliser github pour résoudre les conflits en ligne et pour "squash & merge".

# Documentation

Documentation du site :

* [Table des matières](docs/table_of_contents.md)

Les indispensables :

* Gestionnaire de versions : [git](https://doc.ubuntu-fr.org/git)
* [HTML/CSS](http://openclassrooms.com/courses/apprenez-a-creer-votre-site-web-avec-html5-et-css3)
* Framework : [Django](https://docs.djangoproject.com/en/3.2/)
* Front : [ReactJS](https://reactjs.org/docs/getting-started.html)
* Utilisation de conteneurs : [Docker](https://docs.docker.com/)
* Pour gérer facilement différents conteneurs : [docker-compose](https://docs.docker.com/compose/)

Autres technologies utilisées :

* Pour uniformiser la syntaxe sur le projet : [pre-commit](https://pre-commit.com/index.html)
* Gestionnaire de dépendances python : [Poetry](https://python-poetry.org/docs/)
* Gestionnaire de dépendances javascript : [npm](https://docs.npmjs.com/)
* Application WSGI pour la mise en production : [Gunicorn](https://docs.gunicorn.org/en/stable/)
* Serveur web et reverse-proxy : [Nginx](https://docs.nginx.com/)
* Base de données : [PostgreSQL](https://www.postgresql.org/docs/)
* Intégration continue : [Github Actions](https://docs.github.com/en/actions)
* Bundler javascript : [webpack](https://webpack.js.org/concepts/)
