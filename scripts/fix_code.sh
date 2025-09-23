#!/bin/bash
set -e

# Dossier du projet backend
BACK_DIR="../back"

echo "==> Vérification et correction automatique du code Python dans $BACK_DIR"

# Aller dans le dossier back pour que toutes les commandes s'exécutent correctement
cd "$BACK_DIR"

# 1. Formatage autopep8
echo "-> Formatage autopep8..."
poetry run autopep8 --in-place --aggressive --aggressive $(find . -name "*.py")

# 2. Organisation des imports avec isort
echo "-> Organisation des imports avec isort..."
poetry run isort .

# 3. Formatage complet avec black
echo "-> Formatage avec black..."
poetry run black .

# 4. Supprimer imports et variables inutilisées
echo "-> Suppression des imports et variables inutilisées..."
poetry run autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r .

# 5. Vérification des imports et variables inutilisées avec flake8
echo "-> Vérification des imports et variables inutilisées (F401/F841)..."
poetry run flake8 . --select=F401,F841

echo "==> Correction terminée !"