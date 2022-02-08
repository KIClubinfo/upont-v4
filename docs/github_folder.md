# Dossier *.github*

Dans ce dossier on place les fichiers relatifs à **github**.

## Dossier *workflows*

Contient les **workflows** qui seront exécutés par Github Actions. Chaque workflow se présente sous la forme d'un fichier *yml* dans lequel on configure les actions à effectuer. Par exemple :
* *main.yml* : lance les tests d'intégration
* *super-linter.yml* : teste la syntaxe et la forme des lignes ajoutées (avec différents *linters*)

## Dossier *linters*

Contient les fichiers de configurations de certains *linters* utilisés par le **workflow** *super-linter.yml*.
