# Dossier nginx

## Présentation

Dossier associé au service nginx (utilisé uniquement en production).

## nginx.conf

Ce fichier contient la configuration de nginx.

**/static/** : redirige vers les fichiers statiques (CSS, images, JS...).

**/protected/** : permet d'accéder aux fichiers *media*, comme les images uploadées par les utilisateurs, qu'on veut donc protéger par authentification. C'est pour cela que ce pattern est *internal* : on ne peut y accéder que par redirection interne de django, après authentification.

**/** : toutes les autres URL sont redirigées vers le service **back**.

## Dockerfile

Utilisé pour la construction du service *nginx*. Il se contente d'installer *nginx* et de copier le fichier de configuration *nginx.conf* au bon endroit dans le container.