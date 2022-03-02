# Placer les fichiers statiques sur un serveur distant

Pour des raisons de performance, on peut souhaiter servir les fichiers statiques depuis un autre serveur que celui qui héberge le site. Dans ce cas il faut faire attention à deux choses :
* Placer les fichiers statiques sur le serveur distant.
* Indiquer aux pages du site de récupérer les fichiers statiques depuis le serveur distant.

Le package *django-storages* est utilisé pour faire cela.

**Notons que dans notre cas les fichiers *media* sont encore servis depuis le serveur local.**

Dans notre cas on placera généralement les fichiers sur un hébergement OVH. Celui-ci devra être accessible par FTP et on placera les identifiants adaptés dans la variable d'environnement **FTP_STORAGE_LOCATION**. Ces fichiers seront copiés au moment de lancer le container *back*.
Pour éviter des erreurs de CORS, on pourra placer la configuration suivante sur le serveur distant (exemple avec un serveur web Apache, placer la configuration dans le fichier *.htaccess*) :

```
AddType application/vnd.ms-fontobject    .eot
AddType application/x-font-opentype      .otf
AddType image/svg+xml                    .svg
AddType application/x-font-ttf           .ttf
AddType application/font-woff            .woff
AddType application/font-woff2           .woff2

<IfModule mod_headers.c>
  <FilesMatch ".(eot|otf|svg|ttf|woff2?)$">
    Header set Access-Control-Allow-Origin "*"
  </FilesMatch>
</IfModule>
```
