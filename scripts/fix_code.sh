#!/bin/bash
set -e

# Définir le répertoire du projet
PROJECT_DIR="$(dirname "$0")/../back"
echo "==> Vérification et correction automatique du code Python dans $PROJECT_DIR"

# Se placer dans le dossier back
cd "$PROJECT_DIR"

# Vérifier et corriger le code automatiquement avec autopep8
echo "-> Formatage autopep8..."
poetry run autopep8 --in-place --aggressive --aggressive $(find . -name "*.py")

# Organiser les imports avec isort
echo "-> Organisation des imports avec isort..."
poetry run isort .

# Formatter le code avec black
echo "-> Formatage avec black..."
poetry run black .

# Supprimer les imports et variables inutilisées avec autoflake
echo "-> Suppression des imports et variables inutilisées (F401/F841)..."
poetry run autoflake --remove-all-unused-imports --remove-unused-variables --in-place -r .

echo "==> Correction terminée !"