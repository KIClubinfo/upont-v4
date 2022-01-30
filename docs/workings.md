# Structure générale

Le site se divise en plusieurs applications django : uPont (principale), Social, News, Trade [in-progress] et Pochtron [in-progress].

## Fonctionalités

* Connexion par SSO ou avec mot de passe
* Bouton Feedback
* Système d'administration
* Application Social avec élèves et clubs
* Application News avec posts, évènements et shotguns

## Social

L’application sociale correspond au cœur de tout ce qui touche aux élèves. Elle comporte notamment les
pages de profils, où les utilisateurs peuvent modifier certaines informations présentes sur leurs profils, ainsi que
voir les profils des autres utilisateurs. Elle leur permet également d’accéder à la liste des clubs, et de voir les
différentes responsabilités de chacun des membres. Si l’utilisateur a été ajouté en tant que membre d’un club,
il est également possible de lui donner l’autorisation d’éditer son club. Enfin, une barre de recherche permet de
rechercher les élèves à partir de leur prénom, de leur nom, de leur département et de leur promotion. Une recherche
par trigramme permet également de trouver un élève même si son nom est écorché. Une fonctionnalité similaire
permet de rechercher des clubs sur la base de leur nom, de leur surnom et de leur catégorie.

## News

L’application News regroupe l’ensemble des actualités de la vie associative des ponts. Elle est inspirée du
fonctionnent des groupes Facebook, mais l’idée était d’adapter ce fonctionnement pour qu’il soit le plus pratique
et adapté à l’usage possible. Nous avons donc utilisé l’architecture suivante : un club peut créer un event, lié à une
date, qui correspond à un évènement organisé par le club. L’event est le bloc central de l’application. L’utilisateur
peut accéder à une page recensant l’ensemble des events à venir, par ordre chronologique. L’idée étant d’avoir un
endroit où l’utilisateur peut retrouver toute la programmation associative, une feature qui manque sur les groupes
Facebook. Les clubs et les élèves peuvent également créer des posts. Un post est exactement l’équivalent d’un
post sur Facebook : il contient du texte et des images, et l’idée est de pouvoir informer les autres utilisateurs de
la même façon que dans un groupe Facebook. Le système de likes et de commentaires est également implémenté
dans Upont (cf. plus bas). La valeur ajoutée par rapport à un groupe Facebook est la possibilité pour un post de
renvoyer vers un event préalablement créé par le club. Ainsi, un club peut créer un évènement, puis un post initial
pour l’annoncer, et ensuite faire des rappels ou des précisions avec des posts régulièrement espacés dans le temps.
De plus, dans la vue propre à un event, l’ensemble des posts qui concernent cet event sont regroupés, il est donc
facile de voir les dernières informations concernant l’évènement. Enfin, l’application permet aux élèves de modifier
leurs posts, ainsi que d’éditer les posts et les évenements créés par les clubs dont ils sont membres.
Le système de commentaire permet simplement aux élèves de laisser des messages sous les posts du fil d’actualités, visibles par tous les autres élèves. Un utilisateur peut décider de commenter en tant qu’élève ou en tant qu’un
des clubs dont il membre : l’avatar identifiant l’auteur du commentaire est alors choisi en conséquence (image de
profil de l’étudiant ou du club). Un utilisateur a également la possibilité de supprimer les commentaires publiés
par lui-même ou par l’un des clubs dont il est membre. Enfin, un élève peut également "liker" un post. Chaque
post comporte alors des compteurs pour le nombre de likes et de commentaires.
Finalement, la feature qui manquait le plus aux associations est la possibilité d’organiser des shotguns. Nous avons pour cela
réalisé deux types de shotguns différents : avec ou sans motivation. Dans le cas d’un shotgun sans motivation, le
premier arrivé est le premier servi, donc l’utilisateur sait directement s’il a réussi le shotgun ou non. Dans le cas
d’un shotgun avec motivation, l’utilisateur rentre une motivation au moment de participer, et l’administrateur
du shotgun peut ensuite refuser des participations si leur motivation n’est pas suffisante. Quand l’administrateur
a fini de trier les participations, il publie les résultats et les participants savent alors s’ils ont réussi le shotgun
ou non. Plusieurs pages ont été créées à ces fin : une page regroupant tous les shotguns, en particulier ceux qui
commencent dans un futur proche ; une page propre à chaque shotgun sur laquelle on participe et on consulte ses
résultats ; et des pages d’administration pour créer, modifier, supprimer et administrer les shotguns.

# Fonctionnement du site en production

## Conteneur Back

Nous utilisons Gunicorn comme serveur
WSGI (pour Web Server Gateway Interface). Il s’agit d’un serveur web python qui reçoit certaines requêtes
transmises par Nginx, et communique avec l’application Django (à l’aide d’une application WSGI créée par
Django). Django traite la requête et renvoie une réponse. Gunicorn créé un nombre configurable de workers,
qui sont des processus distincts sans partage de mémoire, chacun capable de traiter des requêtes HTTP. Chaque
worker correspond donc à une parallélisation des tâches. De plus chaque worker crée un certain nombre de threads,
ce qui est donc un second moyen de concurrence.

## Conteneur Nginx

Le fonctionnement de Nginx est essentiel pour le déploiement correct du site. Un des points primordiaux
pour le fonctionnement du site est de servir les fichiers statiques. Il s’agit des fichiers qui ne changent pas d’une
requête à l’autre (au contraire d’une page HTML), généralement des images, du javascript ou du style css. Nous
utilisons nginx en tant que serveur web pour envoyer ces fichiers très rapidement sans passer par le serveur Django.
Pour servir les fichiers statiques qui doivent être réservés aux utilisateurs authentifiés, nous avons créé dans django un contrôleur qui vérifie que l’utilisateur est bien authentifié, avant
de faire une redirection interne vers l’url /protected/. Nginx est configuré de telle sorte que ce schéma d’URL n’est
accessible que depuis une redirection interne, ce qui achève de réserver l’accès aux fichiers media aux utilisateurs
authentifiés. Pour les requêtes autres
que celles de fichiers statiques, Nginx fonctionne comme un reverse proxy et le serveur web qui traite la requête
est Gunicorn.


## Schéma de fonctionnement

![Diagramme UML](/docs/schema1.jpg)
