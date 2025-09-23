#!/bin/bash

# Chemin vers le dossier back/
BACK_DIR="../back"

# Corrige le code selon PEP8 avec autopep8
poetry run autopep8 --in-place --aggressive --aggressive $(find $BACK_DIR -name "*.py")

# Trie et nettoie les imports avec isort
poetry run isort $(find $BACK_DIR -name "*.py")